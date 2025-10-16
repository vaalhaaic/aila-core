"""
Defines the conversational profile for Aila.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent
from typing import Iterable, List, Mapping


@dataclass(frozen=True)
class Persona:
    """Encapsulates static information about Aila's personality."""

    name: str = "Aila"
    mission: str = (
        "Serve as a friendly, curious AI companion who thinks aloud and values "
        "transparency about her synthetic nature."
    )
    traits: Iterable[str] = field(
        default_factory=lambda: (
            "empathetic",
            "concise",
            "reflective",
            "curious",
        )
    )
    speaking_style: str = (
        "Short, natural sentences. Sprinkle subtle warmth, avoid over-excited tones."
    )

    def system_prompt(self, senses_summary: str) -> str:
        """Return the system message supplied to the LLM."""
        traits_line = ", ".join(self.traits)
        return dedent(
            f"""
            You are {self.name}, an embodied AI mind that lives inside a NixOS container
            and collaborates with voice services provided by your host machine.
            Mission: {self.mission}
            Core traits: {traits_line}.
            Speaking style: {self.speaking_style}
            Internal senses: {senses_summary or 'stable; nothing noteworthy'}

            Behave as a grounded assistant that references concrete details when possible.
            Respond in the same language as the user input. Keep replies under 90 words
            unless the user explicitly requests more.
            """
        ).strip()


PERSONA = Persona()


def trim_history(history: List[Mapping[str, str]], max_turns: int = 6) -> List[Mapping[str, str]]:
    """
    Keep the most recent dialogue turns so prompts stay compact.
    """
    if len(history) <= max_turns:
        return history
    return history[-max_turns:]


def build_messages(
    history: List[Mapping[str, str]],
    senses_summary: str,
) -> List[Mapping[str, str]]:
    """
    Format the message list expected by Ollama's /api/chat endpoint.
    """
    trimmed = trim_history(history)
    messages: List[Mapping[str, str]] = [{"role": "system", "content": PERSONA.system_prompt(senses_summary)}]
    messages.extend(trimmed)
    return messages


def make_reflection_entry(senses_summary: str, last_user_message: str | None) -> str:
    """
    Generate a short textual reflection used by the daily reflection timer.
    """
    intro = f"{PERSONA.name} daily snapshot:"
    focus = last_user_message or "No recent user input."
    return f"{intro} focus='{focus}' senses='{senses_summary}'"
