"""Piper REST endpoint placeholder."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import yaml


class SpeakRequest(BaseModel):
    text: str


class PiperConfig(BaseModel):
    voice: str
    speaker: int = 0
    sample_rate: int = 22050
    listen_host: str = "0.0.0.0"
    listen_port: int = 9082


def load_config(path: Path) -> PiperConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PiperConfig(**data)


def create_app(config: PiperConfig) -> FastAPI:
    app = FastAPI(title="Aila Piper Service")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok", "voice": config.voice}

    @app.post("/speak")
    def speak(request: SpeakRequest) -> Dict[str, str]:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="text must not be empty")
        # TODO: integrate Piper runtime. This is a stub only.
        return {"status": "placeholder", "voice": config.voice}

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", required=True, help="Path to voice JSON config")
    args = parser.parse_args()

    config = load_config(Path(args.voice))
    app = create_app(config)
    uvicorn.run(app, host=config.listen_host, port=config.listen_port)


if __name__ == "__main__":
    main()
