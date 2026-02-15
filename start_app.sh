#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8501}"
HOST="${HOST:-127.0.0.1}"

if ! command -v streamlit >/dev/null 2>&1; then
  echo "streamlit not found. Installing requirements..."
  python -m pip install -r requirements.txt
fi

exec streamlit run app.py --server.address "$HOST" --server.port "$PORT"
