"""Speech synthesis facade."""

from __future__ import annotations

import base64
import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tts.v20190823 import models, tts_client


logger = logging.getLogger(__name__)


class TextToSpeechClient:
    """Abstract TTS client."""

    def speak(self, text: str) -> str:
        raise NotImplementedError


@dataclass
class SpeechInterface:
    """Facade exposing speech synthesis for the pipeline."""

    tts: TextToSpeechClient

    def speak(self, text: str) -> str:
        return self.tts.speak(text)


@dataclass
class TencentTTSClient(TextToSpeechClient):
    """Thin wrapper around Tencent Cloud Text-to-Speech service."""

    secret_id: str
    secret_key: str
    region: str = "ap-beijing"
    voice_type: int = 602003  # 爱小悠
    speed: int = 0
    volume: int = 0
    audio_format: str = "wav"
    sample_rate: int = 16000
    _client: tts_client.TtsClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        cred = credential.Credential(self.secret_id, self.secret_key)
        self._client = tts_client.TtsClient(cred, self.region)
        logger.info(
            "Initialized Tencent TTS client (region=%s, voice_type=%s, format=%s)",
            self.region,
            self.voice_type,
            self.audio_format,
        )

    def speak(self, text: str) -> str:
        if not text.strip():
            raise ValueError("text must not be empty for TTS synthesis")

        request = models.TextToVoiceRequest()
        request.Text = text
        request.VoiceType = self.voice_type
        request.Speed = self.speed
        request.Volume = self.volume
        request.Format = self.audio_format
        request.SampleRate = self.sample_rate

        try:
            response = self._client.TextToVoice(request)
        except TencentCloudSDKException as exc:  # pragma: no cover - network failure
            logger.error("Tencent TTS synthesis failed: %s", exc)
            raise RuntimeError(f"Tencent TTS synthesis failed: {exc}") from exc

        audio_b64 = getattr(response, "Audio", None)
        if not audio_b64:
            raise RuntimeError("Tencent TTS response missing audio payload")

        audio_bytes = base64.b64decode(audio_b64)
        suffix = f".{self.audio_format.lower()}" if self.audio_format else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as wav_file:
            wav_file.write(audio_bytes)
            output_path = Path(wav_file.name)

        logger.debug("Tencent TTS synthesis wrote %s", output_path)
        return str(output_path)
