"""Runtime orchestrator for Aila."""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import requests

from ..core import MindPipeline, PerceptionRouter, Planner
from ..interfaces.llm import LLMClient
from ..interfaces.speech import CoquiClient, SpeechInterface


logger = logging.getLogger("aila.orchestrator")


@dataclass
class WhisperAdapter:
    endpoint: str
    timeout: int = 120

    def transcribe(self, audio_path: str) -> str:
        url = f"{self.endpoint.rstrip('/')}/inference"
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        logger.info("Transcribing %s via %s", audio_file, url)
        with audio_file.open("rb") as handle:
            files = {"file": (audio_file.name, handle, "audio/wav")}
            data = {"response_format": "json"}
            response = requests.post(url, data=data, files=files, timeout=self.timeout)
        response.raise_for_status()

        try:
            payload = response.json()
        except ValueError:
            return response.text.strip()

        if isinstance(payload, dict) and "text" in payload:
            return payload["text"]
        return str(payload)


@dataclass
class CoquiAdapter(CoquiClient):
    endpoint: str
    timeout: int = 60

    def speak(self, text: str) -> str:
        url = f"{self.endpoint.rstrip('/')}/synthesize"
        logger.info("Synthesizing speech via %s", url)
        response = requests.post(url, json={"text": text}, timeout=self.timeout)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            wav_file.write(response.content)
            saved_path = Path(wav_file.name)

        logger.debug("Audio synthesized to %s", saved_path)
        return str(saved_path)


@dataclass
class Orchestrator:
    mind: MindPipeline

    def process_audio(self, audio_path: str) -> str:
        logger.debug("Processing audio %s", audio_path)
        return self.mind.handle_audio(audio_path)

    def process_text(self, text: str) -> str:
        logger.debug("Processing text: %s", text)
        return self.mind.handle_text(text)


def build_pipeline(whisper_url: str, llm_base_url: str, llm_model: str, coqui_url: str) -> MindPipeline:
    whisper = WhisperAdapter(endpoint=whisper_url)
    perception = PerceptionRouter(whisper=whisper)
    llm = LLMClient(base_url=llm_base_url, model=llm_model)
    planner = Planner(llm=llm)
    coqui = CoquiAdapter(endpoint=coqui_url)
    speech = SpeechInterface(tts=coqui)
    return MindPipeline(perception=perception, planner=planner, speech=speech)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--whisper", default=os.getenv("AILA_WHISPER_URL", "http://localhost:9081"))
    parser.add_argument(
        "--llm-base-url",
        default=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )
    parser.add_argument(
        "--llm-model",
        default=os.getenv("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free"),
    )
    parser.add_argument("--coqui", default=os.getenv("AILA_COQUI_URL", "http://localhost:9082"))
    parser.add_argument("--audio")
    parser.add_argument("--text")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper())

    mind = build_pipeline(args.whisper, args.llm_base_url, args.llm_model, args.coqui)
    orchestrator = Orchestrator(mind=mind)

    if args.audio:
        result = orchestrator.process_audio(args.audio)
        print(result)
    elif args.text:
        result = orchestrator.process_text(args.text)
        print(result)
    else:
        parser.error("Provide either --audio or --text")


if __name__ == "__main__":
    main()
