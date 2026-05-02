"""Shared helpers for time-anchor scripts.

Resolves the memory file location with the following priority:
  1. $TIME_ANCHOR_MEMORY_PATH (lets users point at an existing memory plugin's file)
  2. ~/.claude/memory/time-anchor.json
  3. ~/.claude/skills/time-anchor/memory.json (default; created on demand)

If the resolved file is "external" (i.e. shared with another memory plugin),
time-anchor's data is namespaced under the top-level `time_anchor` key so it
does not collide with the host plugin's keys.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA_VERSION = "1.0"
NAMESPACE_KEY = "time_anchor"

EXTERNAL_ENV = "TIME_ANCHOR_MEMORY_PATH"
PRIMARY_PATH = Path.home() / ".claude" / "memory" / "time-anchor.json"
DEFAULT_PATH = Path.home() / ".claude" / "skills" / "time-anchor" / "memory.json"


def resolve_memory_path() -> tuple[Path, str]:
    """Return (path, backend) where backend is 'external' or 'self'."""
    external = os.environ.get(EXTERNAL_ENV)
    if external:
        return Path(external).expanduser(), "external"
    if PRIMARY_PATH.exists():
        return PRIMARY_PATH, "self"
    return DEFAULT_PATH, "self"


def empty_memory() -> dict[str, Any]:
    return {
        "version": SCHEMA_VERSION,
        "timezone": None,
        "installed_at": None,
        "memory_backend": "self",
        "external_path": None,
        "sessions": [],
    }


def load_memory() -> tuple[dict[str, Any], Path, str]:
    """Load (or initialize) the memory dict. Returns (data, path, backend)."""
    path, backend = resolve_memory_path()

    if not path.exists():
        return empty_memory(), path, backend

    raw = json.loads(path.read_text(encoding="utf-8"))

    if backend == "external":
        # In a shared file, our data lives under a namespace key.
        data = raw.get(NAMESPACE_KEY) or empty_memory()
        # Carry the host file's other keys forward when we write back.
        data["_host_file_other_keys"] = {
            k: v for k, v in raw.items() if k != NAMESPACE_KEY
        }
    else:
        data = raw

    # Backfill any missing schema fields so older files keep working.
    template = empty_memory()
    for k, v in template.items():
        data.setdefault(k, v)

    return data, path, backend


def save_memory(data: dict[str, Any], path: Path, backend: str) -> None:
    """Persist the memory dict back to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if backend == "external":
        host_extras = data.pop("_host_file_other_keys", {})
        wrapped = dict(host_extras)
        wrapped[NAMESPACE_KEY] = data
        path.write_text(json.dumps(wrapped, indent=2), encoding="utf-8")
    else:
        # Strip any sentinel keys before writing
        data.pop("_host_file_other_keys", None)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_timezone(data: dict[str, Any]) -> ZoneInfo | None:
    """Return a ZoneInfo object for the stored timezone, or None if unset."""
    tz_name = data.get("timezone")
    if not tz_name:
        return None
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return None


def now_in_tz(data: dict[str, Any]) -> datetime | None:
    """Return current datetime in the user's stored timezone, or None if unset."""
    tz = get_timezone(data)
    if tz is None:
        return None
    return datetime.now(tz)


def emit(payload: dict[str, Any]) -> None:
    """Print JSON to stdout (the canonical output format for these scripts)."""
    print(json.dumps(payload, indent=2, default=str))
