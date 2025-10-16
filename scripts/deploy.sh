#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
NIXOS_CONFIG_DIR="/etc/nixos"

# Validate expected layout.
if [[ ! -d "${REPO_ROOT}/host" || ! -f "${REPO_ROOT}/host/configuration.nix" ]]; then
  echo "ERROR: host configuration missing." >&2
  exit 1
fi
if [[ "$EUID" -ne 0 ]]; then
  echo "ERROR: run this script with sudo or as root." >&2
  exit 1
fi

echo "Synchronising host configuration to ${NIXOS_CONFIG_DIR}..."
rsync -av --delete "${REPO_ROOT}/host/" "${NIXOS_CONFIG_DIR}/"
rsync -av "${REPO_ROOT}/container/" "${NIXOS_CONFIG_DIR}/container/"

echo "Rebuilding system..."
nixos-rebuild switch --flake "${NIXOS_CONFIG_DIR}#"

echo "Deployment successful."
