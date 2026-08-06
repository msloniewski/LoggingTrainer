#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"

if [[ "${1:-}" == "--generate-audio" ]]; then
    VENV_DIR="$PROJECT_DIR/.venv-kokoro"
    REQUIREMENTS="$PROJECT_DIR/requirements-audio.txt"
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    if [[ "${1:-}" == "--generate-audio" ]]; then
        TOOLS_VENV="$PROJECT_DIR/.venv-tools"
        if [[ ! -x "$TOOLS_VENV/bin/uv" ]]; then
            "${PYTHON:-python3}" -m venv "$TOOLS_VENV"
            "$TOOLS_VENV/bin/python" -m pip install "uv>=0.8,<1"
        fi
        "$TOOLS_VENV/bin/uv" venv --python 3.12 "$VENV_DIR"
    else
        "${PYTHON:-python3}" -m venv "$VENV_DIR"
    fi
fi

if [[ "${1:-}" == "--generate-audio" ]]; then
    "$PROJECT_DIR/.venv-tools/bin/uv" pip install --torch-backend cpu \
        --python "$VENV_DIR/bin/python" pip -r "$REQUIREMENTS"
else
    "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS"
fi
cd "$PROJECT_DIR"

if [[ "${1:-}" == "--generate-audio" ]]; then
    shift
    export PATH="$VENV_DIR/bin:$PATH"
    exec "$VENV_DIR/bin/python" -m scripts.generate_audio_assets "$@"
fi

exec "$VENV_DIR/bin/python" run_trainer.py "$@"
