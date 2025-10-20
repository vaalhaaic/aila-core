# Whisper Service

Speech-to-text service powered by Whisper. Designed to run locally with GPU acceleration where available.

## Components

- `config/config.yaml` – runtime parameters such as model size and compute device.
- `systemd/whisper.service` – manages the ASR worker process.
- `scripts/install_model.sh` – fetches Whisper models from Hugging Face.
- `main/` – FastAPI server exposing synchronous and streaming transcription.

## Deployment

1. Run `scripts/install_model.sh medium` to download a base model.
2. Adjust `config/config.yaml` to point to the correct model directory and device.
3. Enable systemd unit: `sudo systemctl enable --now whisper.service`.
4. Test locally with `curl http://localhost:9081/transcribe`.

