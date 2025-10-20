# Ollama Service

GPU-accelerated large language model runtime exposed through the Ollama server. This layer delivers fast, local inference for dialogue and planning.

## Components

- `config/ollama.yaml` – server configuration (model list, GPU preferences).
- `systemd/ollama.service` – service unit to manage the daemon.
- `scripts/pull_models.sh` – helper to download or update model blobs.
- `main/` – custom adapters or middleware added on top of Ollama.

## Deployment

1. Copy configuration to `/etc/ollama/ollama.yaml`.
2. Run `scripts/pull_models.sh mistral` (for example) to fetch models before starting the service.
3. Enable the service with `sudo systemctl enable --now ollama.service`.

The service listens on `127.0.0.1:11434` by default. Expose through reverse proxy if remote access is required.

