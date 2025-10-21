"""Runtime orchestrator for Aila."""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from typing import Any

from ..core import MindPipeline, PerceptionRouter, Planner
from ..interfaces.asr import TencentASRClient
from ..interfaces.llm import LLMClient
from ..interfaces.speech import SpeechInterface, TencentTTSClient


logger = logging.getLogger("aila.orchestrator")


def _parse_int(value: Any, *, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc


@dataclass
class Orchestrator:
    mind: MindPipeline

    def process_audio(self, audio_path: str) -> str:
        logger.debug("Processing audio %s", audio_path)
        return self.mind.handle_audio(audio_path)

    def process_text(self, text: str) -> str:
        logger.debug("Processing text: %s", text)
        return self.mind.handle_text(text)


def build_pipeline(tts_client: TencentTTSClient, asr_client: TencentASRClient) -> MindPipeline:
    perception = PerceptionRouter(recognizer=asr_client)
    llm = LLMClient()
    planner = Planner(llm=llm)
    speech = SpeechInterface(tts=tts_client)
    return MindPipeline(perception=perception, planner=planner, speech=speech)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", help="Path to WAV/PCM file for recognition")
    parser.add_argument("--text", help="Text prompt bypassing ASR")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--tts-region",
        default=os.getenv("TENCENT_TTS_REGION", "ap-beijing"),
        help="Tencent Cloud region for TTS",
    )
    parser.add_argument(
        "--tts-voice-type",
        default=os.getenv("TENCENT_TTS_VOICE_TYPE", "602003"),
        help="Tencent Cloud voice type (default 爱小悠 602003)",
    )
    parser.add_argument(
        "--tts-speed",
        default=os.getenv("TENCENT_TTS_SPEED", "0"),
        help="Speech speed [-2,2]",
    )
    parser.add_argument(
        "--tts-volume",
        default=os.getenv("TENCENT_TTS_VOLUME", "0"),
        help="Speech volume [-2,2]",
    )
    parser.add_argument(
        "--tts-format",
        default=os.getenv("TENCENT_TTS_FORMAT", "wav"),
        help="Output audio format (wav/mp3/pcm)",
    )
    parser.add_argument(
        "--tts-sample-rate",
        default=os.getenv("TENCENT_TTS_SAMPLE_RATE", "16000"),
        help="Sample rate in Hz",
    )
    parser.add_argument(
        "--asr-region",
        default=os.getenv("TENCENT_ASR_REGION", "ap-beijing"),
        help="Tencent Cloud region for ASR",
    )
    parser.add_argument(
        "--asr-engine",
        default=os.getenv("TENCENT_ASR_ENGINE", "16k_zh"),
        help="Tencent ASR engine model (e.g. 16k_zh)",
    )
    parser.add_argument(
        "--asr-format",
        default=os.getenv("TENCENT_ASR_FORMAT", "wav"),
        help="Input audio format (wav/mp3/silk etc.)",
    )
    parser.add_argument(
        "--asr-punctuation",
        default=os.getenv("TENCENT_ASR_ENABLE_PUNCTUATION", "1"),
        help="Enable punctuation (1 or 0)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper())

    secret_id = os.getenv("TENCENT_SECRET_ID")
    secret_key = os.getenv("TENCENT_SECRET_KEY")
    if not secret_id or not secret_key:
        raise RuntimeError(
            "TENCENT_SECRET_ID and TENCENT_SECRET_KEY must be set (see system/etc/aila/env.d/tencent.conf)."
        )

    voice_type = _parse_int(args.tts_voice_type, name="tts_voice_type")
    speed = _parse_int(args.tts_speed, name="tts_speed")
    volume = _parse_int(args.tts_volume, name="tts_volume")
    sample_rate = _parse_int(args.tts_sample_rate, name="tts_sample_rate")
    enable_punctuation = args.asr_punctuation not in {"0", "false", "False"}

    tts_client = TencentTTSClient(
        secret_id=secret_id,
        secret_key=secret_key,
        region=args.tts_region,
        voice_type=voice_type,
        speed=speed,
        volume=volume,
        audio_format=args.tts_format,
        sample_rate=sample_rate,
    )

    asr_client = TencentASRClient(
        secret_id=secret_id,
        secret_key=secret_key,
        region=args.asr_region,
        engine_model=args.asr_engine,
        audio_format=args.asr_format,
        enable_punctuation=enable_punctuation,
    )

    mind = build_pipeline(tts_client=tts_client, asr_client=asr_client)
    orchestrator = Orchestrator(mind=mind)

    if args.audio:
        result = orchestrator.process_audio(args.audio)
        print(result)
    elif args.text:
        result = orchestrator.process_text(args.text)
        print(result)
    else:
        parser.error("Provide either --audio or --text")


if __name__ == "__main__":
    main()
