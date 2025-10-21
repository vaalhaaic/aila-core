# 📝 修改后的 README.md

```markdown
# Aila Core - Embodied AI Robot System

基于 Ubuntu 的 Aila 具身智能机器人核心系统，实现 GPU 加速推理、分层式服务编排以及自动化部署。本仓库将系统划分为基础系统、服务器官、核心认知、自动化脚本、部署映射与文档六个层次，便于在开发端与生产端保持一致的交付质量。

## 🤖 项目概述

Aila Core 是一个模块化的具身智能机器人系统，具备以下核心能力：

- 🧠 **多模态感知**：视觉、听觉、触觉信息融合
- 💬 **自然语言交互**：基于大语言模型的对话能力
- 🦾 **运动控制**：精准的机器人动作规划与执行
- 🔄 **持续学习**：在线学习与记忆系统
- 📊 **实时监控**：系统健康状态与性能指标

## 📁 仓库目录结构

```text
aila-core/
├── aila/          # 核心认知运行时（Python 包）
│   ├── perception/    # 感知模块
│   ├── cognition/     # 认知与推理
│   ├── planning/      # 规划与决策
│   ├── memory/        # 记忆系统
│   └── models/        # 预训练模型（不纳入版本控制）
├── deploy/        # 基于 rsync 的部署调度器与映射
│   ├── deploy.py      # 部署脚本
│   └── mapping.yaml   # 路径映射配置
├── docs/          # 架构与运维文档
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── scripts/       # Ubuntu 主机上的 DevOps 脚本
│   ├── install_dependencies.sh
│   ├── deploy_to_host.sh
│   └── run_aila.sh
├── services/      # 本地辅助服务定义（如 monitor），语音能力改用云端 API
│   └── monitor/       # 监控服务
└── system/        # Ubuntu 主机级配置片段
    └── etc/aila/env.d/  # 环境变量配置
```

## 🔧 平台要求

- **操作系统**: Ubuntu 24.04.3 LTS（桌面或服务器版本）
- **GPU**: NVIDIA GPU + 驱动版本 550+
- **运行时**: Python 3.12、Node.js 20、Docker 27
- **服务管理**: systemd

## 🚀 快速开始

### 1. SSH 密钥配置验证

本仓库使用 SSH 进行 Git 操作。验证你的 SSH 连接：

```bash
ssh -T git@github.com
```

✅ 成功输出示例：`Hi vaalhaaic! You've successfully authenticated, but GitHub does not provide shell access.`

❌ 如果失败，请添加 SSH 密钥到 ssh-agent：

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519  # 或你的私钥路径
```

### 2. 克隆仓库

#### 在 Windows 开发机（F盘）

```bash
# 打开 Git Bash 或 PowerShell
cd F:\MasonsDatabase\Documents\GitHub

# 克隆仓库
git clone git@github.com:vaalhaaic/aila-core.git

# 进入项目目录
cd aila-core

# 验证远程仓库
git remote -v
# 应该输出：
# origin  git@github.com:vaalhaaic/aila-core.git (fetch)
# origin  git@github.com:vaalhaaic/aila-core.git (push)
```

#### 在部署服务器（Ubuntu）

```bash
# SSH 登录到服务器
ssh user@your-server-ip

# 克隆仓库到用户目录
git clone git@github.com:vaalhaaic/aila-core.git ~/aila-core
cd ~/aila-core
```

### 3. 初始化开发环境

```bash
# 安装系统依赖
sudo bash scripts/install_dependencies.sh

# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装 Python 依赖（假设有 requirements.txt）
pip install -r requirements.txt

# 检查环境片段（密钥保持占位符，部署后再填写）
cat system/etc/aila/env.d/xunfei.conf
cat system/etc/aila/env.d/tencent.conf
```

## 📤 Git 工作流程

### 日常开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/voice-recognition

# 2. 进行代码修改
# ... 编写代码 ...

# 3. 查看修改状态
git status

# 4. 添加修改的文件
git add aila/perception/voice.py
# 或添加所有修改
git add .

# 5. 提交更改
git commit -m "feat: add voice recognition module"

# 6. 推送到 GitHub
git push -u origin feature/voice-recognition
```

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构代码
- `test:` 添加测试
- `chore:` 构建/工具链更新

