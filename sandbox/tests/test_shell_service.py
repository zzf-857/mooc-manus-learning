import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

from app.services.shell import ShellService


class ControlledStream:
    """可由测试控制输出与 EOF 的异步字节流。"""

    def __init__(self) -> None:
        self._chunks: asyncio.Queue[bytes] = asyncio.Queue()
        self.cancelled = False

    def feed(self, chunk: bytes) -> None:
        self._chunks.put_nowait(chunk)

    def feed_eof(self) -> None:
        self.feed(b"")

    async def read(self, _: int) -> bytes:
        try:
            return await self._chunks.get()
        except asyncio.CancelledError:
            self.cancelled = True
            raise


def make_process(
        stream: ControlledStream,
        *,
        returncode: int | None = None,
) -> Mock:
    """创建满足 Shell Pydantic 模型类型检查的可控进程替身。"""
    process = Mock(spec=asyncio.subprocess.Process)
    process.stdout = stream
    process.stdin = Mock()
    process.stdin.write = Mock()
    process.stdin.drain = AsyncMock()
    process.returncode = returncode

    completed = asyncio.Event()
    if returncode is not None:
        completed.set()

    async def wait() -> int:
        await completed.wait()
        return process.returncode

    def terminate() -> None:
        process.returncode = -15
        completed.set()

    def kill() -> None:
        process.returncode = -9
        completed.set()

    process.wait = AsyncMock(side_effect=wait)
    process.terminate = Mock(side_effect=terminate)
    process.kill = Mock(side_effect=kill)
    return process


def test_quick_command_collects_bounded_output_and_cleans_reader() -> None:
    async def scenario() -> None:
        service = ShellService()
        service.MAX_OUTPUT_CHARS = 8

        stream = ControlledStream()
        stream.feed(b"abcdefghij")
        stream.feed_eof()
        process = make_process(stream, returncode=0)

        with patch.object(
                service,
                "_create_process",
                new=AsyncMock(return_value=process),
        ):
            result = await service.exec_command("quick", os.getcwd(), "echo test")

        assert result.status == "completed"
        assert result.returncode == 0
        assert result.output == "cdefghij"
        assert service.active_shells["quick"].output == "cdefghij"
        assert service.active_shells["quick"].console_records[-1].output == "cdefghij"
        assert "quick" not in service._reader_tasks

    asyncio.run(scenario())


def test_long_running_command_returns_running_and_kill_cleans_reader() -> None:
    async def scenario() -> None:
        service = ShellService()
        service.COMMAND_WAIT_TIMEOUT_SECONDS = 0.01
        service.READER_DRAIN_TIMEOUT_SECONDS = 0.01

        stream = ControlledStream()
        stream.feed(b"started\n")
        process = make_process(stream)

        with patch.object(
                service,
                "_create_process",
                new=AsyncMock(return_value=process),
        ):
            result = await asyncio.wait_for(
                service.exec_command("long", os.getcwd(), "long command"),
                timeout=0.25,
            )

        assert result.status == "running"
        assert service.active_shells["long"].output == "started\n"
        assert "long" in service._reader_tasks

        kill_result = await service.kill_process("long")

        assert kill_result.status == "terminated"
        assert kill_result.returncode == -15
        assert process.terminate.called
        assert stream.cancelled
        assert "long" not in service._reader_tasks

    asyncio.run(scenario())


def test_replacing_process_cleans_old_reader_before_starting_new_one() -> None:
    async def scenario() -> None:
        service = ShellService()
        service.COMMAND_WAIT_TIMEOUT_SECONDS = 0.01
        service.READER_DRAIN_TIMEOUT_SECONDS = 0.01

        old_stream = ControlledStream()
        old_stream.feed(b"old output")
        old_process = make_process(old_stream)

        new_stream = ControlledStream()
        new_stream.feed(b"new output")
        new_stream.feed_eof()
        new_process = make_process(new_stream, returncode=0)

        create_process = AsyncMock(side_effect=[old_process, new_process])
        with patch.object(service, "_create_process", new=create_process):
            first_result = await asyncio.wait_for(
                service.exec_command("replace", os.getcwd(), "first"),
                timeout=0.25,
            )
            second_result = await asyncio.wait_for(
                service.exec_command("replace", os.getcwd(), "second"),
                timeout=0.25,
            )

        assert first_result.status == "running"
        assert second_result.status == "completed"
        assert second_result.output == "new output"
        assert old_process.terminate.called
        assert old_stream.cancelled
        assert "replace" not in service._reader_tasks

    asyncio.run(scenario())
