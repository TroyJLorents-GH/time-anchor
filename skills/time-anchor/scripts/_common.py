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


def format_human(dt: datetime) -> str:
    """Format a tz-aware datetime as 'Saturday, May 2, 2026 at 2:29 PM MST'.

    Built manually rather than via strftime to avoid:
      - Leading zeros (Windows %d/%I always pad; GNU %-d/%-I is platform-specific)
      - Inconsistent rendering across Claude turns when callers reformat the
        ISO string themselves.
    """
    weekday = dt.strftime("%A")
    month = dt.strftime("%B")
    day = dt.day
    year = dt.year
    hour_12 = dt.hour % 12 or 12
    minute = f"{dt.minute:02d}"
    ampm = "AM" if dt.hour < 12 else "PM"
    tz_label = dt.strftime("%Z") or ""
    suffix = f" {tz_label}" if tz_label else ""
    return f"{weekday}, {month} {day}, {year} at {hour_12}:{minute} {ampm}{suffix}"


def format_short_time(dt: datetime) -> str:
    """Format a datetime as '2:29 PM MST' — used in compact table cells."""
    hour_12 = dt.hour % 12 or 12
    minute = f"{dt.minute:02d}"
    ampm = "AM" if dt.hour < 12 else "PM"
    tz_label = dt.strftime("%Z") or ""
    suffix = f" {tz_label}" if tz_label else ""
    return f"{hour_12}:{minute} {ampm}{suffix}"


def humanize_duration(seconds: int) -> str:
    """Format a duration as '2h 14m' / '14m 23s' / '6s'."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours, rem = divmod(seconds, 3600)
    return f"{hours}h {rem // 60}m"


def get_claude_instance_id() -> str | None:
    """Best-effort identifier for the current Claude Code instance.

    Tries (in order):
      1. CLAUDE_SESSION_ID — future-proof, in case Anthropic adds it.
      2. CLAUDE_CODE_SSE_PORT — unique per running CC instance (each instance
         binds its own local SSE server on a random port). Stable for the
         lifetime of the process.
      3. None — caller should fall back to most-recent-open logic.
    """
    for var in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SSE_PORT"):
        v = os.environ.get(var, "").strip()
        if v:
            return f"{var.lower()}:{v}"
    return None
