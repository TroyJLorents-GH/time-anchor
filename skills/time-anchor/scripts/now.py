#!/usr/bin/env python3
"""Print the current time in the user's stored timezone, plus UTC.

Output is JSON with both ISO and human-readable forms. Use the human field
when speaking to the user; use iso when computing or comparing.
"""

import sys
from datetime import datetime, timezone

from _common import emit, get_timezone, load_memory


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print(
            "ERROR: no timezone set. Run init.py first, then set_timezone.py.",
            file=sys.stderr,
        )
        return 2

    local = datetime.now(tz)
    utc = datetime.now(timezone.utc)

    # %-I and %-d are GNU-only; fall back gracefully on Windows
    try:
        human = local.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")
    except ValueError:
        human = local.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    emit(
        {
            "timezone": data["timezone"],
            "iso": local.isoformat(timespec="seconds"),
            "human": human,
            "utc_iso": utc.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "weekday": local.strftime("%A"),
            "is_dst": bool(local.dst()),
            "utc_offset": local.strftime("%z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
