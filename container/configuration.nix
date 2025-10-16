# container/configuration.nix
{ config, pkgs, ... }:

{
  imports = [ ./services.nix ];

  # System packages required inside the container
  environment.systemPackages = with pkgs; [ python312 ];
  
  # Network configuration to reach the host
  networking.defaultGateway = "10.233.1.1";
  networking.nameservers = [ "10.233.1.1" ];

  # Set timezone
  time.timeZone = "America/Los_Angeles";
}
