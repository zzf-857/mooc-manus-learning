FROM ghcr.io/astral-sh/uv:0.11.1 AS uv

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN chmod +x run.sh

EXPOSE 8000
CMD ["./run.sh"]
