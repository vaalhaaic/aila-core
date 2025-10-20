#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <voice-id>" >&2
  exit 1
fi

VOICE=$1
VOICE_DIR="${VOICE_DIR:-/opt/aila/piper/voices}"
mkdir -p "${VOICE_DIR}"

BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/"
VOICE_FILE="${VOICE}-onxe.onnx"

curl -L "${BASE_URL}${VOICE_FILE}" -o "${VOICE_DIR}/${VOICE_FILE}"
