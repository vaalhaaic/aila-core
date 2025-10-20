"""LLM client abstraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMClient:
    endpoint: str

    def complete(self, system_prompt: str, prompt: str) -> str:
        # TODO: connect to Ollama HTTP API.
        return f"[placeholder completion] {prompt}"
