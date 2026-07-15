#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[[ -f .env ]] || cp .env.example .env
[[ -f api/config.yaml ]] || cp api/config.example.yaml api/config.yaml
docker compose config --quiet
docker compose up -d --build
docker compose ps
echo 'MoocManus: http://127.0.0.1:8088'
