{ config, pkgs, ... }:

{
  environment.etc."aila-app" = {
    source = ../../app;
    target = "/opt/aila";
  };

  systemd.services.aila-mind = {
    description = "Aila's Core Consciousness Loop";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "${pkgs.python312}/bin/python /opt/aila/main_loop.py";
      WorkingDirectory = "/opt/aila";
      Restart = "always";
      RestartSec = 5;
    };
  };

  systemd.timers.aila-heartbeat = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnUnitActiveSec = "5..15s";
      RandomizedDelaySec = "5s";
    };
  };

  systemd.services.aila-heartbeat = {
    serviceConfig.Type = "oneshot";
    script = ''echo "$(date --iso-8601=seconds) thump-thump" >> /var/log/aila-internal.log'';
  };

  systemd.timers.aila-reflection = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;
    };
  };

  systemd.services.aila-reflection = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.python312}/bin/python /opt/aila/reflection.py";
    };
  };
}
