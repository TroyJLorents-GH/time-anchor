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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA_VERSION = "2.0"
NAMESPACE_KEY = "time_anchor"

EXTERNAL_ENV = "TIME_ANCHOR_MEMORY_PATH"
PRIMARY_PATH = Path.home() / ".claude" / "memory" / "time-anchor.json"
DEFAULT_PATH = Path.home() / ".claude" / "skills" / "time-anchor" / "memory.json"

DEFAULT_IDLE_RESET_HOURS = 4
DEFAULT_TIME_FORMAT = "12h"


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
        "settings": {
            "idle_reset_hours": DEFAULT_IDLE_RESET_HOURS,
            "time_format": DEFAULT_TIME_FORMAT,
        },
        "session": {
            "started_at": None,
            "last_active_at": None,
        },
        "lifetime_command_count": 0,
    }


def load_memory() -> tuple[dict[str, Any], Path, str]:
    """Load (or initialize) the memory dict. Returns (data, path, backend)."""
    path, backend = resolve_memory_path()

    if not path.exists():
        return empty_memory(), path, backend

    raw = json.loads(path.read_text(encoding="utf-8"))

    if backend == "external":
        data = raw.get(NAMESPACE_KEY) or empty_memory()
        data["_host_file_other_keys"] = {
            k: v for k, v in raw.items() if k != NAMESPACE_KEY
        }
    else:
        data = raw

    # Backfill any missing schema fields so older files keep working.
    template = empty_memory()
    for k, v in template.items():
        if k not in data:
            data[k] = v
    # Backfill nested keys
    for k, v in template["settings"].items():
        data["settings"].setdefault(k, v)
    for k, v in template["session"].items():
        data["session"].setdefault(k, v)

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


def get_time_format(data: dict[str, Any]) -> str:
    """Return user's preferred time format ('12h', '24h', or 'military')."""
    fmt = data.get("settings", {}).get("time_format", DEFAULT_TIME_FORMAT)
    return fmt if fmt in ("12h", "24h", "military") else DEFAULT_TIME_FORMAT


def format_human(dt: datetime, fmt: str = DEFAULT_TIME_FORMAT) -> str:
    """Format a tz-aware datetime per user preference.

    12h:      'Saturday, May 2, 2026 at 1:00 PM MST'
    24h:      'Saturday, May 2, 2026 at 13:00 MST'
    military: 'Saturday, May 2, 2026 at 1300 MST'
    """
    weekday = dt.strftime("%A")
    month = dt.strftime("%B")
    day = dt.day
    year = dt.year
    minute = f"{dt.minute:02d}"
    tz_label = dt.strftime("%Z") or ""
    suffix = f" {tz_label}" if tz_label else ""

    if fmt == "military":
        return f"{weekday}, {month} {day}, {year} at {dt.hour:02d}{minute}{suffix}"

    if fmt == "24h":
        hour_24 = f"{dt.hour:02d}"
        return f"{weekday}, {month} {day}, {year} at {hour_24}:{minute}{suffix}"

    hour_12 = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{weekday}, {month} {day}, {year} at {hour_12}:{minute} {ampm}{suffix}"


def format_short_time(dt: datetime, fmt: str = DEFAULT_TIME_FORMAT) -> str:
    """Format a datetime as compact time per user preference.

    12h:      '1:00 PM MST'
    24h:      '13:00 MST'
    military: '1300 MST'
    """
    minute = f"{dt.minute:02d}"
    tz_label = dt.strftime("%Z") or ""
    suffix = f" {tz_label}" if tz_label else ""

    if fmt == "military":
        return f"{dt.hour:02d}{minute}{suffix}"

    if fmt == "24h":
        hour_24 = f"{dt.hour:02d}"
        return f"{hour_24}:{minute}{suffix}"

    hour_12 = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{hour_12}:{minute} {ampm}{suffix}"


def humanize_duration(seconds: int) -> str:
    """Format a duration as '2h 14m' / '14m 23s' / '6s'."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours, rem = divmod(seconds, 3600)
    return f"{hours}h {rem // 60}m"


def touch_session(data: dict[str, Any], now: datetime) -> dict[str, Any]:
    """Update last_active_at on every command. Reset if idle past threshold.

    Returns metadata about what happened: {'reset': bool, 'reset_reason': str|None}.
    Mutates data in place.
    """
    session = data.setdefault("session", {"started_at": None, "last_active_at": None})
    settings = data.setdefault("settings", {})
    idle_hours = settings.get("idle_reset_hours", DEFAULT_IDLE_RESET_HOURS)

    now_iso = now.isoformat(timespec="seconds")
    info: dict[str, Any] = {"reset": False, "reset_reason": None}

    if not session.get("started_at"):
        session["started_at"] = now_iso
        info["reset"] = True
        info["reset_reason"] = "first run"
    elif idle_hours and session.get("last_active_at"):
        try:
            last = datetime.fromisoformat(session["last_active_at"])
            if now - last > timedelta(hours=float(idle_hours)):
                session["started_at"] = now_iso
                info["reset"] = True
                info["reset_reason"] = f"idle > {idle_hours}h"
        except (ValueError, TypeError):
            pass

    session["last_active_at"] = now_iso
    data["lifetime_command_count"] = int(data.get("lifetime_command_count", 0)) + 1
    return info


def count_claude_processes() -> int | None:
    """Best-effort count of running Claude Code CLI processes on the host.

    Filters by command line path so the Electron desktop app (which also
    runs as `Claude.exe` and spawns many child processes — crashpad,
    gpu, renderer, utility) doesn't inflate the count.

    Returns None if detection fails (we don't pretend zero in that case).
    """
    import subprocess
    import sys

    try:
        if sys.platform == "win32":
            ps = (
                "@(Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" "
                "| Where-Object { $_.CommandLine -like '*claude-code*' }).Count"
            )
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps],
                text=True, timeout=5, stderr=subprocess.DEVNULL)
            return int(out.strip())
        else:
            out = subprocess.check_output(
                ["pgrep", "-cf", "claude-code"],
                text=True, timeout=3, stderr=subprocess.DEVNULL)
            return int(out.strip())
    except Exception:
        return None
