#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <size>" >&2
  exit 1
fi

SIZE=$1
MODELS_DIR="${MODELS_DIR:-/opt/aila/whisper/models}"
mkdir -p "${MODELS_DIR}"

case "${SIZE}" in
  tiny|base|small|medium|large)
    MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-${SIZE}.bin"
    ;;
  *)
    echo "Unsupported size: ${SIZE}" >&2
    exit 1
    ;;
esac

curl -L "${MODEL_URL}" -o "${MODELS_DIR}/ggml-${SIZE}.bin"
