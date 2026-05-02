#!/usr/bin/env python3
"""Log the start of a conversation session.

Idempotent: if the most recent session has no `ended_at` and started within
the last 30 minutes, this script returns it instead of creating a duplicate.
That way Claude can call start_session.py at the top of every reply without
fragmenting the log.
"""

import sys
import uuid
from datetime import datetime, timedelta

from _common import emit, get_timezone, load_memory, save_memory

REUSE_WINDOW_MINUTES = 30


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

    # Check the most recent session
    if sessions:
        last = sessions[-1]
        if not last.get("ended_at"):
            try:
                started = datetime.fromisoformat(last["started_at"])
                if now - started < timedelta(minutes=REUSE_WINDOW_MINUTES):
                    emit(
                        {
                            "ok": True,
                            "reused": True,
                            "session_id": last["session_id"],
                            "started_at": last["started_at"],
                            "now": now.isoformat(timespec="seconds"),
                        }
                    )
                    return 0
            except (KeyError, ValueError):
                pass

    new_session = {
        "session_id": uuid.uuid4().hex[:12],
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
            "started_at": new_session["started_at"],
            "now": now.isoformat(timespec="seconds"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
