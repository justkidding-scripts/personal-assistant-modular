#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
. ./.venv/bin/activate

if [ -z "${DISCORD_TOKEN:-}" ]; then
  echo "[ERR] DISCORD_TOKEN not set" >&2
  exit 1
fi

exec python discord_bot.py
