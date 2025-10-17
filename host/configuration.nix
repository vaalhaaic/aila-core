{ config, pkgs, lib, ... }:

{
  imports = [
    ./hardware.nix
    ./services.nix
  ];

  boot.loader.systemd-boot.enable = false;
  boot.loader.efi = {
    canTouchEfiVariables = true;
    efiSysMountPoint = "/boot/efi";
  };
  boot.loader.grub = {
    enable = true;
    device = "nodev";
    efiSupport = true;
    efiInstallAsRemovable = false;
  };

  users.mutableUsers = true;

  i18n = {
    defaultLocale = "zh_CN.UTF-8";
    supportedLocales = [
      "en_US.UTF-8/UTF-8"
      "zh_CN.UTF-8/UTF-8"
    ];
  };

  nixpkgs.config.allowUnfreePredicate = pkg:
    let
      name = lib.getName pkg;
      prefixes = [
        "cuda-"
        "cuda_"
        "nvidia-"
        "libcu"
        "libnv"
        "libnpp"
      ];
      explicit = [
        "cuda-merged"
        "cuda-merged-12.2"
      ];
    in
      builtins.elem name explicit
      || lib.any (prefix: lib.strings.hasPrefix prefix name) prefixes;

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
    autoStart = true;
    config = import ../container/configuration.nix;
    privateNetwork = true;
    hostAddress = "10.233.1.1";
    localAddress = "10.233.1.2";
  };

  system.stateVersion = "24.05";
}
