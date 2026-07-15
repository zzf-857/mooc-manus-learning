#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v docker >/dev/null || { echo 'Docker is required.' >&2; exit 1; }
command -v uv >/dev/null || { echo 'uv is required: https://docs.astral.sh/uv/' >&2; exit 1; }
command -v npm >/dev/null || { echo 'Node.js/npm is required.' >&2; exit 1; }

[[ -f .env ]] || cp .env.example .env
[[ -f api/config.yaml ]] || cp api/config.example.yaml api/config.yaml

docker compose config --quiet
uv sync --project api --frozen
npm ci --prefix ui
echo 'Setup complete. Run ./scripts/start.sh.'
