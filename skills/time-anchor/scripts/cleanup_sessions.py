#!/usr/bin/env python3
"""Auto-close stale-open session records.

A "stale" session is one where:
  - ended_at is null (still marked active)
  - started_at is older than the threshold (default: 12 hours ago)
  - claude_session_id does NOT match the current Claude Code instance
    (so we never close the actual running session calling cleanup)

Stale records get `ended_at` set to `started_at + threshold` (so the
duration column reads sensibly, not "10 days active"), plus an
`auto_closed: true` marker for transparency.

Usage:
  python cleanup_sessions.py            # threshold = 12 hours
  python cleanup_sessions.py 24         # threshold = 24 hours
  python cleanup_sessions.py 0          # close ALL stale-open records
                                        # (excluding current instance's)
"""

import sys
from datetime import datetime, timedelta

from _common import (
    emit,
    format_short_time,
    get_claude_instance_id,
    get_timezone,
    humanize_duration,
    load_memory,
    save_memory,
)


def main() -> int:
    threshold_hours = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0

    data, path, backend = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    now = datetime.now(tz)
    cutoff = now - timedelta(hours=threshold_hours)
    my_id = get_claude_instance_id()

    sessions = data.get("sessions", [])
    closed = []

    for s in sessions:
        if s.get("ended_at"):
            continue
        if my_id and s.get("claude_session_id") == my_id:
            continue
        try:
            started = datetime.fromisoformat(s["started_at"])
        except (KeyError, ValueError):
            continue

        if threshold_hours == 0 or started < cutoff:
            # Mark ended at started + threshold (or now if threshold=0)
            if threshold_hours == 0:
                ended = now
            else:
                ended = started + timedelta(hours=threshold_hours)
                if ended > now:
                    ended = now
            s["ended_at"] = ended.isoformat(timespec="seconds")
            s["auto_closed"] = True
            duration_seconds = int((ended - started).total_seconds())
            closed.append(
                {
                    "session_id": s["session_id"],
                    "claude_session_id": s.get("claude_session_id"),
                    "started_human": format_short_time(started.astimezone(tz)),
                    "ended_human": format_short_time(ended.astimezone(tz)),
                    "duration_human": humanize_duration(duration_seconds),
                }
            )

    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "threshold_hours": threshold_hours,
            "closed_count": len(closed),
            "closed_sessions": closed,
            "current_instance": my_id,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
