"""
Main loop for the Aila core application.
Exposes a simple HTTP interface for the host Whisper service.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List
from urllib.error import URLError
from urllib.request import Request, urlopen

from personality import build_messages
from senses import SenseSnapshot, capture_snapshot


def _configure_logging() -> logging.Logger:
  log_dir = Path(os.getenv("AILA_LOG_DIR", "/var/log"))
  log_file = log_dir / "aila-mind.log"

  handlers: List[logging.Handler] = []
  try:
    log_dir.mkdir(parents=True, exist_ok=True)
    handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
  except OSError:
    pass
  handlers.append(logging.StreamHandler())

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=handlers,
  )
  return logging.getLogger("aila.mind")


logger = _configure_logging()


class VoiceAgent:
  """Coordinates dialogue with host services."""

  def __init__(self) -> None:
    self.host_addr = os.getenv("AILA_HOST_ADDR", "10.233.1.1")
    self.ollama_port = int(os.getenv("AILA_OLLAMA_PORT", "5001"))
    self.ollama_model = os.getenv("AILA_OLLAMA_MODEL", "llama3")
    self.piper_port = int(os.getenv("AILA_PIPER_PORT", "5002"))
    self.server_port = int(os.getenv("AILA_SERVER_PORT", "8080"))
    self.history: List[Dict[str, str]] = []
    self._lock = threading.Lock()

  def health(self) -> Dict[str, object]:
    with self._lock:
      turns = len(self.history)
    return {
      "status": "ready",
      "turns": turns,
      "ollama": f"http://{self.host_addr}:{self.ollama_port}",
      "piper": f"http://{self.host_addr}:{self.piper_port}",
    }

  def handle_transcript(self, text: str) -> Dict[str, object]:
    text = text.strip()
    if not text:
      raise ValueError("Transcript payload is empty.")

    snapshot = capture_snapshot()
    senses_summary = snapshot.summary()

    with self._lock:
      self.history.append({"role": "user", "content": text})
      messages = build_messages(self.history, senses_summary)

    reply = self._call_ollama(messages)

    with self._lock:
      self.history.append({"role": "assistant", "content": reply})

    self._speak(reply)
    self._log_interaction(text, reply, snapshot)
    return {"reply": reply, "senses": snapshot.as_dict()}

  def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
    url = f"http://{self.host_addr}:{self.ollama_port}/api/chat"
    payload = {
      "model": self.ollama_model,
      "messages": messages,
      "stream": False,
    }
    request = Request(
      url,
      data=json.dumps(payload).encode("utf-8"),
      headers={"Content-Type": "application/json"},
    )
    logger.debug("Calling Ollama at %s", url)
    try:
      with urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8")
    except URLError as exc:
      raise RuntimeError(f"Ollama request failed: {exc}") from exc

    data = json.loads(raw)
    reply = ""
    if "message" in data:
      reply = data["message"].get("content", "")
    elif "choices" in data and data["choices"]:
      reply = data["choices"][0]["message"]["content"]
    if not reply:
      raise RuntimeError(f"Ollama response missing content: {data}")
    return reply.strip()

  def _speak(self, text: str) -> None:
    url = f"http://{self.host_addr}:{self.piper_port}/speak"
    payload = {"text": text, "voice": "zh_CN-huayan-medium"}
    request = Request(
      url,
      data=json.dumps(payload).encode("utf-8"),
      headers={"Content-Type": "application/json"},
    )
    try:
      with urlopen(request, timeout=30):
        logger.debug("Delivered TTS request to Piper")
    except URLError as exc:
      logger.warning("Failed to reach Piper at %s: %s", url, exc)

  def _log_interaction(self, user_text: str, reply: str, snapshot: SenseSnapshot) -> None:
    logger.info(
      "turn complete user=%r reply=%r senses=%s",
      user_text,
      reply,
      snapshot.summary(),
    )


agent = VoiceAgent()


class AgentRequestHandler(BaseHTTPRequestHandler):
  server_version = "AilaMind/1.0"
  sys_version = ""

  def _json_body(self) -> Dict[str, object]:
    length = int(self.headers.get("Content-Length", "0"))
    if length <= 0:
      return {}
    raw = self.rfile.read(length)
    try:
      return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
      raise ValueError(f"Invalid JSON payload: {exc}") from exc

  def _write_json(self, status: HTTPStatus, payload: Dict[str, object]) -> None:
    body = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def do_GET(self) -> None:  # noqa: N802
    if self.path == "/health":
      self._write_json(HTTPStatus.OK, agent.health())
      return
    self.send_error(HTTPStatus.NOT_FOUND, "Unknown path")

  def do_POST(self) -> None:  # noqa: N802
    if self.path == "/transcript":
      try:
        payload = self._json_body()
        text = str(payload.get("text", ""))
        result = agent.handle_transcript(text)
      except ValueError as exc:
        self._write_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        return
      except Exception as exc:  # pragma: no cover
        logger.exception("Failed to process transcript: %s", exc)
        self._write_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
        return
      self._write_json(HTTPStatus.OK, result)
      return
    self.send_error(HTTPStatus.NOT_FOUND, "Unknown path")

  def log_message(self, format: str, *args) -> None:  # noqa: A003
    logger.debug("HTTP %s", format % args)


def run_server() -> None:
  server_address = ("0.0.0.0", agent.server_port)
  httpd = ThreadingHTTPServer(server_address, AgentRequestHandler)
  logger.info("Aila mind listening on %s:%s", *server_address)
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    logger.info("Shutdown requested; exiting.")
  finally:
    httpd.server_close()


if __name__ == "__main__":
  run_server()
