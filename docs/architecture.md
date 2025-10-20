# Architecture Overview

This document adapts the layered structure from the NixOS blueprint to an Ubuntu 24.04 robotics workstation. The guiding principles are declarative configuration, modular services, and reproducible deployments.

## Layer Model

| Layer | Repository Path | Ubuntu Target | Purpose |
| ----- | ---------------- | ------------- | ------- |
| Host System | `system/` | `/etc/` and `/opt/aila/` | Base OS configuration fragments and shared data roots |
| Organs | `services/` | `/etc/systemd/system/`, `/opt/aila/<service>/`, `/etc/<service>/` | Dedicated services for perception, language, and monitoring |
| Core | `aila/` | `/opt/aila/core/` | Cognitive runtime with perception, planning, and dialogue modules |
| Nervous System | `scripts/` | `/usr/local/bin/` | Automation scripts for install, update, and runtime management |
| Deployment | `deploy/` | Controller only | Mapping definitions plus Python dispatcher for rsync |
| Knowledge | `docs/` | N/A | Conceptual references, operations notes, and API documentation |

## Service Contracts

- **Inputs**: microphone streams, camera frames, telemetry metrics
- **Outputs**: textual responses, speech audio, structured logs
- **Messaging**: REST/WebSocket for application control, gRPC optional
- **Observability**: systemd journal, Prometheus textfile exporter, optional Loki

## Runtime Components

1. `aila.runtime.Orchestrator` manages process lifecycle and plugs into service APIs.
2. `aila.core.MindPipeline` fuses Whisper transcripts, Ollama completions, and Piper synthesis.
3. `services/*/systemd/*.service` run under dedicated system users with GPU access.
4. `scripts/run_aila.sh` bootstraps the runtime inside a Python virtual environment.
5. `deploy/deploy.py` ensures repeatable synchronization to remote hosts via SSH/rsync.

## Data Flow Summary

```
Audio -> services/whisper -> aila.core.perception -> aila.core.mind -> services/piper
                          \-> services/monitor -> Prometheus scrape endpoint
Text  <- services/ollama <- aila.core.planner  <- aila.interfaces.speech
```

## Multi-Host Considerations

- Edge nodes (Jetson or x86) can run individual services, each using the same structure.
- `mapping.yaml` supports per-target overrides through environment variables (see deploy README).
- Use `scripts/deploy_to_host.sh --tag edge` to apply specialized mappings (future work).

