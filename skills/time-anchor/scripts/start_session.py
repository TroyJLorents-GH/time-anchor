#!/usr/bin/env python3
"""Log the start of a Claude Code session.

Captures `$CLAUDE_SESSION_ID` (the Claude Code instance ID) in the session
record so multiple parallel Claude Code windows don't trample each other.
If the same CLAUDE_SESSION_ID already has an open session, reuses it
instead of creating a duplicate (handles SessionStart firing twice per
Claude Code instance).
"""

import os
import sys
import uuid
from datetime import datetime

from _common import emit, get_timezone, load_memory, save_memory


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print(
            "ERROR: no timezone set. Run init.py first, then set_timezone.py.",
            file=sys.stderr,
        )
        return 2

    now = datetime.now(tz)
    sessions = data.setdefault("sessions", [])
    claude_session_id = os.environ.get("CLAUDE_SESSION_ID", "").strip() or None

    # If we already have an open record for this Claude Code instance, reuse it.
    if claude_session_id:
        for s in reversed(sessions):
            if s.get("claude_session_id") == claude_session_id and not s.get("ended_at"):
                emit(
                    {
                        "ok": True,
                        "reused": True,
                        "session_id": s["session_id"],
                        "claude_session_id": claude_session_id,
                        "started_at": s["started_at"],
                        "now": now.isoformat(timespec="seconds"),
                        "tz_label": now.strftime("%Z"),
                    }
                )
                return 0

    new_session = {
        "session_id": uuid.uuid4().hex[:12],
        "claude_session_id": claude_session_id,
        "started_at": now.isoformat(timespec="seconds"),
        "ended_at": None,
        "messages": [],
    }
    sessions.append(new_session)
    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "reused": False,
            "session_id": new_session["session_id"],
            "claude_session_id": claude_session_id,
            "started_at": new_session["started_at"],
            "now": now.isoformat(timespec="seconds"),
            "tz_label": now.strftime("%Z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
