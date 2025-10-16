{ config, pkgs, ... }:

{
  services.ollama = {
    enable = true;
    acceleration = "cuda";
    listenAddress = "0.0.0.0";
    port = 5001;
  };

  services.piper-tts = {
    enable = true;
    listenAddress = "0.0.0.0";
    port = 5002;
    voice = "${pkgs.piper-voices}/zh_CN-huayan-medium.onnx";
  };

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
