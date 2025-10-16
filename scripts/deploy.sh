#!/usr/bin/env bash
set -euo pipefail

# Define repository root and system config destination
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
NIXOS_CONFIG_DIR="/etc/nixos"

# --- TASK 1: VALIDATE ---
if [[ ! -d "${REPO_ROOT}/host" || ! -f "${REPO_ROOT}/host/configuration.nix" ]]; then
    echo "ERROR: Invalid repository structure. 'host/configuration.nix' not found." >&2
    exit 1
fi
if [[ "$EUID" -ne 0 ]]; then
    echo "ERROR: This script must be run with sudo or as root." >&2
    exit 1
fi

# --- TASK 2: SYNCHRONIZE FILES ---
echo "Syncing repository config to ${NIXOS_CONFIG_DIR}..."
# Use rsync to copy the host configuration.
# The `container` and `app` dirs are referenced via relative paths in Nix files, so they don't need to be copied to /etc.
# The deploy script itself must reside with the repo.
rsync -av --delete "${REPO_ROOT}/host/" "${NIXOS_CONFIG_DIR}/"
rsync -av "${REPO_ROOT}/container/" "${NIXOS_CONFIG_DIR}/container/"

# --- TASK 3: REBUILD SYSTEM ---
echo "Executing nixos-rebuild switch..."
nixos-rebuild switch --flake "${NIXOS_CONFIG_DIR}#"

# --- TASK 4: REPORT SUCCESS ---
echo "Deployment successful. Aila system is active."
exit 0
