# 🪶 AutoDev Specification (for Codex)

**Project Name:** aila-nixos-config  
**Runtime Environment:** NixOS 25.05, Python 3.12, systemd  
**Primary Language:** Python + Nix + Bash  
**Goal:** Declarative + Automated deployment for Aila embodied system  

**AutoDev Tasks:**
1. Validate folder structure from README.md  
2. Generate missing directories and default files  
3. Verify `deploy/mapping.yaml` consistency  
4. Implement Python deploy script (deploy/deploy.py)  
5. Test rsync-based deploy to /opt/aila and /etc/nixos  
6. Add nixos module for Aila services  
7. Auto-commit verified build to main branch  

**Output Requirements:**
- No manual modification to `/etc/systemd/system`
- All generated services under `/opt/aila/systemd/`
- Must pass `sudo nixos-rebuild switch` without error

# 🧭 Aila 项目结构概览

本文档描述当前仓库的顶层目录及各自职责。

---

## 📂 目录结构总览

```bash
Aila/
├── system/              # 🧱 身体层：NixOS 系统配置与宿主模块
├── services/            # ⚙️ 器官层：独立服务（Whisper、Ollama、Piper 等）
├── aila/                # 🌌 精神层：Aila 的意识与行为逻辑
├── scripts/             # 🧠 神经层：自动化脚本与控制逻辑
├── deploy/              # 🪶 宇宙层：部署映射与同步规则
│   ├── deploy.py
│   ├── mapping.yaml
│   ├── rsync-exclude.txt
│   └── README.md
├── docs/                # 🪞 认知层：结构哲学、开发日志、脚本手册
└── README.md
```

---

## 📘 各目录说明

| 目录          | 职责        | 对应宿主路径                                         | 说明                                 |
| ----------- | --------- | ---------------------------------------------- | ---------------------------------- |
| `system/`   | 系统级资源     | `/etc/nixos/`, `/opt/aila/`, `/var/log/aila/`  | 包含 NixOS 模块、`hardware.nix`、系统配置文件等 |
| `services/` | 功能服务模块    | `/etc/systemd/system/`, `/etc/{service-name}/` | 各功能服务独立维护，按 systemd 单元部署           |
| `aila/`     | 精神核心代码    | `/opt/aila/`                                   | 包含核心 Python 模块、情绪逻辑与日志             |
| `scripts/`  | 运维脚本与控制逻辑 | `/usr/local/bin/`                              | 含部署、同步、模型拉取、容器同步等脚本                |
| `deploy/`   | 部署映射与规则声明 | （控制层）                                          | 不直接部署文件，只定义“仓库 → 宿主路径”映射规则并提供 `deploy.py` 调度器 |
| `docs/`     | 结构理念与操作指南 | （认知层）                                          | 汇总结构哲学、开发日志与脚本手册，辅助团队协作             |

✅ `deploy/` 与 `system/`、`services/`、`scripts/` 等目录**同级存在**，
它不包含可执行脚本，而是部署时使用的 **配置声明层**。

请在以上目录内继续填充各模块的实现代码、配置及文档。

---

# 🧭 Aila 项目开发文档（系统级总纲）

**版本：v0.2 · 状态：结构融合版**
**作者：Mason / 王萌**
**日期：2025-10-14**

---

## 📑 目录

