#!/usr/bin/env python3
"""Show info about the current session and recent history.

Optional argument: number of recent sessions to include (default 3).
"""

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

    current = None
    for s in reversed(sessions):
        if not s.get("ended_at"):
            started = datetime.fromisoformat(s["started_at"])
            current = {
                "session_id": s["session_id"],
                "started_at": s["started_at"],
                "elapsed_seconds": int((now - started).total_seconds()),
                "message_count": len(s.get("messages", [])),
            }
            break

    emit(
        {
            "now": now.isoformat(timespec="seconds"),
            "timezone": data["timezone"],
            "total_sessions": len(sessions),
            "current_session": current,
            "recent_sessions": recent,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
