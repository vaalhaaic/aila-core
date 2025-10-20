"""Speech synthesis facade."""

from __future__ import annotations

from dataclasses import dataclass


class CoquiClient:
    def speak(self, text: str) -> str:
        raise NotImplementedError


@dataclass
class SpeechInterface:
    tts: CoquiClient

    def speak(self, text: str) -> str:
        return self.tts.speak(text)
