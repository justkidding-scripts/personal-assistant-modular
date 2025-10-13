#!/usr/bin/env bash
set -euo pipefail

# Personal Assistant setup script
# - Creates venv and installs requirements
# - Checks for optional RAG source and Ollama

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. ./.venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "[OK] Dependencies installed"

# Check RAG source (optional)
DEFAULT_RAG="/media/nike/backup-hdd/Modular Deepdive/RAG"
if [ -d "$DEFAULT_RAG" ]; then
  echo "[INFO] Found RAG at: $DEFAULT_RAG (will be used automatically)"
else
  echo "[INFO] Optional RAG source not found at $DEFAULT_RAG"
  echo "      If your RAG lives elsewhere, export RAG_SRC_PATH to that directory before running."
fi

echo "[TIP] To run the Discord bot:"
echo "      export DISCORD_TOKEN=\"{{DISCORD_TOKEN}}\""
echo "      ./run_bot.sh"

echo "[TIP] To run API server: ./run_api.sh"

echo "[TIP] Optional local LLM (Ollama):"
echo "      export OLLAMA_BASE_URL=http://localhost:11434"
echo "      export OLLAMA_MODEL=llama3.2:3b"
