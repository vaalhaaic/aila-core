"""Perception adapters for external services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class SpeechRecognitionClient(Protocol):
    def transcribe(self, audio_path: str) -> str: ...


@dataclass
class PerceptionRouter:
    recognizer: SpeechRecognitionClient

    def transcribe(self, audio_path: str) -> str:
        return self.recognizer.transcribe(audio_path)