### 分支策略

- `main`: 生产稳定版本
- `develop`: 开发主分支
- `feature/*`: 功能开发分支
- `hotfix/*`: 紧急修复分支

## 🏗️ 开发与部署全流程

### 1. 初始化环境

```bash
chmod +x scripts/install_dependencies.sh
sudo ./scripts/install_dependencies.sh

python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置云端密钥（OpenRouter & 腾讯 TTS）

1. **部署完成后再写入真实密钥：**
   - `/etc/aila/env.d/xunfei.conf` → 设置 `XUNFEI_APP_ID` / `XUNFEI_API_KEY` / `XUNFEI_API_SECRET`
   - `/etc/aila/env.d/tencent.conf` → 设置 `TENCENT_SECRET_ID` / `TENCENT_SECRET_KEY`

   以上文件已在仓库中提供模板（默认值为 `changeme`），请勿将真实密钥提交到版本库。

2. **本地调试临时导出环境变量：**

   ```powershell
   # Windows PowerShell
   setx XUNFEI_APP_ID "你的讯飞AppID"
   setx XUNFEI_API_KEY "你的讯飞APIKey"
   setx XUNFEI_API_SECRET "你的讯飞APISecret"
   setx TENCENT_SECRET_ID "你的腾讯SecretId"
   setx TENCENT_SECRET_KEY "你的腾讯SecretKey"
   ```

   ```bash
   # Linux / macOS
   export XUNFEI_APP_ID="你的讯飞AppID"
   export XUNFEI_API_KEY="你的讯飞APIKey"
   export XUNFEI_API_SECRET="你的讯飞APISecret"
   export TENCENT_SECRET_ID="你的腾讯SecretId"
   export TENCENT_SECRET_KEY="你的腾讯SecretKey"
   ```

3. **可选参数：**

   ```bash
   # 讯飞星火模型参数
   export XUNFEI_TEMPERATURE="0.7"
   export XUNFEI_MAX_TOKENS="2048"

   # 腾讯 TTS 语音/语速/格式覆写
   export TENCENT_TTS_REGION="ap-shanghai"
   export TENCENT_TTS_VOICE_TYPE="101001"
   export TENCENT_TTS_SPEED="0"
   export TENCENT_TTS_VOLUME="0"
   export TENCENT_TTS_FORMAT="wav"
   export TENCENT_TTS_SAMPLE_RATE="16000"
   ```

### 3. 云端语音能力调用示例

#### 3.1 语音合成（腾讯云爱小悠 602003）

```python
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import tts_client, models


def text_to_speech(text: str) -> bytes:
    cred = credential.Credential("你的SECRET_ID", "你的SECRET_KEY")
    client = tts_client.TtsClient(cred, "ap-beijing")

    req = models.TextToVoiceRequest()
    req.Text = text
    req.VoiceType = 602003  # 爱小悠
    req.Speed = 0
    req.Volume = 0
    req.Format = "wav"

    resp = client.TextToVoice(req)
    return resp.Audio


if __name__ == "__main__":
    binary = text_to_speech("你好，我是爱小悠，很高兴为你服务～")
    with open("ai_xiaoyou_test.wav", "wb") as fh:
        fh.write(binary)
```

#### 3.2 语音转文字（腾讯云 16k_zh）

```python
from base64 import b64encode
from pathlib import Path
from tencentcloud.common import credential
from tencentcloud.asr.v20190614 import asr_client, models


