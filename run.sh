#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

echo "Starting Role-Level AI Intelligence at http://localhost:8000"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
