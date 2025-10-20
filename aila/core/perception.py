"""Perception adapters for external services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class WhisperClient(Protocol):
    def transcribe(self, audio_path: str) -> str: ...


@dataclass
class PerceptionRouter:
    whisper: WhisperClient

    def transcribe(self, audio_path: str) -> str:
        return self.whisper.transcribe(audio_path)
