#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_USER="${SERVICE_USER:-$(whoami)}"

WHISPER_ROOT="${WHISPER_ROOT:-/opt/aila/whisper.cpp}"
WHISPER_MODEL_SIZE="${WHISPER_MODEL_SIZE:-small}"
WHISPER_PORT="${WHISPER_PORT:-9081}"

COQUI_ROOT="${COQUI_ROOT:-/opt/aila/coqui}"
COQUI_MODEL_NAME="${COQUI_MODEL_NAME:-tts_models/zh-CN/baker/tacotron2-DDC-GST}"
COQUI_PORT="${COQUI_PORT:-9082}"
COQUI_SPEAKER_ID="${COQUI_SPEAKER_ID:--1}"
COQUI_SAMPLE_RATE="${COQUI_SAMPLE_RATE:-22050}"
COQUI_WARMUP_TEXT="${COQUI_WARMUP_TEXT:-你好，欢迎使用 Aila 的语音服务。}"
COQUI_ENABLE_CUDA="${COQUI_ENABLE_CUDA:-true}"

SYSTEMD_DIR="/etc/systemd/system"
COQUI_CONFIG_DIR="/etc/aila-coqui"

log() {
  echo -e "\033[1;34m[deploy]\033[0m $*"
}

bool_literal() {
  if [[ "$1" =~ ^(1|true|TRUE|yes|YES)$ ]]; then
    echo "True"
  else
    echo "False"
  fi
}

ensure_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command '$1' is not available." >&2
    exit 1
  fi
}

log "Using service user: ${SERVICE_USER}"

# -----------------------------------------------------------------------------
# 1. Install system dependencies
# -----------------------------------------------------------------------------
log "Installing system dependencies (sudo required)…"
sudo apt-get update -y
sudo apt-get install -y \
  git build-essential cmake ninja-build pkg-config \
  libsndfile1 libasound2-dev ffmpeg sox \
  python3 python3-pip python3-venv python3-dev \
  espeak-ng espeak-ng-data \
  rsync wget curl

# -----------------------------------------------------------------------------
# 2. Setup whisper.cpp (CUDA build)
# -----------------------------------------------------------------------------
log "Preparing whisper.cpp at ${WHISPER_ROOT}"
sudo mkdir -p "${WHISPER_ROOT}"
sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" "${WHISPER_ROOT}"

if [ ! -d "${WHISPER_ROOT}/.git" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git "${WHISPER_ROOT}"
else
  git -C "${WHISPER_ROOT}" pull --ff-only
fi

cmake -S "${WHISPER_ROOT}" -B "${WHISPER_ROOT}/build" \
  -DWHISPER_CUBLAS=ON \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "${WHISPER_ROOT}/build" --target whisper-server --parallel

log "Downloading whisper.cpp model: ${WHISPER_MODEL_SIZE}"
MODELS_DIR="${WHISPER_ROOT}/models"
mkdir -p "${MODELS_DIR}"
MODELS_DIR="${MODELS_DIR}" bash "${PROJECT_ROOT}/services/whisper/scripts/install_model.sh" "${WHISPER_MODEL_SIZE}"

WHISPER_MODEL_PATH="${MODELS_DIR}/ggml-${WHISPER_MODEL_SIZE}.bin"
if [ ! -f "${WHISPER_MODEL_PATH}" ]; then
  echo "Expected Whisper model not found at ${WHISPER_MODEL_PATH}" >&2
  exit 1
fi

# -----------------------------------------------------------------------------
# 3. Setup Coqui TTS service
# -----------------------------------------------------------------------------
log "Preparing Coqui TTS at ${COQUI_ROOT}"
sudo mkdir -p "${COQUI_ROOT}"
sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" "${COQUI_ROOT}"

python3 -m venv "${COQUI_ROOT}/venv"
source "${COQUI_ROOT}/venv/bin/activate"
pip install --upgrade pip
pip install "TTS==0.22.0" fastapi uvicorn[standard] soundfile

PY_USE_CUDA=$(bool_literal "${COQUI_ENABLE_CUDA}")
log "Downloading Coqui TTS model: ${COQUI_MODEL_NAME}"
"${COQUI_ROOT}/venv/bin/python" - <<PY
from TTS.utils.synthesizer import Synthesizer
synth = Synthesizer.from_pretrained(model_name="${COQUI_MODEL_NAME}", use_cuda=${PY_USE_CUDA})
try:
    synth.tts("${COQUI_WARMUP_TEXT}")
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"Failed to warm up Coqui model: {exc}") from exc
PY
deactivate

log "Syncing Coqui runtime sources"
rsync -a "${PROJECT_ROOT}/services/coqui/main/" "${COQUI_ROOT}/"

sudo mkdir -p "${COQUI_CONFIG_DIR}"
if [[ -z "${COQUI_SPEAKER_ID}" || "${COQUI_SPEAKER_ID}" == "-1" ]]; then
  COQUI_SPEAKER_FIELD="null"
else
  COQUI_SPEAKER_FIELD="\"${COQUI_SPEAKER_ID}\""
fi
sudo tee "${COQUI_CONFIG_DIR}/config.yaml" >/dev/null <<EOF
model_name: "${COQUI_MODEL_NAME}"
listen_host: "0.0.0.0"
listen_port: ${COQUI_PORT}
use_cuda: ${PY_USE_CUDA}
speaker_id: ${COQUI_SPEAKER_FIELD}
sample_rate: ${COQUI_SAMPLE_RATE}
warmup_text: "${COQUI_WARMUP_TEXT}"
EOF

# -----------------------------------------------------------------------------
# 4. Install systemd services
# -----------------------------------------------------------------------------
log "Writing systemd unit: whisper.service"
sudo tee "${SYSTEMD_DIR}/whisper.service" >/dev/null <<UNIT
[Unit]
Description=Whisper.cpp Speech-to-Text Service
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${WHISPER_ROOT}
Environment=GGML_CUDA=1
ExecStart=${WHISPER_ROOT}/build/bin/whisper-server \\
  --model ${WHISPER_MODEL_PATH} \\
  --host 0.0.0.0 \\
  --port ${WHISPER_PORT} \\
  --language auto \\
  --threads $(nproc)
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

log "Writing systemd unit: coqui.service"
sudo tee "${SYSTEMD_DIR}/coqui.service" >/dev/null <<UNIT
[Unit]
Description=Coqui TTS Service
After=network.target sound.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${COQUI_ROOT}
EnvironmentFile=/etc/aila/env.d/coqui.conf
ExecStart=${COQUI_ROOT}/venv/bin/python -m server --config ${COQUI_CONFIG_DIR}/config.yaml
Restart=on-failure
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
UNIT

log "Reloading systemd and enabling services"
sudo systemctl daemon-reload
sudo systemctl enable --now whisper.service
sudo systemctl enable --now coqui.service

# -----------------------------------------------------------------------------
# 5. Summary
# -----------------------------------------------------------------------------
echo
log "部署完成："
echo "  • Whisper.cpp 监听端口: ${WHISPER_PORT} (service: whisper.service, status: $(systemctl is-active whisper.service))"
echo "  • Coqui TTS    监听端口: ${COQUI_PORT} (service: coqui.service, status: $(systemctl is-active coqui.service))"
echo
echo "验证示例："
echo "  curl http://localhost:${WHISPER_PORT}/health"
echo "  curl -X POST http://localhost:${COQUI_PORT}/synthesize -H 'Content-Type: application/json' -d '{\"text\":\"你好，欢迎使用 Coqui TTS!\"}' --output out.wav"
echo "  aplay out.wav"
