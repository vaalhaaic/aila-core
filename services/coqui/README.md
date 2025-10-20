## Coqui TTS Service

Artifacts for deploying a Coqui TTS HTTP service backed by the `tts_models/zh-CN/baker/tacotron2-DDC-GST` voice.

- `config/config.yaml` – runtime configuration (model name, port, CUDA usage).
- `main/server.py` – FastAPI app exposing `/health` and `/synthesize`.
- `systemd/coqui.service` – unit file referencing `/opt/aila/coqui`.

During deployment, ensure the Python virtual environment installs `TTS==0.22.0`, `fastapi`, `uvicorn`, and `soundfile`. The first synthesis warms up the model and downloads weights if absent.
