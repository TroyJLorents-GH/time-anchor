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

from _common import emit, get_claude_instance_id, get_timezone, load_memory, save_memory


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

    # Legacy fallback: only close untracked open sessions (no claude_session_id
    # field at all). Never close a session that belongs to a different known
    # Claude Code instance.
    if target is None and not claude_session_id:
        for s in reversed(sessions):
            if not s.get("ended_at") and "claude_session_id" not in s:
                target = s
                break

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
    duration_seconds = int((now - started).total_seconds())

    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "closed": True,
            "session_id": target["session_id"],
            "claude_session_id": target.get("claude_session_id"),
            "started_at": target["started_at"],
            "ended_at": target["ended_at"],
            "duration_seconds": duration_seconds,
            "duration_human": _humanize(duration_seconds),
            "message_count": len(target.get("messages", [])),
            "tz_label": now.strftime("%Z"),
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
