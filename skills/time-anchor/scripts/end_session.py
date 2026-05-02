#!/usr/bin/env python3
"""Close the time-anchor session matching this Claude Code instance.

Reads `$CLAUDE_SESSION_ID` and only closes the session record that matches.
Falls back to the most-recent-open record only if (a) there's no
CLAUDE_SESSION_ID set, AND (b) that record itself was logged without one
(legacy / pre-multi-window). This prevents one Claude Code window from
ending a session that belongs to another open window.
"""

import sys
from datetime import datetime

from _common import (
    emit,
    format_human,
    format_short_time,
    get_claude_instance_id,
    get_timezone,
    humanize_duration,
    load_memory,
    save_memory,
)


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    sessions = data.get("sessions", [])
    claude_session_id = get_claude_instance_id()

    target = None
    if claude_session_id:
        for s in reversed(sessions):
            if s.get("claude_session_id") == claude_session_id and not s.get("ended_at"):
                target = s
                break
    # When env var is missing we can't tell which open null-port record
    # belongs to this terminal. Bail out rather than risk closing a
    # different terminal's session.

    if target is None:
        emit(
            {
                "ok": True,
                "closed": False,
                "claude_session_id": claude_session_id,
                "reason": "no matching open session",
            }
        )
        return 0

    now = datetime.now(tz)
    target["ended_at"] = now.isoformat(timespec="seconds")

    started = datetime.fromisoformat(target["started_at"])
    started_local = started.astimezone(tz)
    duration_seconds = int((now - started).total_seconds())

    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "closed": True,
            "session_id": target["session_id"],
            "claude_session_id": target.get("claude_session_id"),
            "started_at": target["started_at"],
            "started_human": format_short_time(started_local),
            "ended_at": target["ended_at"],
            "ended_human": format_short_time(now),
            "now_human": format_human(now),
            "duration_seconds": duration_seconds,
            "duration_human": humanize_duration(duration_seconds),
            "message_count": len(target.get("messages", [])),
            "tz_label": now.strftime("%Z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
