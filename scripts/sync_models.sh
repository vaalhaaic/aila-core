#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <host> [--apply]" >&2
  exit 1
fi

HOST=$1
shift

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "${ROOT_DIR}/deploy/deploy.py" --host "${HOST}" --filter aila-core "$@"
