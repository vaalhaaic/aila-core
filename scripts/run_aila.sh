#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

if [[ "${1:-}" == "--setup" ]]; then
  python3 -m venv "${VENV_DIR}"
  source "${VENV_DIR}/bin/activate"
  pip install --upgrade pip
  pip install -r "${ROOT_DIR}/requirements.txt"
  echo "Virtual environment ready."
  exit 0
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Virtual environment missing. Run '$0 --setup' first." >&2
  exit 1
fi

source "${VENV_DIR}/bin/activate"
python -m aila.runtime.orchestrator "$@"
