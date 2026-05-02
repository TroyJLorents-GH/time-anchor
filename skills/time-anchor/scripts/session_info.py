#!/usr/bin/env python3
"""Show info about the current session and recent history.

"Current session" is the record matching `$CLAUDE_SESSION_ID` if available
(multi-window aware). Falls back to the most-recent-open untracked record
if no env var is set.

Always emits canonical `now_human` and `tz_label` fields so callers can
render time consistently without reformatting the ISO string themselves.

Optional argument: number of recent sessions to include (default 3).
"""

import os
import sys
from datetime import datetime

from _common import emit, get_timezone, load_memory


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    data, _, _ = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    now = datetime.now(tz)
    sessions = data.get("sessions", [])
    recent = sessions[-n:] if sessions else []
    claude_session_id = os.environ.get("CLAUDE_SESSION_ID", "").strip() or None

    current_record = None
    if claude_session_id:
        for s in reversed(sessions):
            if s.get("claude_session_id") == claude_session_id and not s.get("ended_at"):
                current_record = s
                break

    # Legacy fallback: only consider untracked open records "current" when
    # we don't have a CLAUDE_SESSION_ID to compare against.
    if current_record is None and not claude_session_id:
        for s in reversed(sessions):
            if not s.get("ended_at") and "claude_session_id" not in s:
                current_record = s
                break

    current = None
    if current_record:
        started = datetime.fromisoformat(current_record["started_at"])
        current = {
            "session_id": current_record["session_id"],
            "claude_session_id": current_record.get("claude_session_id"),
            "started_at": current_record["started_at"],
            "elapsed_seconds": int((now - started).total_seconds()),
            "message_count": len(current_record.get("messages", [])),
        }

    try:
        now_human = now.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")
    except ValueError:
        now_human = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    emit(
        {
            "now": now.isoformat(timespec="seconds"),
            "now_human": now_human,
            "tz_label": now.strftime("%Z"),
            "timezone": data["timezone"],
            "claude_session_id": claude_session_id,
            "total_sessions": len(sessions),
            "current_session": current,
            "recent_sessions": recent,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
