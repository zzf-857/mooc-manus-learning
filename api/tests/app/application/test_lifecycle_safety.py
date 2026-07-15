import io
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.application.errors.exceptions import ServerRequestsError
from app.application.services.session_service import SessionService
from app.domain.models.file import File
from app.domain.models.session import Session
from app.domain.services.agent_task_runner import AgentTaskRunner
from app.infrastructure.external.file_storage.local_file_storage import LocalFileStorage
from app.infrastructure.external.message_queue.redis_stream_message_queue import RedisStreamMessageQueue
from app.infrastructure.external.sandbox.docker_sandbox import DockerSandbox
from app.infrastructure.external.task.redis_stream_task import RedisStreamTask
from app.infrastructure.repositories.db_uow import DBUnitOfWork


class FakeRedisClient:
    def __init__(self) -> None:
        self.xadd_calls = []
        self.expire_calls = []
        self.delete_calls = []
        self.raise_on_range = False

    async def xadd(self, name, fields, **kwargs):
        self.xadd_calls.append((name, fields, kwargs))
        return "1-0"

    async def expire(self, name, ttl):
        self.expire_calls.append((name, ttl))
        return True

    async def delete(self, name):
        self.delete_calls.append(name)
        return 1

    def pipeline(self, transaction=True):
        assert transaction is True
        return FakeRedisPipeline(self)

    async def set(self, *args, **kwargs):
        return True

    async def xrange(self, *args, **kwargs):
        if self.raise_on_range:
            raise RuntimeError("broken stream payload")
        return []

    def register_script(self, script):
        async def execute(*, keys, args):
            return 1

        return execute


class FakeRedisPipeline:
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    def xadd(self, name, fields, **kwargs):
        self.client.xadd_calls.append((name, fields, kwargs))
        return self

    def expire(self, name, ttl):
        self.client.expire_calls.append((name, ttl))
        return self

    async def execute(self):
        return ["1-0", True]


@pytest.mark.anyio
async def test_redis_stream_put_enforces_length_and_refreshes_ttl(monkeypatch):
    import app.infrastructure.external.message_queue.redis_stream_message_queue as queue_module

    client = FakeRedisClient()
    monkeypatch.setattr(queue_module, "get_redis", lambda: SimpleNamespace(client=client))
    queue = RedisStreamMessageQueue("task:output:test", max_length=25, ttl_seconds=60)

    message_id = await queue.put("event")
    await queue.delete()

    assert message_id == "1-0"
    assert client.xadd_calls == [
        ("task:output:test", {"data": "event"}, {"maxlen": 25, "approximate": False})
    ]
    assert client.expire_calls == [("task:output:test", 60)]
    assert client.delete_calls == ["task:output:test"]


@pytest.mark.anyio
async def test_redis_stream_pop_error_keeps_tuple_contract(monkeypatch):
    import app.infrastructure.external.message_queue.redis_stream_message_queue as queue_module

    client = FakeRedisClient()
    client.raise_on_range = True
    monkeypatch.setattr(queue_module, "get_redis", lambda: SimpleNamespace(client=client))
    queue = RedisStreamMessageQueue("task:input:test")

    assert await queue.pop() == (None, None)


class FakeQueue:
    instances = []

    def __init__(self, stream_name, max_length=None, ttl_seconds=None):
        self.stream_name = stream_name
        self.max_length = max_length
        self.ttl_seconds = ttl_seconds
        self.deleted = False
        self.__class__.instances.append(self)

    async def delete(self):
        self.deleted = True


class FakeTaskRunner:
    def __init__(self):
        self.destroyed = False

    async def invoke(self, task):
        return None

    async def destroy(self):
        self.destroyed = True

    async def on_done(self, task):
        return None


