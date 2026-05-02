#!/usr/bin/env python3
"""Log the start of a Claude Code session.

Captures `$CLAUDE_SESSION_ID` (the Claude Code instance ID) in the session
record so multiple parallel Claude Code windows don't trample each other.
If the same CLAUDE_SESSION_ID already has an open session, reuses it
instead of creating a duplicate (handles SessionStart firing twice per
Claude Code instance).
"""

import sys
import uuid
from datetime import datetime

from _common import emit, format_human, format_short_time, get_claude_instance_id, get_timezone, load_memory, save_memory


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
    claude_session_id = get_claude_instance_id()

    # If we already have an open record for this Claude Code instance, reuse it.
    # When env var is missing (claude --resume mode) we still want to reuse the
    # most recent untagged-open record rather than create a new one each call.
    reuse_predicate = (
        (lambda s: s.get("claude_session_id") == claude_session_id)
        if claude_session_id
        else (lambda s: not s.get("claude_session_id"))
    )
    if True:
        for s in reversed(sessions):
            if reuse_predicate(s) and not s.get("ended_at"):
                started = datetime.fromisoformat(s["started_at"])
                started_local = started.astimezone(tz)
                emit(
                    {
                        "ok": True,
                        "reused": True,
                        "session_id": s["session_id"],
                        "claude_session_id": claude_session_id,
                        "started_at": s["started_at"],
                        "started_human": format_short_time(started_local),
                        "now": now.isoformat(timespec="seconds"),
                        "now_human": format_human(now),
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
            "started_human": format_short_time(now),
            "now": now.isoformat(timespec="seconds"),
            "now_human": format_human(now),
            "tz_label": now.strftime("%Z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
