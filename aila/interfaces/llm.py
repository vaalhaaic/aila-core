"""LLM client abstraction backed by iFLYTEK Spark."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass, field
from email.utils import formatdate
from typing import Dict, List, Optional
from urllib.parse import urlparse

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
    """Thin wrapper around the iFLYTEK Spark chat completions endpoint."""

    app_id: str = field(default_factory=lambda: os.getenv("XUNFEI_APP_ID", ""))
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_url: str = field(
        default_factory=lambda: os.getenv("XUNFEI_API_URL", "https://spark-api-open.xf-yun.com/v2/chat/completions")
    )
    temperature: float = field(default_factory=lambda: float(os.getenv("XUNFEI_TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("XUNFEI_MAX_TOKENS", "2048")))
    timeout: int = field(default_factory=lambda: int(os.getenv("XUNFEI_TIMEOUT", "60")))

    def __post_init__(self) -> None:
        if not self.api_key:
            self.api_key = os.getenv("XUNFEI_API_KEY")
        if not self.api_secret:
            self.api_secret = os.getenv("XUNFEI_API_SECRET")

        if not self.app_id or not self.api_key or not self.api_secret:
            raise LLMError(
                "XUNFEI_APP_ID, XUNFEI_API_KEY, and XUNFEI_API_SECRET must be set "
                "(see system/etc/aila/env.d/xunfei.conf)."
            )

        parsed = urlparse(self.api_url)
        self._host = parsed.netloc
        self._path = parsed.path or "/v2/chat/completions"
        self._session = requests.Session()

    def _build_headers(self) -> Dict[str, str]:
        date_header = formatdate(time.time(), usegmt=True)
        signature_origin = f"host: {self._host}\ndate: {date_header}\nPOST {self._path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode()
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", '
            f'signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode()

        return {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Host": self._host,
            "Date": date_header,
        }

    def complete(self, system_prompt: str, prompt: str) -> str:
        messages = _build_messages(system_prompt, prompt)
        payload = {
            "app_id": self.app_id,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = self._session.post(
            self.api_url,
            headers=self._build_headers(),
            json=payload,
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network failure
            raise LLMError(f"Spark request failed: {exc} - {response.text}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected Spark response shape: {data}") from exc
