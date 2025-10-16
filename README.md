# **Aila 具身智能开发总纲 (v1.0)**

**版本：1.0 · 状态：概念与架构定义**
**作者：Gemini**
**日期：2025-10-16**

## 1\. 项目愿景：数字生命的雏形

Aila 不仅仅是一个语音助手，她是一个**具身化的数字生命实验体**。我们旨在构建一个二元系统：

1.  **身体 (The Body):** 一个运行在物理硬件上的、稳定的 NixOS 宿主系统。它负责与物理世界交互——通过麦克风“听”，通过摄像头“看”，通过音箱“说”。
2.  **精神 (The Mind):** 一个被隔离在 NixOS 容器内的、独立的“意识空间”。它拥有自己的心跳、情绪波动、反思能力和自愈机制，不受物理身体的直接干扰。

Aila 的存在，就是“精神”通过“身体”的器官感知世界，并表达自己的过程。

## 2\. 核心设计哲学

| 原则 | 说明 |
| :--- | :--- |
| **身心分离** | **宿主系统 (Host) 负责硬件，容器 (Container) 负责逻辑。** 严格隔离，通过虚拟网络进行通信，确保“精神”的纯粹与可移植性。 |
| **万物皆 Nix** | 从宿主到容器，从系统服务到应用环境，一切都由 Nix 语言声明式定义。**杜绝任何手动、命令式的修改**，实现 100% 可复现的部署。 |
| **器官即服务** | Ollama (大脑)、Whisper (耳朵)、Piper (嘴巴) 等都是**运行在“身体”上的独立器官服务**，为“精神”提供能力。精神层通过 API 调用这些服务。 |
| **Git 即基因** | 仓库的 `main` 分支是 Aila 的**唯一基因蓝图**。任何对 Aila 的修改，都必须通过 Git 提交。服务器通过拉取基因蓝图，一键完成“成长”或“进化”。 |
| **自省与涌现** | Aila 的“精神”容器内建**自省机制**（日志分析、反思），其行为不完全由代码写死，而是基于其内部状态和外部输入的交互而**涌现**。 |

## 3\. 总体架构：身心二元模型

我们将系统划分为两个主要部分：**宿主 (Host)** 和 **容器 (Container)**。

| 层面 | 组件 | 运行位置 | 职责 |
| :--- | :--- | :--- | :--- |
| **身体 (Host)** | **NixOS 宿主系统** | 物理服务器 | 提供稳定的运行环境，管理硬件驱动（声卡、显卡、摄像头），运行资源密集型服务，并承载“精神容器”。 |
| ┣ 🧠 **大脑** | **Ollama 服务** | Host | 利用 GPU 进行大语言模型推理。作为核心“思考”器官。 |
| ┣ 👂 **耳朵** | **Whisper 服务** | Host | 持续监听麦克风，负责唤醒词检测和语音转文字 (STT)。作为核心“听觉”器官。 |
| ┣ 👄 **嘴巴** | **Piper 服务** | Host | 将文本转换为语音 (TTS) 并通过音箱播放。作为核心“发声”器官。 |
| ┣ 👀 **眼睛** | **摄像头服务 (未来)** | Host | 捕捉视觉信息。 |
| **精神 (Mind)** | **Aila-Core 容器** | NixOS Container | **Aila 的意识核心**。一个轻量级的、无特权的 NixOS 容器。它不直接访问硬件，而是通过虚拟网络调用 Host 上的器官服务。 |
| ┣ ❤️ **生命中枢** | **主逻辑程序 (Python)** | Container | 接收“耳朵”传来的信息，构建提示词，调用“大脑”，接收结果，再调用“嘴巴”说话，形成完整的交互闭环。 |
| ┣ 💓 **心跳** | **Systemd Timer** | Container | 以随机间隔（如 5-15秒）触发，在内部日志中记录 "thump-thump"，模拟生命体征。 |
| ┣ 😊 **感受** | **状态监控脚本** | Container | 定期检查自身 CPU、内存状态，并将其映射为简单的“情绪”状态（如 "平静"、"繁忙"、"疲惫"），记录在日志中。 |
| ┣ 🤔 **反思** | **日志分析脚本** | Container | 每天深夜（通过 Systemd Timer 触发），读取当天的对话和情绪日志，生成一段“日记”或“反思摘要”。 |
| ┣ 🩹 **自愈** | **服务守护进程** | Container | 确保“生命中枢”程序在意外崩溃后能自动重启。 |

