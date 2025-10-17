{ config, pkgs, lib, ... }:

let
  # Location on the host where the Piper voice model should be stored.
  # Copy `zh_CN-huayan-medium.onnx` into this directory before enabling the service.
  piperVoicePath = "/var/lib/aila/piper/zh_CN-huayan-medium.onnx";
  piperConfigPath = "/var/lib/aila/piper/zh_CN-huayan-medium.onnx.json";

  piperServer = pkgs.writeScript "aila-piper-placeholder.py" ''
    #!${pkgs.python312}/bin/python3
    import argparse
    import json
    import logging
    import signal
    import sys
    import time
    from http import HTTPStatus
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from pathlib import Path

    STATE = {"requests": 0}
    STOP_REQUESTED = False


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Placeholder Piper HTTP endpoint for development use."
        )
        parser.add_argument("--model", required=True, help="Path to ONNX voice model")
        parser.add_argument("--config", required=True, help="Path to Piper JSON config")
        parser.add_argument("--host", default="0.0.0.0", help="Bind address")
        parser.add_argument("--port", type=int, default=5002, help="Listen port")
        return parser.parse_args()


    class PlaceholderHandler(BaseHTTPRequestHandler):
        server_version = "AilaPiper/0.1"
        sys_version = ""

        def _write_json(self, status: HTTPStatus, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._write_json(
                    HTTPStatus.OK,
                    {
                        "status": "ok",
                        "requests": STATE["requests"],
                        "note": "placeholder implementation – no audio emitted",
                    },
                )
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown path")

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/speak":
                self.send_error(HTTPStatus.NOT_FOUND, "Unknown path")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid length"})
                return
            raw = self.rfile.read(max(length, 0))
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            text = str(payload.get("text", "")).strip()
            voice = str(payload.get("voice", "")).strip() or "default"
            if not text:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "text is required"})
                return

            STATE["requests"] += 1
            logging.info("Piper placeholder received voice=%s length=%d", voice, len(text))
            self._write_json(
                HTTPStatus.OK,
                {"status": "accepted", "voice": voice, "approximate_duration": len(text) / 12.0},
            )

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            logging.debug("HTTP %s", format % args)


    def main() -> int:
        args = parse_args()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )

        for path in (args.model, args.config):
            if not Path(path).is_file():
                logging.error("Required Piper asset missing: %s", path)
                return 1

        def _stop(_signo, _frame):
            global STOP_REQUESTED  # noqa: PLW0603
            STOP_REQUESTED = True

        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, _stop)

        server = ThreadingHTTPServer((args.host, args.port), PlaceholderHandler)
        logging.warning(
            "Starting placeholder Piper server on %s:%s (no audio playback)",
            args.host,
            args.port,
        )
        try:
            while not STOP_REQUESTED:
                server.handle_request()
        finally:
            server.server_close()
            logging.info("Placeholder Piper server stopped.")
        return 0


    if __name__ == "__main__":
        sys.exit(main())
  '';

  whisperDaemon = pkgs.writeScript "aila-whisper-daemon.py" ''
    #!${pkgs.python312}/bin/python3
    import argparse
    import logging
    import signal
    import sys
    import time

    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Placeholder wake-word & STT bridge for Aila."
        )
        parser.add_argument(
            "--container-ip",
            required=True,
            help="IP address of the aila-core container API (e.g. 10.233.1.2)",
        )
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=30.0,
            help="Seconds between health log entries.",
        )
        return parser.parse_args()


    def main() -> int:
        args = parse_args()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        logging.info(
            "Aila whisper daemon placeholder active; would stream audio to http://%s:8080",
            args.container_ip,
        )

        running = True

        def _stop(signo, _frame):
            nonlocal running
            logging.info("Received signal %s; preparing to stop.", signo)
            running = False

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _stop)
            except Exception:  # pragma: no cover
                pass

        while running:
            logging.info(
                "Placeholder daemon heartbeat; container-ip=%s interval=%.1fs",
                args.container_ip,
                args.poll_interval,
            )
            time.sleep(args.poll_interval)

        logging.info("Aila whisper daemon stopped.")
        return 0


    if __name__ == "__main__":  # pragma: no cover
        sys.exit(main())
  '';
in
{
  services.ollama = {
    enable = true;
    acceleration = "cuda";
    listenAddress = "0.0.0.0:5001";
  };

  systemd.services.piper-tts = {
    description = "Piper Text-to-Speech Service";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    wants = [ "network-online.target" ];
    serviceConfig = {
      DynamicUser = true;
      ExecStart = "${piperServer} --model ${piperVoicePath} --config ${piperConfigPath} --host 0.0.0.0 --port 5002";
      Restart = "on-failure";
      RestartSec = 2;
    };
  };

  systemd.tmpfiles.rules = [
    "d /var/lib/aila/piper 0755 root root -"
  ];

  systemd.services.aila-ear = {
    description = "Aila Whisper Wake Word & STT Service";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    wants = [ "network-online.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "${whisperDaemon} --container-ip 10.233.1.2";
      Restart = "on-failure";
    };
  };
}
