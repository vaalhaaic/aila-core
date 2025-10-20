"""Mind pipeline orchestrating perception, planning, and speech."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from .perception import PerceptionRouter
from .planner import Planner
from ..interfaces.speech import SpeechInterface


@dataclass
class MindPipeline:
    perception: PerceptionRouter
    planner: Planner
    speech: SpeechInterface

    def handle_audio(self, audio_path: str) -> str:
        transcript = self.perception.transcribe(audio_path)
        decision = self.planner.plan(transcript)
        return self.speech.speak(decision)

    def handle_text(self, text: str, context: Dict[str, str] | None = None) -> str:
        decision = self.planner.plan(text, context=context)
        return decision