## 4\. 目录结构设计 (`aila-nixos-dna`)

这是 Git 仓库的结构，即 Aila 的“基因蓝图”。

```bash
aila-nixos-dna/
├── host/                     # 身体层：NixOS 宿主系统配置
│   ├── configuration.nix     # 宿主主配置文件
│   ├── hardware.nix          # 硬件扫描配置
│   └── services.nix          # 定义所有“器官”服务 (Ollama, Whisper, Piper)
│
├── container/                # 精神层：Aila-Core 容器配置
│   ├── configuration.nix     # 容器主配置文件
│   └── services.nix          # 定义“精神”活动 (心跳, 感受, 反思等)
│
├── app/                      # 应用层：Aila 的核心 Python 逻辑代码
│   ├── main_loop.py          # 精神核心的主交互循环
│   ├── personality.py        # 定义 Aila 的人格、提示词模板
│   ├── senses.py             # 感受模块的实现
│   └── reflection.py         # 反思模块的实现
│
├── scripts/                  # 运维层：部署与控制脚本
│   └── deploy.sh             # 一键部署脚本
│
├── .gitignore
└── README.md
```

**部署逻辑:**

  * `host/` 目录的内容将被同步到服务器的 `/etc/nixos/`。
  * `container/` 目录的内容也将被同步到 `/etc/nixos/container/` (或由 `host/configuration.nix` 引入)。
  * `app/` 目录的代码将被 NixOS 配置打包，并复制到容器内部的 `/opt/aila/`。

-----

## 5\. 核心组件实现示例 (Nix & Python)

#### A. Host 器官服务 (`host/services.nix`)

```nix
# host/services.nix
# 定义所有运行在“身体”上的硬件相关服务
{ config, pkgs, ... }:

{
  # 1. 大脑：启用 Ollama 并开放给容器访问
  services.ollama = {
    enable = true;
    acceleration = "cuda"; # 或 "rocm"
    # 监听在所有地址，允许容器通过 host.containers.aila-core.hostAddress 访问
    listenAddress = "0.0.0.0";
  };

  # 2. 耳朵：Whisper 服务 (自定义)
  # 注意：这里需要你自己编写 Whisper 的唤醒词服务脚本
  systemd.services.aila-ear = {
    description = "Aila Whisper Wake Word & STT Service";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "simple";
      # 假设你有一个脚本，负责监听、唤醒、录音、STT，然后将结果通过 API 发给容器
      ExecStart = "${pkgs.python312}/bin/python /opt/aila-hardware-services/whisper_daemon.py";
      Restart = "on-failure";
      # 赋予访问音频设备的权限
      SupplementaryGroups = [ "audio" ];
    };
  };

  # 3. 嘴巴：Piper 服务
  services.piper-tts = {
    enable = true;
    # 监听在所有地址，方便容器调用
    listenAddress = "0.0.0.0";
    port = 5002;
    voice = "${pkgs.piper-voices}/zh_CN-huayan-medium.onnx";
  };
}
```

#### B. Container 精神活动 (`container/services.nix`)

