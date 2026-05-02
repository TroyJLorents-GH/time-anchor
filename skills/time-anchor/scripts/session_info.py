#!/usr/bin/env python3
"""Show the current rolling session: when it started, elapsed, total commands.

A "session" here is NOT per-terminal — it's a single rolling window across all
your Claude Code activity. It auto-resets after `settings.idle_reset_hours`
of inactivity (default 4h, set to null/0 for "never"), or manually via
reset_session.py / /reset-session.

Every time-anchor command touches `last_active_at`. /session-time itself
counts as activity.
"""

import sys
from datetime import datetime

from _common import (
    count_claude_processes,
    emit,
    format_human,
    format_short_time,
    get_time_format,
    get_timezone,
    humanize_duration,
    load_memory,
    save_memory,
    touch_session,
)


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set. Run /set-timezone first.", file=sys.stderr)
        return 2

    now = datetime.now(tz)
    fmt = get_time_format(data)

    info = touch_session(data, now)
    save_memory(data, path, backend)

    session = data["session"]
    settings = data["settings"]
    started = datetime.fromisoformat(session["started_at"]).astimezone(tz)
    elapsed_seconds = int((now - started).total_seconds())

    idle_hours = settings.get("idle_reset_hours")
    idle_label = "never" if not idle_hours else f"{idle_hours}h"
    terminal_count = count_claude_processes()

    emit(
        {
            "now": now.isoformat(timespec="seconds"),
            "now_human": format_human(now, fmt),
            "tz_label": now.strftime("%Z"),
            "timezone": data["timezone"],
            "session_started_at": session["started_at"],
            "session_started_human": format_short_time(started, fmt),
            "elapsed_seconds": elapsed_seconds,
            "elapsed_human": humanize_duration(elapsed_seconds),
            "lifetime_command_count": data.get("lifetime_command_count", 0),
            "active_terminals": terminal_count,
            "idle_reset_hours": idle_hours,
            "idle_reset_label": idle_label,
            "time_format": fmt,
            "just_reset": info["reset"],
            "reset_reason": info["reset_reason"],
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
