"""Custom middleware hooks for Ollama requests."""

from __future__ import annotations

from typing import Any, Dict


def transform_prompt(prompt: str, context: Dict[str, Any] | None = None) -> str:
    """Inject persona metadata into the prompt before sending to Ollama."""
    context = context or {}
    persona = context.get("persona", "Aila")
    prefix = context.get("prefix", "")
    suffix = context.get("suffix", "")
    return f"{prefix}[{persona}] {prompt}{suffix}"


def post_process(response: str) -> str:
    """Normalize whitespace on responses."""
    return response.strip()

