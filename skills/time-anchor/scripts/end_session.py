#!/usr/bin/env python3
"""Close the most recent open session with the current timestamp."""

import sys
from datetime import datetime

from _common import emit, get_timezone, load_memory, save_memory


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    sessions = data.get("sessions", [])
    open_sessions = [s for s in sessions if not s.get("ended_at")]

    if not open_sessions:
        emit({"ok": True, "closed": False, "reason": "no open sessions"})
        return 0

    target = open_sessions[-1]
    now = datetime.now(tz)
    target["ended_at"] = now.isoformat(timespec="seconds")

    started = datetime.fromisoformat(target["started_at"])
    duration_seconds = int((now - started).total_seconds())

    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "closed": True,
            "session_id": target["session_id"],
            "started_at": target["started_at"],
            "ended_at": target["ended_at"],
            "duration_seconds": duration_seconds,
            "duration_human": _humanize(duration_seconds),
            "message_count": len(target.get("messages", [])),
        }
    )
    return 0


def _humanize(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours, rem = divmod(seconds, 3600)
    return f"{hours}h {rem // 60}m"


if __name__ == "__main__":
    sys.exit(main())
