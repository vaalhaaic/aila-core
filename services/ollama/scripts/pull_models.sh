#!/usr/bin/env bash
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama binary not found in PATH." >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <model> [tag]" >&2
  exit 1
fi

MODEL=$1
TAG=${2:-latest}

ollama pull "${MODEL}:${TAG}"
