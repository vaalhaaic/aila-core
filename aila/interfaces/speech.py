"""Speech synthesis facade."""

from __future__ import annotations

from dataclasses import dataclass


class PiperClient:
    def speak(self, text: str) -> str:
        raise NotImplementedError


@dataclass
class SpeechInterface:
    piper: PiperClient

    def speak(self, text: str) -> str:
        return self.piper.speak(text)
