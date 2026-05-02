#!/usr/bin/env python3
"""Show info about the current session and recent history.

"Current session" is the record matching this Claude Code instance's
identifier (CLAUDE_CODE_SSE_PORT) when available — multi-window aware.

Always emits canonical `now_human`, `tz_label`, and per-session
`started_human`/`ended_human`/`duration_human` fields so callers render
time consistently without reformatting any ISO strings themselves.

Optional argument: number of recent sessions to include (default 3).
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
)


def _enrich(record: dict, now: datetime, tz) -> dict:
    """Add human-formatted fields to a session record for table rendering."""
    started = datetime.fromisoformat(record["started_at"])
    started_local = started.astimezone(tz)
    enriched = {
        "session_id": record["session_id"],
        "claude_session_id": record.get("claude_session_id"),
        "started_at": record["started_at"],
        "started_human": format_short_time(started_local),
        "ended_at": record.get("ended_at"),
        "ended_human": None,
        "duration_human": None,
        "messages": record.get("messages", []),
    }
    if record.get("ended_at"):
        ended = datetime.fromisoformat(record["ended_at"])
        ended_local = ended.astimezone(tz)
        enriched["ended_human"] = format_short_time(ended_local)
        enriched["duration_human"] = humanize_duration(int((ended - started).total_seconds()))
    else:
        enriched["duration_human"] = humanize_duration(int((now - started).total_seconds())) + " (active)"
    return enriched


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    data, _, _ = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    now = datetime.now(tz)
    sessions = data.get("sessions", [])
    recent_raw = sessions[-n:] if sessions else []
    claude_session_id = get_claude_instance_id()

    current_record = None
    if claude_session_id:
        # Match by Claude Code instance id (CLAUDE_CODE_SSE_PORT)
        for s in reversed(sessions):
            if s.get("claude_session_id") == claude_session_id and not s.get("ended_at"):
                current_record = s
                break
    else:
        # No env var available (e.g. CC launched via --resume). Match the
        # most recent open record that ALSO has no instance id — covers
        # both legacy untracked records and modern records written with
        # claude_session_id: null.
        for s in reversed(sessions):
            if not s.get("ended_at") and not s.get("claude_session_id"):
                current_record = s
                break

    current = None
    if current_record:
        started = datetime.fromisoformat(current_record["started_at"])
        started_local = started.astimezone(tz)
        elapsed_seconds = int((now - started).total_seconds())
        current = {
            "session_id": current_record["session_id"],
            "claude_session_id": current_record.get("claude_session_id"),
            "started_at": current_record["started_at"],
            "started_human": format_short_time(started_local),
            "elapsed_seconds": elapsed_seconds,
            "elapsed_human": humanize_duration(elapsed_seconds),
            "message_count": len(current_record.get("messages", [])),
        }

    emit(
        {
            "now": now.isoformat(timespec="seconds"),
            "now_human": format_human(now),
            "tz_label": now.strftime("%Z"),
            "timezone": data["timezone"],
            "claude_session_id": claude_session_id,
            "total_sessions": len(sessions),
            "current_session": current,
            "recent_sessions": [_enrich(s, now, tz) for s in recent_raw],
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
