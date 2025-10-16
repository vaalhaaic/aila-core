# host/services.nix
{ config, pkgs, ... }:

{
  # Ollama Service Configuration
  services.ollama = {
    enable = true;
    acceleration = "cuda"; # Specify acceleration type
    listenAddress = "0.0.0.0";
    port = 5001;
  };

  # Piper TTS Service Configuration
  services.piper-tts = {
    enable = true;
    listenAddress = "0.0.0.0";
    port = 5002;
    # Path to voice model provided by Nixpkgs
    voice = "${pkgs.piper-voices}/zh_CN-huayan-medium.onnx";
  };

  # Whisper STT Service Definition (Placeholder for custom implementation)
  systemd.services.aila-ear = {
    description = "Aila Whisper Wake Word & STT Service";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "simple";
      # NOTE: This script must be implemented separately. It should call the container's API.
      ExecStart = "/usr/bin/python3 /opt/aila-hardware-services/whisper_daemon.py --container-ip 10.233.1.2";
      Restart = "on-failure";
      SupplementaryGroups = [ "audio" ];
    };
  };
}
