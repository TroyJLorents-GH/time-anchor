#!/usr/bin/env python3
"""Print the current time in the user's stored timezone, plus UTC.

Output is JSON with both ISO and human-readable forms. Always use the
canonical `human` field verbatim — do not reformat the ISO string yourself
(callers across Claude turns drift if they do).
"""

import sys
from datetime import datetime, timezone

from _common import emit, format_human, get_timezone, load_memory


def main() -> int:
    data, _, _ = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print(
            "ERROR: no timezone set. Run init.py first, then set_timezone.py.",
            file=sys.stderr,
        )
        return 2

    local = datetime.now(tz)
    utc = datetime.now(timezone.utc)

    emit(
        {
            "timezone": data["timezone"],
            "iso": local.isoformat(timespec="seconds"),
            "human": format_human(local),
            "tz_label": local.strftime("%Z"),
            "utc_iso": utc.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "weekday": local.strftime("%A"),
            "is_dst": bool(local.dst()),
            "utc_offset": local.strftime("%z"),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
