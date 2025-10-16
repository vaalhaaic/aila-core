### **`aila-nixos-dna` AutoDev Specification v1.0**

```yaml
---
ProjectName: aila-nixos-dna
RuntimeEnvironment: NixOS, NixOS Containers, Python 3.12, systemd
PrimaryGoal: Declarative and automated deployment of a containerized, voice-interactive AI agent.
CoreTechnologies:
  - NixOS: Host and container OS.
  - Ollama: LLM inference service.
  - Whisper: Wake word detection and Speech-to-Text (STT) service.
  - Piper: Text-to-Speech (TTS) service.
  - Python: Core application logic.
DeploymentModel: Git-based, single-script execution via `git pull` and `deploy.sh`.
SuccessCondition: The script `scripts/deploy.sh` executes successfully, and the system passes all verification criteria, resulting in a functional voice agent.
---
```

### **1. System Architecture: Host-Container Model**

The system MUST be implemented using a two-part architecture: a NixOS Host System and a dedicated NixOS Container.

| Component ID | Component Name | Location | Function |
| :--- | :--- | :--- | :--- |
| `HOST-OS` | NixOS Host | Physical Server | Manages hardware, networking, and NixOS Container lifecycle. |
| `SVC-OLLAMA` | LLM Service | Host | Exposes an LLM inference endpoint. MUST listen on `0.0.0.0` to be accessible by the container. |
| `SVC-WHISPER` | STT Service | Host | Manages microphone access, performs wake word detection, and converts speech to text. MUST forward text output to the `APP-CORE` API endpoint. |
| `SVC-PIPER` | TTS Service | Host | Exposes a TTS endpoint. Receives text and outputs audio to the host's sound device. MUST listen on `0.0.0.0`. |
| `CONT-AILA` | Aila-Core Container | NixOS Container | Runs the isolated application logic. MUST NOT have direct hardware access. Communicates with Host services via the virtual network interface. |
| `APP-CORE` | Core Logic Loop | Container | The primary Python application. It orchestrates the interaction between `SVC-WHISPER`, `SVC-OLLAMA`, and `SVC-PIPER`. |
| `APP-STATE` | Internal State Services | Container | A set of systemd services and timers responsible for simulating internal state (`heartbeat`, `senses`, `reflection`). |

### **2. Required Directory Structure**

The source code repository MUST conform to the following file and directory structure.

```
aila-nixos-dna/
├── host/
│   ├── configuration.nix
│   ├── hardware.nix
│   └── services.nix
├── container/
│   ├── configuration.nix
│   └── services.nix
├── app/
│   ├── main_loop.py
│   ├── personality.py
│   ├── senses.py
│   └── reflection.py
├── scripts/
│   └── deploy.sh
└── .gitignore
```

### **3. File Content Specifications**

#### **3.1 `host/configuration.nix`**

This file MUST define the host system's configuration and declare the `aila-core` container.

```nix
# host/configuration.nix
{ config, pkgs, ... }:

{
  imports = [ ./hardware.nix ./services.nix ];

  # Required system packages
  environment.systemPackages = with pkgs; [ git ];

  # Networking and firewall rules for service access
  networking.firewall.enable = true;
  networking.firewall.allowedTCPPorts = [ 5001 /* Ollama Port, adjust if needed */ 5002 /* Piper Port */ ];

  # Define and configure the aila-core container
  containers.aila-core = {
    enable = true;
    autoStart = true;
    # Import the container's declarative configuration
    config = import ../container/configuration.nix;
    # Required for communication between host and container
    privateNetwork = true;
    hostAddress = "10.233.1.1";
    localAddress = "10.233.1.2";
  };
}
```

#### **3.2 `host/services.nix`**

This file MUST define all hardware-dependent services running on the host.

```nix
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
```

#### **3.3 `container/configuration.nix`**

This file MUST define the complete configuration of the `aila-core` container.

```nix
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
```

#### **3.4 `container/services.nix`**

This file MUST define the application logic services and internal state timers inside the container.

```nix
# container/services.nix
{ config, pkgs, ... }:

{
  # Copy the application source code into the container's filesystem
  environment.etc."aila-app" = {
    source = ../../app;
    target = "/opt/aila";
  };
  
  # Main application logic service
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

  # Heartbeat timer and service
  systemd.timers.aila-heartbeat = {
    wantedBy = [ "timers.target" ];
    timerConfig = { OnUnitActiveSec = "5..15s"; RandomizedDelaySec = "5s"; };
  };
  systemd.services.aila-heartbeat = {
    serviceConfig.Type = "oneshot";
    script = ''echo "$(date --iso-8601=seconds) thump-thump" >> /var/log/aila-internal.log'';
  };
  
  # Reflection timer and service
  systemd.timers.aila-reflection = {
    wantedBy = [ "timers.target" ];
    timerConfig = { OnCalendar = "daily"; Persistent = true; };
  };
  systemd.services.aila-reflection = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.python312}/bin/python /opt/aila/reflection.py";
    };
  };
}
```

#### **3.5 `scripts/deploy.sh`**

This script is the entry point for deployment. It MUST synchronize the configuration files and trigger a system rebuild.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Define repository root and system config destination
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
NIXOS_CONFIG_DIR="/etc/nixos"

# --- TASK 1: VALIDATE ---
if [[ ! -d "${REPO_ROOT}/host" || ! -f "${REPO_ROOT}/host/configuration.nix" ]]; then
    echo "ERROR: Invalid repository structure. 'host/configuration.nix' not found." >&2
    exit 1
fi
if [[ "$EUID" -ne 0 ]]; then
    echo "ERROR: This script must be run with sudo or as root." >&2
    exit 1
fi

# --- TASK 2: SYNCHRONIZE FILES ---
echo "Syncing repository config to ${NIXOS_CONFIG_DIR}..."
# Use rsync to copy the host configuration.
# The `container` and `app` dirs are referenced via relative paths in Nix files, so they don't need to be copied to /etc.
# The deploy script itself must reside with the repo.
rsync -av --delete "${REPO_ROOT}/host/" "${NIXOS_CONFIG_DIR}/"
rsync -av "${REPO_ROOT}/container/" "${NIXOS_CONFIG_DIR}/container/"

# --- TASK 3: REBUILD SYSTEM ---
echo "Executing nixos-rebuild switch..."
nixos-rebuild switch --flake "${NIXOS_CONFIG_DIR}#"

# --- TASK 4: REPORT SUCCESS ---
echo "Deployment successful. Aila system is active."
exit 0
```

### **4. Deployment and Execution Protocol**

1.  **Prerequisites:** The target server has a functional NixOS installation. The repository is cloned.
2.  **Step 1: Update Repository.** Execute the following command in the repository directory:
    ```bash
    git pull origin main
    ```
3.  **Step 2: Execute Deployment.** Run the deployment script with superuser privileges:
    ```bash
    sudo ./scripts/deploy.sh
    ```

### **5. Verification Criteria**

Deployment is considered successful if all the following conditions are met:

1.  The `deploy.sh` script exits with status code `0`.
2.  The command `systemctl is-active aila-core.service` on the host returns `active`.
3.  The command `nixos-container run aila-core -- systemctl is-active aila-mind.service` returns `active`.
4.  An end-to-end voice interaction test passes:
      * **Input:** The wake word "aila" is spoken, followed by a phrase (e.g., "hello").
      * **Expected Output:** The system plays back a coherent audio response generated by the LLM.
      * **Verification:** The interaction is logged within the container at `/var/log/aila-internal.log`.