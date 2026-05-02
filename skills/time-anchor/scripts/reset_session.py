#!/usr/bin/env python3
"""Manually reset the rolling session timer. Sets started_at = now."""

import sys
from datetime import datetime

from _common import (
    emit,
    format_human,
    get_time_format,
    get_timezone,
    load_memory,
    save_memory,
)


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set. Run /set-timezone first.", file=sys.stderr)
        return 2

    now = datetime.now(tz)
    fmt = get_time_format(data)

    session = data.setdefault(
        "session", {"started_at": None, "last_active_at": None}
    )
    previous_started = session.get("started_at")
    now_iso = now.isoformat(timespec="seconds")
    session["started_at"] = now_iso
    session["last_active_at"] = now_iso

    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "previous_started_at": previous_started,
            "started_at": now_iso,
            "started_human": format_human(now, fmt),
            "tz_label": now.strftime("%Z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