@pytest.mark.anyio
async def test_destroy_uses_registry_snapshot_and_disposes_every_task(monkeypatch):
    import app.infrastructure.external.task.redis_stream_task as task_module

    RedisStreamTask._task_registry.clear()
    FakeQueue.instances.clear()
    monkeypatch.setattr(task_module, "RedisStreamMessageQueue", FakeQueue)
    runners = [FakeTaskRunner(), FakeTaskRunner()]
    RedisStreamTask(runners[0])
    RedisStreamTask(runners[1])

    await RedisStreamTask.destroy()

    assert RedisStreamTask._task_registry == {}
    assert all(runner.destroyed for runner in runners)
    assert all(queue.deleted for queue in FakeQueue.instances)
    assert {queue.max_length for queue in FakeQueue.instances} == {
        RedisStreamTask.INPUT_STREAM_MAX_LENGTH,
        RedisStreamTask.OUTPUT_STREAM_MAX_LENGTH,
    }
    assert {queue.ttl_seconds for queue in FakeQueue.instances} == {
        RedisStreamTask.STREAM_TTL_SECONDS
    }


class FakeSessionRepository:
    def __init__(self, sessions):
        self.sessions = {session.id: session for session in sessions}
        self.deleted = []

    async def get_by_id(self, session_id):
        return self.sessions.get(session_id)

    async def get_all(self):
        return list(self.sessions.values())

    async def delete_by_id(self, session_id):
        self.deleted.append(session_id)
        self.sessions.pop(session_id, None)


class FakeUow:
    def __init__(self, session_repository, file_repository=None):
        self.session = session_repository
        self.file = file_repository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class DisposableTask:
    def __init__(self):
        self.disposed = False

    async def dispose(self):
        self.disposed = True


class FakeTaskType:
    tasks = {}

    @classmethod
    def get(cls, task_id):
        return cls.tasks.get(task_id)


class FakeSandbox:
    def __init__(self, destroy_result=True):
        self.destroy_result = destroy_result
        self.destroyed = False

    async def destroy(self):
        self.destroyed = True
        return self.destroy_result


class FakeSandboxType:
    sandboxes = {}

    @classmethod
    async def get(cls, sandbox_id):
        return cls.sandboxes.get(sandbox_id)


class FakeFileStorage:
    def __init__(self, failing_file_id=None):
        self.deleted = []
        self.failing_file_id = failing_file_id

    async def delete_file(self, file_id):
        self.deleted.append(file_id)
        if file_id == self.failing_file_id:
            raise RuntimeError("storage unavailable")


@pytest.mark.anyio
async def test_delete_session_releases_task_sandbox_and_unshared_files():
    unique_file = File(id="unique", filename="unique.txt")
    shared_file = File(id="shared", filename="shared.txt")
    target = Session(
        id="target",
        task_id="task-1",
        sandbox_id="sandbox-1",
        files=[unique_file, shared_file],
    )
    other = Session(id="other", files=[shared_file])
    repository = FakeSessionRepository([target, other])
    task = DisposableTask()
    sandbox = FakeSandbox()
    storage = FakeFileStorage()
    FakeTaskType.tasks = {"task-1": task}
    FakeSandboxType.sandboxes = {"sandbox-1": sandbox}
    service = SessionService(
        uow_factory=lambda: FakeUow(repository),
        sandbox_cls=FakeSandboxType,
        task_cls=FakeTaskType,
        file_storage=storage,
    )

    await service.delete_session("target")

    assert task.disposed is True
    assert sandbox.destroyed is True
    assert storage.deleted == ["unique"]
    assert repository.deleted == ["target"]


@pytest.mark.anyio
async def test_delete_session_keeps_record_when_resource_cleanup_fails():
    file = File(id="failed-file", filename="failed.txt")
    target = Session(id="target", files=[file])
    repository = FakeSessionRepository([target])
    storage = FakeFileStorage(failing_file_id=file.id)
    FakeTaskType.tasks = {}
    FakeSandboxType.sandboxes = {}
    service = SessionService(
        uow_factory=lambda: FakeUow(repository),
        sandbox_cls=FakeSandboxType,
        task_cls=FakeTaskType,
        file_storage=storage,
    )

    with pytest.raises(ServerRequestsError):
        await service.delete_session("target")

    assert repository.deleted == []
    assert repository.sessions["target"] is target


