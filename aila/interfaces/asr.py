"""Speech recognition clients."""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass, field
from pathlib import Path

from tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


logger = logging.getLogger(__name__)


class SpeechRecognitionClient:
    """Abstract base for speech recognition."""

    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError


@dataclass
class TencentASRClient(SpeechRecognitionClient):
    """Wraps Tencent Cloud SentenceRecognition API."""

    secret_id: str
    secret_key: str
    region: str = "ap-beijing"
    engine_model: str = "16k_zh"
    audio_format: str = "wav"
    enable_punctuation: bool = True
    _client: asr_client.AsrClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        cred = credential.Credential(self.secret_id, self.secret_key)
        self._client = asr_client.AsrClient(cred, self.region)
        logger.info(
            "Initialized Tencent ASR client (region=%s, model=%s, format=%s)",
            self.region,
            self.engine_model,
            self.audio_format,
        )

    def transcribe(self, audio_path: str) -> str:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode("utf-8")

        request = models.SentenceRecognitionRequest()
        request.EngineModelType = self.engine_model
        request.AudioFormat = self.audio_format
        request.Data = encoded
        request.DataLen = len(data)
        request.EnablePunctuation = 1 if self.enable_punctuation else 0

        try:
            response = self._client.SentenceRecognition(request)
        except TencentCloudSDKException as exc:  # pragma: no cover - network failure
            logger.error("Tencent ASR transcription failed: %s", exc)
            raise RuntimeError(f"Tencent ASR transcription failed: {exc}") from exc

        result = getattr(response, "Result", None)
        if not result:
            raise RuntimeError("Tencent ASR response missing Result field")

        logger.debug("Tencent ASR transcription completed for %s", path)
        return result
