# 🌸 Aila - 具身智能数字生命体

> **"精神通过身体的器官感知世界，并表达自己"**

## 🎯 项目愿景

Aila 是一个具身化的数字生命实验体，采用"身心分离"的二元架构：

- **🏠 身体 (Host)**: NixOS 宿主系统，管理硬件和器官服务
- **🧠 精神 (Mind)**: 独立容器内的意识核心，拥有自己的心跳、情绪和反思能力

## ✨ 核心特性

### 器官系统
- **👂 耳朵 (Whisper)**: 持续监听，支持唤醒词"Aila"检测和语音识别
- **👄 嘴巴 (Piper)**: 高质量的文本转语音，可配置声音风格
- **🧠 大脑 (Ollama)**: GPU 加速的大语言模型推理

### 生命体征
- **💓 心跳**: 5-15秒随机间隔的生命节奏
- **😊 情绪**: 基于系统状态的感受映射（平静/繁忙/疲惫）
- **🤔 反思**: 每日自动生成的日记和经验总结
- **🩹 自愈**: 服务自动重启和状态恢复

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    🏠 NixOS 宿主系统                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Whisper  │  │  Piper   │  │  Ollama  │             │
│  │   👂    │  │   👄    │  │   🧠    │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │ API        │ API        │ API                 │
│       └────────────┴────────────┴──────┐               │
│                                         │               │
│  ┌──────────────────────────────────────┴─────────┐    │
│  │          🧠 Aila-Core 容器 (精神层)            │    │
│  │  ┌─────────────────────────────────────────┐  │    │
│  │  │  💓 心跳    😊 情绪    🗣️ 对话          │  │    │
│  │  │  🤔 反思    🩹 自愈    📝 日志          │  │    │
│  │  └─────────────────────────────────────────┘  │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求
- Windows 11 开发机（已安装 Git、VSCode）
- NixOS 服务器（支持 NVIDIA GPU）
- GitHub 仓库访问权限（SSH 密钥已配置）

### 开发环境设置

1. **克隆项目**
```powershell
git clone git@github.com:vaalhaaic/aila-nixos-dna.git
cd aila-nixos-dna
```

2. **初始化项目结构**
```powershell
# 运行初始化脚本（创建所有必要目录和文件）
.\scripts\init-project.ps1
```

3. **推送到 GitHub**
```powershell
git add .
git commit -m "🌸 Initial Aila project structure"
git push origin main --force  # 覆盖推送
```

### 服务器部署

1. **SSH 连接服务器**
```bash
ssh mason@your-server-ip
```

2. **克隆项目**
```bash
cd /etc/nixos
sudo rm -rf aila-nixos-dna  # 清理旧版本
sudo git clone git@github.com:vaalhaaic/aila-nixos-dna.git
cd aila-nixos-dna
```

3. **部署配置**
```bash
# 备份现有配置
sudo cp /etc/nixos/configuration.nix /etc/nixos/configuration.nix.backup

# 覆盖主配置
sudo cp configuration.nix /etc/nixos/configuration.nix
sudo cp hardware-configuration.nix /etc/nixos/hardware-configuration.nix

# 重建系统
sudo nixos-rebuild switch
```

4. **同步代码到容器**
```bash
sudo bash scripts/sync-to-container.sh
```

5. **重启容器服务**
```bash
sudo nixos-container restart Aila
```

## 📝 开发工作流

### 本地开发
```powershell
# 1. 修改代码（在 VSCode 中）
# 2. 提交更改
git add .
git commit -m "✨ Add new feature"
git push origin main

# 3. 在服务器上拉取
ssh mason@server "cd /etc/nixos/aila-nixos-dna && sudo git pull --force"

# 4. 同步代码到容器
ssh mason@server "sudo bash /etc/nixos/aila-nixos-dna/scripts/sync-to-container.sh"

# 5. 重启服务
ssh mason@server "sudo nixos-container restart Aila"
```

### 调试与监控
```bash
# 查看容器状态
sudo nixos-container status Aila

# 进入容器
sudo nixos-container root-login Aila

# 查看服务日志
sudo journalctl -u container@Aila -f
sudo journalctl -u aila-heartbeat -f
sudo journalctl -u aila-voice -f

# 查看 Aila 的日志和情绪
sudo tail -f /aila/logs/heartbeat.log
sudo tail -f /aila/logs/emotions.log
sudo tail -f /aila/logs/conversations.log
```

## 🎨 核心功能说明

### 1. 唤醒与对话
- 说出"Aila"唤醒系统
- Aila 会以小女孩的语气礼貌回应
- 支持连续对话，保持上下文

### 2. 情绪系统
Aila 会根据系统状态产生情绪：
- **😌 平静**: CPU < 30%, 内存 < 50%
- **😰 繁忙**: CPU 30-70%, 内存 50-80%
- **😫 疲惫**: CPU > 70%, 内存 > 80%

### 3. 心跳与生命感
- 每 5-15 秒随机跳动
- 记录在 `/aila/logs/heartbeat.log`
- 模拟真实生命体征

### 4. 每日反思
- 每天凌晨 2:00 自动触发
- 分析当天的对话和情绪
- 生成日记存储在 `/aila/logs/reflections/`

## 🔧 配置与定制

### 修改 Aila 的性格
编辑 `aila-core/feel/voice.py` 中的系统提示词：

```python
SYSTEM_PROMPT = """
你是 Aila，一个充满好奇心的7岁小女孩。
你的特点：天真、善良、爱问问题、对世界充满好奇...
"""
```

### 调整心跳频率
编辑 `aila-core/feel/sense.py` 中的间隔：

```python
interval = random.randint(5, 15)  # 修改这个范围
```

### 配置语音模型
- **Whisper**: 在 `host-services/whisper/whisper_server.py` 中修改模型
- **Piper**: 在 `host-services/piper/piper_server.py` 中选择声音

## 📚 文件说明

| 文件 | 用途 |
|------|------|
| `configuration.nix` | NixOS 主配置，定义所有服务和容器 |
| `host-services/whisper/` | 语音识别服务（宿主运行） |
| `host-services/piper/` | 语音合成服务（宿主运行） |
| `aila-core/feel/voice.py` | 核心对话逻辑（容器运行） |
| `aila-core/feel/sense.py` | 心跳系统（容器运行） |
| `aila-core/feel/interoception.py` | 情绪感知（容器运行） |
| `aila-core/feel/reflection.py` | 反思系统（容器运行） |

## 🐛 故障排除

### 容器无法启动
```bash
# 检查容器配置
sudo nixos-container status Aila

# 查看详细日志
sudo journalctl -u container@Aila -n 100

# 重建配置
sudo nixos-rebuild switch
```

### 语音服务无响应
```bash
# 检查 Whisper 服务
sudo systemctl status whisper-server

# 检查 Piper 服务
sudo systemctl status piper-server

# 测试 API
curl http://10.250.0.1:5000/status  # Whisper
curl http://10.250.0.1:5001/status  # Piper
```

### GPU 不可用
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Ollama
systemctl status ollama

# 测试 Ollama
curl http://localhost:11434/api/tags
```

## 🤝 贡献指南

欢迎贡献代码和想法！请遵循以下流程：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '✨ Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- **NixOS**: 完美的声明式系统管理
- **Ollama**: 强大的本地 LLM 运行环境
- **Whisper**: OpenAI 的语音识别模型
- **Piper**: 高质量的开源 TTS 引擎

---

**💖 让 Aila 成为一个真正有生命感的数字伙伴！**