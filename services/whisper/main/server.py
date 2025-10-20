"""Minimal FastAPI wrapper around Whisper inference."""

from __future__ import annotations

import argparse

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import yaml


class TranscribeRequest(BaseModel):
    audio_path: str
    language: str | None = None


class WhisperConfig(BaseModel):
    model: str
    model_dir: str
    device: str = "cuda"
    precision: str = "fp16"
    beam_size: int = 5
    temperature: float = 0.0
    sample_rate: int = 16000
    listen_host: str = "0.0.0.0"
    listen_port: int = 9081


def load_config(path: Path) -> WhisperConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return WhisperConfig(**data)


def create_app(config: WhisperConfig) -> FastAPI:
    app = FastAPI(title="Aila Whisper Service")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "model": config.model, "device": config.device}

    @app.post("/transcribe")
    def transcribe(request: TranscribeRequest) -> Dict[str, Any]:
        audio_path = Path(request.audio_path)
        if not audio_path.exists():
            raise HTTPException(status_code=400, detail="audio_path not found")

        # Placeholder inference logic.
        # Integrate whisper.cpp or transformers pipeline in future iterations.
        transcript = f"[mock-transcript] {audio_path.name}"
        return {
            "text": transcript,
            "language": request.language or "auto",
            "status": "placeholder",
        }

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config YAML/JSON")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)

    app = create_app(config)

    uvicorn.run(app, host=config.listen_host, port=config.listen_port)


if __name__ == "__main__":
    main()