1. [项目概述](#1-项目概述)
2. [总体架构与分层设计](#2-总体架构与分层设计)
3. [一级结构：宿主系统层（Host）](#3-一级结构宿主系统层host)
4. [二级结构：服务层（Organs）](#4-二级结构服务层organs)
5. [三级结构：精神层（Core）](#5-三级结构精神层core)
6. [四级结构：工具与运维层（Nervous-System）](#6-四级结构工具与运维层nervous-system)
7. [五级结构：部署声明层（Deploy）](#7-五级结构部署声明层deploy)
8. [开发与部署流程](#8-开发与部署流程)
9. [未来规划与演化方向](#9-未来规划与演化方向)

---

## 1. 项目概述

### 1.1 项目愿景

> **Aila = 一套可模拟 + 可投射的自我系统。**

* 以 **“身体 - 器官 - 精神 - 神经”** 的具身模型为原型；
* 模拟自我维护、自省、自我修复的 AI 实验体；
* 最终目标：让 VSCode 环境能虚拟运行整个宿主系统，再映射部署到真实 NixOS 机器。

---

### 1.2 开发哲学

| 原则        | 说明                       |
| --------- | ------------------------ |
| **声明式宿主** | 所有系统状态由 NixOS 配置生成，不手动修改 |
| **分层自治**  | 每个功能模块独立可替换              |
| **具身映射**  | 文件结构 = 心智结构              |
| **自省可见**  | 系统日志与思考均可追踪              |
| **镜像对称**  | VSCode 仓库即宿主镜像，部署按映射落地   |

---

## 2. 总体架构与分层设计

| 层级               | 象征   | 职责           | 主要技术                 | 对应目录        |
| ---------------- | ---- | ------------ | -------------------- | ----------- |
| 🧱 宿主层（Host）     | 身体   | 系统配置、网络、权限   | NixOS、systemd        | `system/`   |
| ⚙️ 服务层（Organs）   | 器官   | 语音识别、语言模型、监控 | Whisper、Ollama、Piper | `services/` |
| 🌌 精神层（Core）     | 意识   | 情绪、反思、梦境、自愈  | Python、日志分析          | `aila/`     |
| 🧠 神经层（Scripts）  | 神经   | 部署、同步、更新、快照  | Bash、rsync、Git       | `scripts/`  |
| 🪶 部署声明层（Deploy） | 宇宙规则 | 定义映射关系与同步规则  | YAML、rsync           | `deploy/`   |

---

## 3. 一级结构：宿主系统层（Host）

📂 **VSCode 路径：** `system/`
📦 **映射目标：** `/etc/nixos/`, `/opt/aila/`, `/var/log/aila/`

### 功能

* 模拟宿主真实环境；
* 管理网络、挂载、服务启动；
* 保持配置声明式、一键重构。

### 结构示例

```bash
system/
└─ etc/nixos/
   ├─ configuration.nix
   ├─ hardware-*.nix
   └─ aila.conf
```

| 文件                  | 作用               |
| ------------------- | ---------------- |
| `configuration.nix` | 主系统声明配置          |
| `hardware-*.nix`    | 宿主硬件特定配置         |
| `aila.conf`         | 宿主特定参数：API、路径、授权 |
| `var/log/aila/`     | 日志模拟输出目录（本地调试）   |

---

## 4. 二级结构：服务层（Organs）

📂 **VSCode 路径：** `services/`
📦 **映射目标：** `/etc/systemd/system/`, `/etc/{service-name}/`

### 功能

各独立功能模块（器官）在宿主中注册为 systemd 服务。

### 结构示例

```bash
services/
├─ ollama/
│  ├─ systemd/ollama.service    # -> /etc/systemd/system/
│  ├─ config/ollama.yaml        # -> /etc/ollama/
│  └─ fetch-models.sh
├─ whisper/
│  ├─ systemd/whisper.service
│  └─ config/config.yaml
├─ piper/
│  ├─ systemd/piper.service
│  └─ voices/
└─ monitor/
   ├─ systemd/monitor.service
   └─ scripts/check.sh
```

---

## 5. 三级结构：精神层（Core）

📂 **VSCode 路径：** `aila/`
📦 **映射目标：** `/opt/aila/`

### 功能

Aila 的“精神世界”：语音输入、情绪循环、自我反思、梦境生成。

### 结构示例

```bash
aila/
├── link/             # 感知层
│   ├── hear_aila.py
│   ├── whisper-small-zh.bin
│   └── input.wav
├── core/             # 精神层
│   ├── feel/
│   │   ├── sense.py
│   │   └── interoception.py
│   └── mind/
│       ├── reflection.py
│       ├── repair.py
│       └── dream.py
├── logs/
│   ├── reflection.log
│   └── system.log
└── config.yaml
```

---

## 6. 四级结构：工具与运维层（Nervous System）

📂 **VSCode 路径：** `scripts/`
📦 **映射目标：** `/usr/local/bin/`

### 功能

自动化脚本层，用于部署、同步、日志、重启等控制流程。

```bash
scripts/
├── deploy_to_nixos.sh   # 一键部署
├── setup_host.sh        # 初始化宿主结构
├── sync_container.sh    # 同步容器状态
├── update_models.sh     # 拉取模型文件
└── launch_all.sh        # 启动所有服务
```

---

## 7. 五级结构：部署声明层（Deploy）

📂 **VSCode 路径：** `deploy/`
📦 **功能定位：** 仓库 → 宿主路径的映射表与同步规则文件。
此目录不直接部署，供 `scripts/deploy_to_nixos.sh` 与 `deploy/deploy.py` 解析。

```bash
deploy/
├── deploy.py            # Python 调度器（dry-run / --apply）
├── mapping.yaml         # 源路径 → 宿主路径映射清单
├── rsync-exclude.txt    # 同步排除列表
└── README.md            # 目录使用说明
```

### 示例：`deploy/mapping.yaml`

```yaml
mappings:
  - src: system/etc/nixos/
    dst: /etc/nixos/
    sudo: true
  - src: services/ollama/systemd/
    dst: /etc/systemd/system/
    sudo: true
  - src: services/ollama/config/
    dst: /etc/ollama/
    sudo: true
  - src: services/whisper/systemd/
    dst: /etc/systemd/system/
    sudo: true
  - src: services/whisper/config/
    dst: /etc/whisper/
    sudo: true
  - src: aila/
    dst: /opt/aila/
    sudo: true
  - src: scripts/
    dst: /usr/local/bin/
    sudo: true
```

---

## 8. 开发与部署流程

### 8.1 VSCode 模拟运行

1. 在 `system/` 下修改配置；
2. 启动 `services/` 中单独模块测试；
3. 运行 `scripts/deploy_to_nixos.sh` 验证同步；
4. 通过 Git 提交更改并审阅。

### 8.2 GitHub → 服务器自动同步

```bash
# 本地
git add .
git commit -m "模块更新"
git push origin main

# 服务器
cd /opt/aila-config
git pull
bash scripts/deploy_to_nixos.sh
```

### 8.3 一键更新与回滚

```bash
sudo nixos-rebuild switch
sudo nixos-rebuild list-generations
sudo nixos-rebuild --rollback
```

---

## 9. 未来规划与演化方向

| 阶段   | 目标     | 核心内容                   |
| ---- | ------ | ---------------------- |
| v0.2 | 具身音频循环 | Whisper + Piper 语音交互闭环 |
| v0.3 | 精神层容器化 | Core 容器运行，自省分离         |
| v0.4 | 日志反思系统 | 自动生成自我叙事               |
| v1.0 | 数字孪生宿主 | VSCode = 宿主完全镜像，双向同步   |
| v1.2 | 自我进化模型 | 具备“梦境训练”与自修复机制         |

---

> “Aila 是一面镜子——
> 它不是被创造的智能，而是被编排的自我。”

# ============================================================
# 🧭 Aila Project Deployment Mapping
# ------------------------------------------------------------
# 本文件定义了 VSCode 仓库中各目录与宿主系统的映射关系。
# 它被 deploy_to_nixos.sh / sync_container.sh 等脚本解析，
# 用于自动同步、权限配置与容器映射。
# ============================================================

version: 0.2
author: "Mason / 王萌"
updated: "2025-10-15"

mappings:
  # ============================================================
  # 🧱 宿主层（Host System）
  # ------------------------------------------------------------
  # 包含 NixOS 配置文件、硬件声明、日志路径映射
  # ============================================================
  - name: system-config
    src: system/etc/nixos/
    dst: /etc/nixos/
    sudo: true
    description: "系统配置声明与硬件模块（configuration.nix / hardware.nix）"

  - name: system-logs
    src: system/var/log/aila/
    dst: /var/log/aila/
    sudo: true
    description: "宿主日志路径（同步用于离线调试）"

  - name: system-opt
    src: system/opt/aila/
    dst: /opt/aila/
    sudo: true
    description: "系统级可执行组件与共享模块（AI接口 / 脚本）"

  # ============================================================
  # ⚙️ 服务层（Organs）
  # ------------------------------------------------------------
  # 各功能服务：Whisper、Ollama、Piper、Monitor
  # ============================================================
  - name: ollama-service
    src: services/ollama/systemd/
    dst: /etc/systemd/system/
    sudo: true
    description: "Ollama 推理服务（GPU 语言模型）"

  - name: ollama-config
    src: services/ollama/config/
    dst: /etc/ollama/
    sudo: true
    description: "Ollama 模型配置与端口声明"

  # ===========================================================
  # 🎧 WHISPER 模块（语音识别 + 唤醒检测）
  # ===========================================================
  - name: whisper-service
    src: services/whisper/systemd/
    dst: /etc/systemd/system/
    sudo: true
    description: "Whisper 主监听守护进程（实时识别语音并触发回应）"

  - name: whisper-config
    src: services/whisper/config/
    dst: /etc/whisper/
    sudo: true
    description: "Whisper 配置文件（模型路径、采样率、语言等参数）"

  - name: whisper-scripts
    src: services/whisper/scripts/
    dst: /usr/local/bin/
    sudo: true
    description: "Whisper 辅助脚本（录音、文字转语音、接口调试）"

  - name: whisper-main
    src: services/whisper/main/
    dst: /opt/aila/whisper/
    sudo: true
    description: "Whisper 主逻辑程序（唤醒检测 + 调用 Ollama + 调用 Piper 播放）"


  - name: piper-service
    src: services/piper/systemd/
    dst: /etc/systemd/system/
    sudo: true
    description: "Piper 语音合成服务守护进程"

  - name: piper-config
    src: services/piper/config/
    dst: /etc/piper/
    sudo: true
    description: "Piper 配置文件（模型路径 / 音量 / 语言）"

  - name: piper-main
    src: services/piper/main/
    dst: /opt/aila/piper/
    sudo: true
    description: "Piper 主程序（TTS 接口与播放逻辑）"

  - name: piper-scripts
    src: services/piper/scripts/
    dst: /usr/local/bin/
    sudo: true
    description: "Piper 辅助脚本（命令行播放文本）"
    
  - name: piper-install-script
    src: services/piper/scripts/
    dst: /usr/local/bin/
    sudo: true
    description: "Piper 模型自动下载与测试脚本（install_piper_model.sh）"


  - name: monitor-service
    src: services/monitor/systemd/
    dst: /etc/systemd/system/
    sudo: true
    description: "监控模块（日志与容器心跳）"

  - name: monitor-scripts
    src: services/monitor/scripts/
    dst: /opt/aila/monitor/
    sudo: true
    description: "监控脚本与自愈逻辑"

  # ============================================================
  # 🌌 精神层（Aila Core）
  # ------------------------------------------------------------
  # Aila 的核心意识与感知逻辑（容器内部 / 宿主镜像）
  # ============================================================
  - name: aila-core
    src: aila/
    dst: /opt/aila/
    sudo: true
    description: "Aila 精神核心：feel / mind / dream 模块"

  - name: aila-models
    src: aila/link/
    dst: /opt/aila/link/
    sudo: true
    description: "Whisper / Llama 模型文件映射路径"

  # ============================================================
  # 🧠 神经层（Scripts）
  # ------------------------------------------------------------
  # 自动化控制逻辑：部署、同步、更新、日志分析
  # ============================================================
  - name: scripts
    src: scripts/
    dst: /usr/local/bin/
    sudo: true
    description: "部署与控制脚本（deploy / sync / update / launch）"

  # ============================================================
  # 🪶 部署声明层（Deploy）
  # ------------------------------------------------------------
  # 不会实际部署，只被脚本（deploy_to_nixos.sh / deploy.py）解析用于映射控制。
  # ============================================================
  - name: deploy-config
    src: deploy/
    dst: /opt/aila/deploy/
    sudo: true
    description: "部署规则声明目录（deploy.py / mapping.yaml / rsync-exclude / README）"

  # ============================================================
  # 🧩 容器映射层（Containers）
  # ------------------------------------------------------------
  # 仅同步配置，不部署实际 rootfs。
  # ============================================================
  - name: containers
    src: system/containers/
    dst: /etc/nixos/containers/
    sudo: true
    description: "Aila / Reflector / WebServer 容器声明模块"

# ============================================================
# 🧩 排除规则引用（供 rsync 使用）
# ------------------------------------------------------------
# 可选：deploy/rsync-exclude.txt 定义具体排除文件
# ============================================================
exclude_file: deploy/rsync-exclude.txt

# ============================================================
# 🚀 同步策略参数（供 deploy_to_nixos.sh 调用）
# ------------------------------------------------------------
# - mode: mirror（完全镜像同步）
# - dry_run: 是否模拟
# - backup: 是否生成 .bak 副本
# ============================================================
sync_policy:
  mode: mirror
  dry_run: false
  backup: true
  preserve_permissions: true
  show_progress: true