def speech_to_text(path: str) -> str:
    cred = credential.Credential("你的SECRET_ID", "你的SECRET_KEY")
    client = asr_client.AsrClient(cred, "ap-beijing")

    req = models.SentenceRecognitionRequest()
    req.EngineModelType = "16k_zh"
    req.AudioFormat = "wav"
    data = Path(path).read_bytes()
    req.Data = b64encode(data).decode()
    req.DataLen = len(data)

    resp = client.SentenceRecognition(req)
    return resp.Result
```

#### 3.3 星火大模型（Python 调用）

```python
import base64
import hashlib
import hmac
import time
import requests
from email.utils import formatdate
from urllib.parse import urlparse


def call_xinghuo(prompt: str) -> str:
    app_id = "你的APPID"
    api_key = "你的APIKey"
    api_secret = "你的APISecret"
    api_url = "https://spark-api-open.xf-yun.com/v2/chat/completions"

    parsed = urlparse(api_url)
    host = parsed.netloc
    path = parsed.path
    date_header = formatdate(time.time(), usegmt=True)
    signature_origin = f"host: {host}\ndate: {date_header}\nPOST {path} HTTP/1.1"
    signature_sha = hmac.new(api_secret.encode(), signature_origin.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode()).decode()

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "Host": host,
        "Date": date_header,
    }
    payload = {
        "app_id": app_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
    data = resp.json()
    return data["choices"][0]["message"]["content"]
```

### 4. 本地开发与测试

```bash
# 确保 XUNFEI_APP_ID / XUNFEI_API_KEY / XUNFEI_API_SECRET / TENCENT_SECRET_ID / TENCENT_SECRET_KEY 已在当前会话可见
source venv/bin/activate

# 运行编排器（文本输入示例）
python -m aila.runtime.orchestrator --text "你好，Aila！"

# 运行测试
pytest tests/
```

### 5. 部署前检查

```bash
# 检查部署映射配置
cat deploy/mapping.yaml

# 干运行（不实际部署，仅预览）
python deploy/deploy.py --dry-run
```

### 6. 部署到 Ubuntu 目标主机

```bash
# 同步代码与配置
bash scripts/deploy_to_host.sh production-server

# 在目标主机验证环境变量（填入后）
ssh user@production-server
sudo cat /etc/aila/env.d/tencent.conf
sudo cat /etc/aila/env.d/xunfei.conf

# 使用虚拟环境运行编排器
source /opt/aila/core/venv/bin/activate  # 按需调整路径
python -m aila.runtime.orchestrator --text "系统自检完成"
```

### 7. 持续集成与回滚

```bash
# 打标签发布版本
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 回滚到指定版本
git checkout v1.0.0
bash scripts/deploy_to_host.sh production-server
```

## 🔍 关键目录说明

| 目录 | 说明 |
|------|------|
| `aila/` | Python 核心运行时，包含感知、认知、规划、记忆等模块 |
| `services/` | 独立服务封装（Monitor 等），包含 systemd 单元文件 |
| `scripts/` | DevOps 自动化脚本：安装、部署、诊断 |
| `deploy/` | 部署工具，基于 rsync 同步代码与配置 |
| `docs/` | 项目文档：架构设计、API 文档、运维手册 |
| `system/` | Ubuntu 主机配置片段（/etc 对应文件） |

## ⚠️ 常见检查项

- ✅ 推送前执行 `git status` 确保工作区干净
- ✅ 运行 `scripts/run_aila.sh` 验证核心流程
- ✅ 检查服务日志：`journalctl -u <service-name>`
- ✅ 大文件（模型）已添加到 `.gitignore`
- ✅ 敏感信息（API Keys）仅存储在 `.env` 文件中，不提交到仓库

## 📚 文档索引

- [系统架构](docs/architecture.md)
- [API 文档](docs/api.md)
- [部署手册](docs/deployment.md)
- [开发指南](docs/development.md)

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 📧 联系方式

- **项目仓库**: https://github.com/vaalhaaic/aila-core
- **问题反馈**: https://github.com/vaalhaaic/aila-core/issues
- **开发者**: Mason

---

**⚡ Aila Core - Empowering Embodied Intelligence**
```
