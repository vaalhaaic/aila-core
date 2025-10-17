{ config, pkgs, lib, ... }:

let
  # Location on the host where the Piper voice model should be stored.
  # Copy `zh_CN-huayan-medium.onnx` into this directory before enabling the service.
  piperVoicePath = "/var/lib/aila/piper/zh_CN-huayan-medium.onnx";

  piperCommand = pkgs.writeShellScript "piper-tts-server" ''
    set -euo pipefail

    if [[ ! -f "${piperVoicePath}" ]]; then
      echo "Piper voice missing at ${piperVoicePath}" >&2
      exit 1
    fi

    exec ${pkgs.piper}/bin/piper \
      --server \
      --host 0.0.0.0 \
      --port 5002 \
      --model "${piperVoicePath}"
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
    after = [ "network.target" ];
    serviceConfig = {
      ExecStart = piperCommand;
      Restart = "on-failure";
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
