# Deploy Controller

The deploy controller keeps a single source of truth for synchronizing this repository to one or more Ubuntu hosts.

## Files

- `deploy.py` – Python wrapper around `rsync` that reads `mapping.yaml`.
- `mapping.yaml` – declarative mapping from repository directories to target paths.
- `rsync-exclude.txt` – patterns excluded from synchronization (build artifacts, caches).

## Usage

```
python deploy.py --host robot01
python deploy.py --host robot01 --apply
python deploy.py --host robot01 --apply --filter services=whisper,coqui
```

`deploy.py` reads SSH connection details from the environment:

- `AILA_DEPLOY_USER`
- `AILA_DEPLOY_PORT` (defaults to 22)
- `AILA_DEPLOY_KEY` (optional path to a private key)

The command runs in dry-run mode by default. Add `--apply` to push changes using `rsync --archive --delete`.

## Extending Mappings

Add or modify entries in `mapping.yaml`. Each mapping contains:

- `name` (identifier)
- `src` (path within the repository)
- `dst` (path on the target host)
- `sudo` (boolean to execute with elevated permissions)
- `description` (human readable note)

`deploy.py` can filter by `name` or group using the `--filter` option.
