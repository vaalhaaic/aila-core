"""Planner bridging OpenRouter completions with business rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..interfaces.llm import LLMClient


@dataclass
class Planner:
    llm: LLMClient

    def plan(self, prompt: str, context: Dict[str, str] | None = None) -> str:
        context = context or {}
        system_prompt = context.get("system_prompt", "You are Aila, an empathetic assistant.")
        return self.llm.complete(system_prompt, prompt)
