"""LLM client abstraction backed by OpenRouter."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests


class LLMError(RuntimeError):
    """Raised when the LLM backend returns an error response."""


def _build_messages(system_prompt: str | None, prompt: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


@dataclass
class LLMClient:
    """Thin wrapper around the OpenRouter Chat Completions endpoint."""

    base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    model: str = field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free"))
    api_key: Optional[str] = None
    referer: Optional[str] = field(default_factory=lambda: os.getenv("OPENROUTER_REFERER"))
    app_title: Optional[str] = field(default_factory=lambda: os.getenv("OPENROUTER_APP_TITLE"))
    timeout: int = field(default_factory=lambda: int(os.getenv("OPENROUTER_TIMEOUT", "60")))

    def __post_init__(self) -> None:
        if not self.api_key:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise LLMError("OPENROUTER_API_KEY is not set. Export it before starting the runtime.")

        self._session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.app_title:
            headers["X-Title"] = self.app_title
        return headers

    def complete(self, system_prompt: str, prompt: str) -> str:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": _build_messages(system_prompt, prompt),
        }

        response = self._session.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - error path
            raise LLMError(f"OpenRouter request failed: {exc} - {response.text}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:  # pragma: no cover - schema error
            raise LLMError(f"Unexpected OpenRouter response shape: {data}") from exc
