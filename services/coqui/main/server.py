"""Coqui TTS REST endpoint."""

from __future__ import annotations

import argparse
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import soundfile as sf
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from TTS.utils.synthesizer import Synthesizer


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1)


@dataclass
class CoquiConfig:
    model_name: str
    listen_host: str = "0.0.0.0"
    listen_port: int = 9082
    use_cuda: bool = True
    speaker_id: int | None = None
    sample_rate: int | None = None
    warmup_text: str | None = None


def load_config(path: Path) -> CoquiConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return CoquiConfig(**data)


class CoquiRuntime:
    def __init__(self, config: CoquiConfig) -> None:
        self.config = config
        self.synthesizer = Synthesizer.from_pretrained(
            model_name=config.model_name,
            use_cuda=config.use_cuda,
        )
        self.sample_rate = config.sample_rate or getattr(self.synthesizer, "output_sample_rate", 22050)
        if config.warmup_text:
            self._synthesize(config.warmup_text, eager=False)

    def _synthesize(self, text: str, eager: bool = True) -> bytes | None:
        kwargs: Dict[str, Any] = {}
        if self.config.speaker_id is not None:
            kwargs["speaker"] = self.config.speaker_id

        audio = self.synthesizer.tts(text, **kwargs)
        if not eager:
            return None

        buffer = io.BytesIO()
        sf.write(buffer, audio, self.sample_rate, format="WAV")
        return buffer.getvalue()

    def synthesize(self, text: str) -> bytes:
        payload = self._synthesize(text, eager=True)
        assert payload is not None  # for type-checkers
        return payload


def create_app(config: CoquiConfig) -> FastAPI:
    runtime = CoquiRuntime(config)
    app = FastAPI(title="Aila Coqui TTS Service")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {
            "status": "ok",
            "model": config.model_name,
            "use_cuda": config.use_cuda,
            "sample_rate": runtime.sample_rate,
        }

    @app.post("/synthesize")
    def synthesize(request: SpeakRequest) -> Response:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="text must not be empty")

        audio = runtime.synthesize(text)
        headers = {
            "X-Model": config.model_name,
            "X-Sample-Rate": str(runtime.sample_rate),
        }
        return Response(content=audio, media_type="audio/wav", headers=headers)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to Coqui YAML config")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    app = create_app(config)
    uvicorn.run(app, host=config.listen_host, port=config.listen_port)


if __name__ == "__main__":
    main()
