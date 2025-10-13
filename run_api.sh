#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
. ./.venv/bin/activate
exec uvicorn server:app --host 0.0.0.0 --port 8000 --reload
