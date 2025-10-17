{ config, pkgs, ... }:

{
  imports = [
    ./hardware.nix
    ./services.nix
  ];

  # Provide essential CLI tools on the host.
  environment.systemPackages = with pkgs; [
    git
  ];

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 5001 5002 ];
  };

  boot.enableContainers = true;

  containers.aila-core = {
    enable = true;
    autoStart = true;
    config = import ../container/configuration.nix;
    privateNetwork = true;
    hostAddress = "10.233.1.1";
    localAddress = "10.233.1.2";
  };

  system.stateVersion = "24.05";
}
