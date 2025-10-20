# Piper Service

Neural text-to-speech runtime using Piper models. Converts textual responses from the core into audio streams for the embodied agent.

## Components

- `config/voice.json` – voice profile metadata.
- `systemd/piper.service` – service unit for daemonizing the synthesizer.
- `scripts/install_voice.sh` – downloads selected voices.
- `main/` – Python entry points for REST and CLI synthesis.

## Deployment Steps

1. Install voices with `scripts/install_voice.sh en_US-amy`.
2. Validate `config/voice.json` with available voices.
3. Enable the systemd unit `sudo systemctl enable --now piper.service`.
4. Test with `curl -X POST http://localhost:9082/speak -d '{"text":"Hello"}'`.

