#!/usr/bin/env python3
"""Append a timestamped message preview to the current session.

Usage:
    python log_message.py user "first 80 chars of what the user said"
    python log_message.py assistant "first 80 chars of the reply"

If no open session exists, one is created automatically.
"""

import sys
from datetime import datetime

from _common import emit, get_timezone, load_memory, save_memory

MAX_PREVIEW = 80


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("user", "assistant"):
        print(
            'Usage: python log_message.py <user|assistant> "preview text"',
            file=sys.stderr,
        )
        return 1

    role = sys.argv[1]
    preview = " ".join(sys.argv[2:])[:MAX_PREVIEW]

    data, path, backend = load_memory()
    tz = get_timezone(data)
    if tz is None:
        print("ERROR: no timezone set.", file=sys.stderr)
        return 2

    sessions = data.setdefault("sessions", [])
    open_sessions = [s for s in sessions if not s.get("ended_at")]
    if not open_sessions:
        # Auto-open one
        import uuid

        new = {
            "session_id": uuid.uuid4().hex[:12],
            "started_at": datetime.now(tz).isoformat(timespec="seconds"),
            "ended_at": None,
            "messages": [],
        }
        sessions.append(new)
        target = new
    else:
        target = open_sessions[-1]

    now = datetime.now(tz)
    entry = {"ts": now.isoformat(timespec="seconds"), "role": role, "preview": preview}
    target.setdefault("messages", []).append(entry)
    save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "session_id": target["session_id"],
            "logged": entry,
            "session_message_count": len(target["messages"]),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
