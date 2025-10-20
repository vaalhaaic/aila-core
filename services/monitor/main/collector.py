"""Lightweight metrics collector."""

from __future__ import annotations

import argparse
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict

import requests
import yaml


class MetricsConfig(yaml.YAMLObject):
    yaml_tag = "!MetricsConfig"


def load_config(path: Path) -> Dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def scrape(endpoints: Dict[str, str]) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=3)
            metrics[f"aila_service_up{{service=\"{name}\"}}"] = 1.0 if response.ok else 0.0
        except requests.RequestException:
            metrics[f"aila_service_up{{service=\"{name}\"}}"] = 0.0
    return metrics


def format_metrics(metrics: Dict[str, float]) -> str:
    lines = [f"{metric} {value}" for metric, value in metrics.items()]
    return "\n".join(lines) + "\n"


def serve(config_path: Path, once: bool = False) -> None:
    cfg = load_config(config_path)
    endpoints = cfg.get("endpoints", {})
    port = int(cfg.get("metrics_port", 9091))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # type: ignore[override]
            if self.path != "/metrics":
                self.send_response(404)
                self.end_headers()
                return
            metrics = scrape(endpoints)
            payload = format_metrics(metrics)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload.encode("utf-8"))

    if once:
        metrics = scrape(endpoints)
        print(format_metrics(metrics))
        return

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving metrics on :{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to monitor.yaml")
    parser.add_argument("--snapshot", action="store_true", help="Print metrics once and exit")
    args = parser.parse_args()

    serve(Path(args.config), once=args.snapshot)


if __name__ == "__main__":
    main()
