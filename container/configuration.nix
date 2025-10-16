{ config, pkgs, ... }:

{
  imports = [ ./services.nix ];

  environment.systemPackages = with pkgs; [
    python312
  ];

  networking.defaultGateway = "10.233.1.1";
  networking.nameservers = [ "10.233.1.1" ];

  time.timeZone = "America/Los_Angeles";

  system.stateVersion = "24.05";
}
