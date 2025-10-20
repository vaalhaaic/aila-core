# Monitor Service

Collects metrics and status information from the Aila stack and exports it via HTTP.

## Components

- `config/monitor.yaml` – scrape definitions and alert thresholds.
- `systemd/monitor.service` – systemd unit.
- `scripts/collect_metrics.sh` – manual trigger for telemetry snapshot.
- `main/collector.py` – Python service exposing Prometheus textfile output.

## Deployment

1. Adjust endpoints in `config/monitor.yaml`.
2. Enable the unit with `sudo systemctl enable --now aila-monitor.service`.
3. Configure Prometheus to scrape `http://<host>:9091/metrics`.