@pytest.mark.anyio
async def test_static_sandbox_get_never_marks_shared_container_as_owned(monkeypatch):
    import app.infrastructure.external.sandbox.docker_sandbox as sandbox_module

    monkeypatch.setattr(
        sandbox_module,
        "get_settings",
        lambda: SimpleNamespace(sandbox_address="manus-sandbox"),
    )

    async def resolve(cls, hostname):
        return "172.23.0.4"

    monkeypatch.setattr(DockerSandbox, "_resolve_hostname_to_ip", classmethod(resolve))
    monkeypatch.setattr(
        sandbox_module.docker,
        "from_env",
        lambda: pytest.fail("静态沙箱不得访问Docker删除容器"),
    )

    sandbox = await DockerSandbox.get("manus-sandbox")

    assert sandbox is not None
    assert sandbox.id == "manus-sandbox"
    assert sandbox._container_name is None
    assert await sandbox.destroy() is True


class FakeDBSession:
    def __init__(self, commit_error=None, rollback_error=None, close_error=None):
        self.commit_error = commit_error
        self.rollback_error = rollback_error
        self.close_error = close_error
        self.committed = False
        self.rolled_back = False
        self.closed = False

    async def commit(self):
        self.committed = True
        if self.commit_error:
            raise self.commit_error

    async def rollback(self):
        self.rolled_back = True
        if self.rollback_error:
            raise self.rollback_error

    async def close(self):
        self.closed = True
        if self.close_error:
            raise self.close_error


@pytest.mark.anyio
async def test_uow_propagates_commit_failure_and_still_closes_session():
    error = RuntimeError("commit failed")
    db_session = FakeDBSession(commit_error=error)
    uow = DBUnitOfWork(lambda: db_session)

    with pytest.raises(RuntimeError, match="commit failed"):
        async with uow:
            pass

    assert db_session.committed is True
    assert db_session.closed is True


@pytest.mark.anyio
async def test_uow_propagates_rollback_failure_and_still_closes_session():
    rollback_error = RuntimeError("rollback failed")
    db_session = FakeDBSession(rollback_error=rollback_error)
    uow = DBUnitOfWork(lambda: db_session)

    with pytest.raises(RuntimeError, match="rollback failed"):
        async with uow:
            raise ValueError("business failed")

    assert db_session.rolled_back is True
    assert db_session.closed is True


class RunnerSessionRepository:
    def __init__(self, old_file):
        self.old_file = old_file
        self.removed = []
        self.added = []

    async def get_file_by_path(self, session_id, filepath):
        return self.old_file

    async def remove_file(self, session_id, file_id):
        self.removed.append((session_id, file_id))

    async def add_file(self, session_id, file):
        self.added.append((session_id, file))


class DownloadSandbox:
    async def download_file(self, filepath):
        return io.BytesIO(b"updated")


class UploadStorage:
    async def upload_file(self, upload_file):
        return File(id="new-id", filename=upload_file.filename)


@pytest.mark.anyio
async def test_sync_file_removes_previous_session_file_by_id():
    old_file = File(id="old-id", filename="report.txt", filepath="/work/report.txt")
    repository = RunnerSessionRepository(old_file)
    runner = object.__new__(AgentTaskRunner)
    runner._session_id = "session-1"
    runner._uow = FakeUow(repository)
    runner._sandbox = DownloadSandbox()
    runner._file_storage = UploadStorage()

    uploaded = await runner._sync_file_to_storage("/work/report.txt")

    assert repository.removed == [("session-1", "old-id")]
    assert repository.added == [("session-1", uploaded)]
    assert uploaded.filepath == "/work/report.txt"


class LocalFileRepository:
    def __init__(self, file):
        self.file = file

    async def get_by_id(self, file_id):
        if self.file and self.file.id == file_id:
            return self.file
        return None

    async def delete_by_id(self, file_id):
        if self.file and self.file.id == file_id:
            self.file = None


@pytest.mark.anyio
async def test_local_file_storage_delete_removes_object_and_metadata(tmp_path: Path):
    file = File(id="file-1", filename="note.txt", key="2026/07/file-1.txt")
    repository = LocalFileRepository(file)
    stored_path = tmp_path / file.key
    stored_path.parent.mkdir(parents=True)
    stored_path.write_text("content", encoding="utf-8")
    storage = LocalFileStorage(
        base_path=str(tmp_path),
        uow_factory=lambda: FakeUow(None, repository),
    )

    await storage.delete_file(file.id)
    await storage.delete_file(file.id)

    assert stored_path.exists() is False
    assert repository.file is None
