"""
Utilities for capturing simple snapshots of the container's environment.
"""

from __future__ import annotations

import os
import platform
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict


@dataclass
class SenseSnapshot:
    timestamp: float
    load_1m: float
    load_5m: float
    memory_total_mb: float
    memory_available_mb: float
    disk_free_mb: float
    disk_total_mb: float
    notes: str = ""

    def summary(self) -> str:
        load = f"load(1m)={self.load_1m:.2f}"
        mem_used_pct = 0.0
        if self.memory_total_mb:
            mem_used_pct = 100.0 * (1.0 - (self.memory_available_mb / self.memory_total_mb))
        mem = f"mem={mem_used_pct:.0f}%"
        disk_pct = 0.0
        if self.disk_total_mb:
            disk_pct = 100.0 * (1.0 - (self.disk_free_mb / self.disk_total_mb))
        disk = f"disk={disk_pct:.0f}%"
        bits = [load, mem, disk]
        if self.notes:
            bits.append(self.notes)
        return ", ".join(bits)

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)


def _read_proc_meminfo() -> Dict[str, float]:
    """
    Parse /proc/meminfo when available. Values are returned in MiB.
    """
    path = Path("/proc/meminfo")
    data: Dict[str, float] = {}
    if not path.exists():
        return data
    for line in path.read_text().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parts = value.strip().split()
        if not parts:
            continue
        try:
            amount_kb = float(parts[0])
        except ValueError:
            continue
        data[key] = amount_kb / 1024.0
    return data


def _get_load_average() -> tuple[float, float, float]:
    try:
        return os.getloadavg()
    except (AttributeError, OSError):
        # Platform does not expose load average (e.g., Windows during development).
        return (0.0, 0.0, 0.0)


def capture_snapshot() -> SenseSnapshot:
    """
    Collect a coarse-grained view of resource utilisation.
    """
    load_1m, load_5m, load_15m = _get_load_average()
    meminfo = _read_proc_meminfo()
    mem_total = meminfo.get("MemTotal", 0.0)
    mem_available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0.0))

    # Use the filesystem that contains /opt/aila, falling back to the root FS.
    app_path = Path("/opt/aila")
    probe_path = app_path if app_path.exists() else Path("/")
    usage = shutil.disk_usage(probe_path)
    disk_total_mb = usage.total / (1024.0 * 1024.0)
    disk_free_mb = usage.free / (1024.0 * 1024.0)

    notes = ""
    if platform.system() != "Linux":
        notes = f"platform={platform.system()}"

    return SenseSnapshot(
        timestamp=time.time(),
        load_1m=load_1m,
        load_5m=load_5m,
        memory_total_mb=mem_total,
        memory_available_mb=mem_available,
        disk_free_mb=disk_free_mb,
        disk_total_mb=disk_total_mb,
        notes=notes,
    )
