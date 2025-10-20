#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root or via sudo." >&2
  exit 1
fi

apt-get update
apt-get install -y \
  build-essential \
  python3.12 \
  python3.12-venv \
  python3-pip \
  git \
  curl \
  ffmpeg \
  jq \
  rsync \
  unzip

groupadd --system aila 2>/dev/null || true
useradd --system --no-create-home --gid aila --shell /usr/sbin/nologin aila 2>/dev/null || true

echo "Dependencies installed. Configure NVIDIA drivers separately if required."
