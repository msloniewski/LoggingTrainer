#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    "${PYTHON:-python3}" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install -r "$PROJECT_DIR/requirements.txt"
cd "$PROJECT_DIR"
exec "$VENV_DIR/bin/python" run_trainer.py "$@"
