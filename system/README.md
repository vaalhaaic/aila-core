# System Layer

Host-level configuration fragments for Ubuntu deployments.

## Contents

- `etc/aila/env.d/` – environment fragments consumed by systemd units.
- `opt/aila/` – base directories seeded on the host (data, cache, shared models).
- `var/log/aila/` – log directories with correct layout.

Populate `env.d/*.conf` with secrets and API keys before deployment. The defaults are placeholders.

