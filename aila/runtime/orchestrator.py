"""Runtime orchestrator for Aila."""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from ..core import MindPipeline, PerceptionRouter, Planner
from ..interfaces.llm import LLMClient
from ..interfaces.speech import SpeechInterface, PiperClient


logger = logging.getLogger("aila.orchestrator")


@dataclass
class WhisperAdapter:
    endpoint: str

    def transcribe(self, audio_path: str) -> str:
        logger.info("Transcribing %s via %s", audio_path, self.endpoint)
        return f"[whisper placeholder transcript for {audio_path}]"


@dataclass
class PiperAdapter(PiperClient):
    endpoint: str

    def speak(self, text: str) -> str:
        logger.info("Synthesizing speech via %s", self.endpoint)
        return f"[audio-bytes placeholder] {text}"


@dataclass
class Orchestrator:
    mind: MindPipeline

    def process_audio(self, audio_path: str) -> str:
        logger.debug("Processing audio %s", audio_path)
        return self.mind.handle_audio(audio_path)

    def process_text(self, text: str) -> str:
        logger.debug("Processing text: %s", text)
        return self.mind.handle_text(text)


def build_pipeline(whisper_url: str, ollama_url: str, piper_url: str) -> MindPipeline:
    whisper = WhisperAdapter(endpoint=whisper_url)
    perception = PerceptionRouter(whisper=whisper)
    llm = LLMClient(endpoint=ollama_url)
    planner = Planner(llm=llm)
    piper = PiperAdapter(endpoint=piper_url)
    speech = SpeechInterface(piper=piper)
    return MindPipeline(perception=perception, planner=planner, speech=speech)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--whisper", default="http://localhost:9081")
    parser.add_argument("--ollama", default="http://localhost:11434")
    parser.add_argument("--piper", default="http://localhost:9082")
    parser.add_argument("--audio")
    parser.add_argument("--text")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper())

    mind = build_pipeline(args.whisper, args.ollama, args.piper)
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
