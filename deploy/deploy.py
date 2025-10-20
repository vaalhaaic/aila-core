#!/usr/bin/env python3
"""
Rsync-based deploy controller for the Aila Ubuntu stack.

Examples:
    python deploy.py --host robot01
    python deploy.py --host robot01 --apply
    python deploy.py --host robot01 --apply --filter services=whisper,piper
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - simple helper
    raise SystemExit(
        "PyYAML is required. Install it with `python -m pip install pyyaml`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "deploy" / "mapping.yaml"


@dataclass
class Mapping:
    name: str
    src: Path
    dst: str
    sudo: bool
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> "Mapping":
        required = {"name", "src", "dst"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Mapping missing fields: {missing!r}")
        return cls(
            name=str(data["name"]),
            src=(ROOT / data["src"]).resolve(),
            dst=str(data["dst"]),
            sudo=bool(data.get("sudo", False)),
            description=str(data.get("description", "")).strip(),
        )


def load_config(path: Path) -> tuple[List[Mapping], dict]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    raw_mappings = payload.get("mappings", [])
    mappings = [Mapping.from_dict(item) for item in raw_mappings]
    sync_policy = payload.get("sync_policy", {}) or {}
    return mappings, sync_policy


def parse_filters(filters: Sequence[str]) -> List[str]:
    tokens: List[str] = []
    for item in filters:
        if "=" in item:
            _, value = item.split("=", 1)
            tokens.extend(val.strip() for val in value.split(",") if val.strip())
        else:
            tokens.append(item.strip())
    return tokens


def filter_mappings(mappings: Iterable[Mapping], tokens: Sequence[str]) -> List[Mapping]:
    if not tokens:
        return list(mappings)
    lowered = [token.lower() for token in tokens]
    result = [
        mapping
        for mapping in mappings
        if any(token in mapping.name.lower() for token in lowered)
    ]
    return result


def build_rsync_base(
    sync_policy: dict,
    apply_changes: bool,
    exclude_file: Path | None,
) -> List[str]:
    cmd = ["rsync", "--archive", "--compress", "--human-readable"]
    mode = (sync_policy.get("mode") or "").lower()
    if mode == "mirror":
        cmd.append("--delete")
    if sync_policy.get("show_progress", False):
        cmd.append("--info=progress2")
    if sync_policy.get("preserve_permissions", True):
        cmd.append("--perms")
    if sync_policy.get("backup", False):
        cmd.append("--backup")
    if not apply_changes:
        cmd.append("--dry-run")
    elif sync_policy.get("dry_run", False):
        cmd.append("--dry-run")
    if exclude_file and exclude_file.exists():
        cmd.append(f"--exclude-from={str(exclude_file)}")
    return cmd


def build_ssh_command(port: int, key_path: str | None) -> str:
    parts = ["ssh", "-p", str(port), "-o", "BatchMode=yes"]
    if key_path:
        parts.extend(["-i", key_path])
    return " ".join(parts)


def run_rsync(
    mapping: Mapping,
    base_cmd: List[str],
    host: str,
    user: str | None,
    port: int,
    key_path: str | None,
    apply_changes: bool,
) -> int:
    if not mapping.src.exists():
        raise FileNotFoundError(f"Source path does not exist: {mapping.src}")

    src = str(mapping.src)
    if mapping.src.is_dir():
        src = str(mapping.src) + "/"

    ssh_command = build_ssh_command(port, key_path)

    if host in ("local", "localhost") and not user:
        remote = mapping.dst
        cmd = list(base_cmd)
        if mapping.sudo and apply_changes:
            cmd = ["sudo"] + cmd
        cmd.extend([src, remote])
    else:
        remote = mapping.dst
        ssh_options = ["-e", ssh_command]
        cmd = list(base_cmd) + ssh_options
        if mapping.sudo:
            cmd.append('--rsync-path="sudo rsync"')
        target = f"{remote}"
        if not remote.startswith("/"):
            raise ValueError(f"Destination must be an absolute path: {remote}")
        destination = f"{remote}"
        prefix = f"{user}@{host}" if user else host
        destination = f"{prefix}:{destination}"
        cmd.extend([src, destination])

    print(f"\n>>> {mapping.name}")
    if mapping.description:
        print(f"    {mapping.description}")
    print("    " + " ".join(shlex.quote(part) for part in cmd))

    process = subprocess.run(cmd, check=False)
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy repository content to Ubuntu hosts.")
    parser.add_argument("--host", default="localhost", help="Host name or IP of the target")
    parser.add_argument("--apply", action="store_true", help="Apply changes (disable dry-run)")
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Filter mappings by name token (e.g. services=whisper,piper)",
    )
    parser.add_argument(
        "--mapping",
        default=str(CONFIG_PATH),
        help="Path to the mapping.yaml file",
    )
    parser.add_argument(
        "--exclude",
        default=None,
        help="Override path to rsync exclude file",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override SSH port (default 22 or env AILA_DEPLOY_PORT)",
    )
    args = parser.parse_args()

    mapping_path = Path(args.mapping).resolve()
    mappings, sync_policy = load_config(mapping_path)

    tokens = parse_filters(args.filter)
    mappings = filter_mappings(mappings, tokens)
    if not mappings:
        print("No mappings selected.", file=sys.stderr)
        return 1

    exclude_path = (
        Path(args.exclude).resolve()
        if args.exclude
        else (mapping_path.parent / "rsync-exclude.txt")
    )
    base_cmd = build_rsync_base(sync_policy, args.apply, exclude_path)

    env_user = os.getenv("AILA_DEPLOY_USER")
    env_port = os.getenv("AILA_DEPLOY_PORT")
    env_key = os.getenv("AILA_DEPLOY_KEY")

    port = args.port or int(env_port or 22)
    host = args.host
    user = env_user
    key_path = env_key

    print(f"Target host: {host}")
    print(f"SSH user   : {user or '<local>'}")
    print(f"SSH port   : {port}")
    print(f"Apply mode : {'yes' if args.apply else 'no (dry-run)'}")
    if key_path:
        print(f"SSH key    : {key_path}")

    failures = 0
    for mapping in mappings:
        try:
            code = run_rsync(
                mapping=mapping,
                base_cmd=base_cmd,
                host=host,
                user=user,
                port=port,
                key_path=key_path,
                apply_changes=args.apply,
            )
        except Exception as exc:  # pragma: no cover - deployment feedback
            print(f"[ERROR] {mapping.name}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if code != 0:
            print(f"[ERROR] {mapping.name}: rsync returned {code}", file=sys.stderr)
            failures += 1

    if failures:
        print(f"Completed with {failures} failures.", file=sys.stderr)
        return 2

    print("All mappings processed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
