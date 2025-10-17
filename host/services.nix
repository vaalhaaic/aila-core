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
    serviceConfig = {
      Type = "simple";
      ExecStart = "/usr/bin/python3 /opt/aila-hardware-services/whisper_daemon.py --container-ip 10.233.1.2";
      Restart = "on-failure";
      SupplementaryGroups = [ "audio" ];
    };
  };
}