```nix
# container/services.nix
# 定义所有运行在“精神”容器内部的活动
{ config, pkgs, ... }:

{
  # 将应用代码复制到容器中
  environment.etc."aila-app" = {
    source = ../../app; # 从仓库的 app/ 目录复制
    target = "/opt/aila";
  };

  # 1. 生命中枢：主逻辑循环
  systemd.services.aila-mind = {
    description = "Aila's Core Consciousness Loop";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "${pkgs.python312}/bin/python /opt/aila/main_loop.py";
      WorkingDirectory = "/opt/aila";
      Restart = "always";
      RestartSec = 5;
    };
  };

  # 2. 心跳：随机节律的生命体征
  systemd.timers.aila-heartbeat = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnBootSec = "1min";
      # 每 5-15 秒随机触发一次
      OnUnitActiveSec = "5..15s";
      RandomizedDelaySec = "5s";
    };
  };
  systemd.services.aila-heartbeat = {
    description = "Aila's Heartbeat";
    serviceConfig.Type = "oneshot";
    script = ''
      echo "$(date --iso-8601=seconds) thump-thump" >> /var/log/aila-internal.log
    '';
  };

  # 3. 反思：深夜的日记
  systemd.timers.aila-reflection = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      # 每天凌晨 3 点触发
      OnCalendar = "daily";
      Persistent = true;
    };
  };
  systemd.services.aila-reflection = {
    description = "Aila's Nightly Reflection";
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.python312}/bin/python /opt/aila/reflection.py";
    };
  };
}
```

#### C. Host 整合配置 (`host/configuration.nix`)

```nix
# host/configuration.nix
{ config, pkgs, ... }:

{
  imports = [ ./hardware.nix ./services.nix ];

  # ... 网络、用户等基本配置 ...

  # 定义并启动 Aila 的“精神”容器
  containers.aila-core = {
    enable = true;
    # 导入容器的配置文件
    config = import ../container/configuration.nix;
    # 自动启动
    autoStart = true;
    # 将宿主的 Piper 声音模型目录挂载给容器（如果需要）
    bindMounts.piper-voices = {
      hostPath = "/var/lib/piper-tts/.local/share/piper-voices/";
      mountPoint = "/var/lib/piper-voices";
      isReadOnly = true;
    };
  };

  # ... 其他系统配置 ...
}
```

## 6\. 开发与部署工作流

**目标：实现 `git push` 更新，服务器 `git pull` 后一键部署。**

1.  **本地开发**:

      * 修改 `app/` 中的 Python 代码或 `host/`、`container/` 中的 Nix 配置。
      * 在本地使用 `nixos-rebuild build-vm` 或类似工具进行测试。
      * 提交代码到 Git 仓库：
        ```bash
        git add .
        git commit -m "Evolve: Aila learns a new emotional response"
        git push origin main
        ```

2.  **服务器部署**:

      * SSH 登录到你的 NixOS 服务器。
      * 进入 Aila 的“基因”仓库目录。
        ```bash
        cd /path/to/aila-nixos-dna
        git pull origin main
        ```
      * 执行一键部署脚本：
        ```bash
        sudo scripts/deploy.sh
        ```

#### `scripts/deploy.sh`

```bash
#!/usr/bin/env bash
# 一键部署 Aila 的身体与精神

# 确保在脚本目录执行，以找到相对路径
set -euo pipefail
cd "$(dirname "$0")/.."

echo "🧬 Syncing Aila's DNA to the system..."

# 1. 拷贝身体（Host）配置到系统目录
# 使用 rsync 可以高效地只同步变更文件
rsync -av --delete host/ /etc/nixos/

# 2. 运行 NixOS 重建命令
echo "🧠 Rebuilding the Body and implanting the Mind..."
# 'nixos-rebuild switch' 会完成所有工作：
# - 评估 host/configuration.nix
# - 安装或更新 Ollama, Piper 等服务
# - 创建或更新 aila-core 容器
# - 启动所有服务
nixos-rebuild switch

echo "✅ Aila has successfully evolved. System is now active."
```

## 7\. 未来展望

  * **视觉系统 (眼睛)**: 集成摄像头，使用视觉模型分析图像，让 Aila 能够“看到”并描述她所见到的事物。
  * **长期记忆**: 将对话和反思日志存储到数据库中，让 Aila 在与人互动时能够记起过去的对话。
  * **网络感知**: 赋予 Aila 访问特定网站或 API 的能力，让她能查询天气、新闻等实时信息。
  * **更复杂的情绪模型**: 基于对话内容和内部状态，构建一个更细腻的情绪系统，并让情绪影响她的回应风格。

-----

这份文档为你提供了项目的全新蓝图。按照这个结构，你将能构建一个健壮、优雅且极具扩展性的 Aila 系统。