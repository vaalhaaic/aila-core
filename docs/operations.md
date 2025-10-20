# Operations Guide

## Prerequisites

- Ubuntu 24.04 with passwordless sudo for the deploy account
- SSH access (public key added to `/home/<user>/.ssh/authorized_keys`)
- GPU drivers and CUDA toolkit installed
- Python 3.12 with `venv` module
- `rsync`, `jq`, `ffmpeg`, and `systemd` available

## Installation Workflow

1. Run `scripts/install_dependencies.sh` to install APT packages and create the `aila` system group.
2. Execute `scripts/deploy_to_host.sh <hostname>` to push configuration and services.
3. Rebuild the Python environment using `scripts/run_aila.sh --setup`.
4. Enable services on the target:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now whisper.service coqui.service aila-monitor.service
   ```
5. Inspect logs with `journalctl -u <service> -f`.

## Maintenance Tasks

- **Update models**: add new files under `aila/models/` and rerun `scripts/sync_models.sh`.
- **Upgrade services**: edit code in `services/<name>/main/`, deploy, then restart the related unit.
- **Configuration drift**: run `deploy/deploy.py --diff <host>` to preview changes.
- **Backups**: collect `/opt/aila/` and `/var/log/aila/` with `rsync` or `restic`.

## Troubleshooting

- Service fails to start: check environment fragment in `system/etc/aila/env.d/`.
- Missing CUDA: verify `nvidia-smi` output and the `GPU` capability in service unit files.
- Audio glitches: ensure PulseAudio or PipeWire is configured and accessible to the service user.
- Slow Whisper recognition: adjust the `device` and `precision` fields in `services/whisper/config/config.yaml`.

## Production Hardening

- Run services under dedicated system users with `ProtectSystem=strict`.
- Mount `/opt/aila` on fast NVMe storage and isolate `/var/log/aila`.
- Configure a firewall (`ufw` or `nftables`) and open only service ports.
- Integrate Prometheus scrape configuration for `monitor` endpoints.
