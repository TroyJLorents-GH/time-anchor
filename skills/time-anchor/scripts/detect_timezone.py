#!/usr/bin/env python3
"""Best-effort detection of the host system's IANA timezone.

Tries (in order):
  1. $TZ env var
  2. /etc/timezone (Linux)
  3. /etc/localtime symlink target (Linux/Mac)
  4. `tzutil /g` -> Windows->IANA mapping (Windows)

Prints JSON:
  {"best": {"timezone": "America/Phoenix", "source": "tzutil:US Mountain Standard Time"},
   "candidates": [...],
   "raw": {"windows_name": "..."}}

Exit 0 if at least one valid IANA candidate found, else 1.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from zoneinfo import available_timezones

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
WIN_MAP_FILE = ASSETS_DIR / "windows_zones.json"


def from_env() -> tuple[str | None, str | None]:
    tz = os.environ.get("TZ", "").strip()
    if tz and tz in available_timezones():
        return tz, "env:TZ"
    return None, None


def from_etc_timezone() -> tuple[str | None, str | None]:
    p = Path("/etc/timezone")
    if not p.exists():
        return None, None
    try:
        v = p.read_text(encoding="utf-8").strip()
    except Exception:
        return None, None
    if v in available_timezones():
        return v, "/etc/timezone"
    return None, None


def from_etc_localtime() -> tuple[str | None, str | None]:
    p = Path("/etc/localtime")
    try:
        is_link = p.is_symlink()
    except OSError:
        is_link = False
    if not is_link:
        return None, None
    try:
        target = os.readlink(p)
    except OSError:
        return None, None
    marker = "zoneinfo/"
    if marker in target:
        v = target.split(marker, 1)[1]
        if v in available_timezones():
            return v, "/etc/localtime"
    return None, None


def load_windows_map() -> dict[str, str]:
    if not WIN_MAP_FILE.exists():
        return {}
    try:
        raw = json.loads(WIN_MAP_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def from_windows_tzutil() -> tuple[str | None, str | None, str | None]:
    """Returns (iana, source, raw_windows_name)."""
    if sys.platform != "win32":
        return None, None, None
    try:
        out = subprocess.check_output(
            ["tzutil", "/g"], text=True, timeout=5, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None, None, None
    if not out:
        return None, None, None
    mapping = load_windows_map()
    iana = mapping.get(out)
    if iana and iana in available_timezones():
        return iana, f"tzutil:{out}", out
    return None, None, out


def main() -> int:
    candidates: list[dict[str, str]] = []
    raw: dict[str, str] = {}

    for fn in (from_env, from_etc_timezone, from_etc_localtime):
        tz, src = fn()
        if tz:
            candidates.append({"timezone": tz, "source": src})

    iana, src, win_name = from_windows_tzutil()
    if win_name:
        raw["windows_name"] = win_name
    if iana:
        candidates.append({"timezone": iana, "source": src})

    result = {
        "best": candidates[0] if candidates else None,
        "candidates": candidates,
        "raw": raw,
    }
    print(json.dumps(result, indent=2))
    return 0 if candidates else 1


if __name__ == "__main__":
    sys.exit(main())
