#!/usr/bin/env python3
"""Print the current time in the user's stored timezone, plus UTC.

Output is JSON with both ISO and human-readable forms. Use the canonical
`human` field verbatim — it's already formatted per the user's
`settings.time_format` preference (12h or 24h).
"""

import sys
from datetime import datetime, timezone

from _common import (
    emit,
    format_human,
    get_time_format,
    get_timezone,
    load_memory,
    save_memory,
    touch_session,
)


def main() -> int:
    data, path, backend = load_memory()
    tz = get_timezone(data)

    if tz is None:
        print(
            "ERROR: no timezone set. Run /set-timezone first.",
            file=sys.stderr,
        )
        return 2

    local = datetime.now(tz)
    utc = datetime.now(timezone.utc)
    fmt = get_time_format(data)

    touch_session(data, local)
    save_memory(data, path, backend)

    emit(
        {
            "timezone": data["timezone"],
            "iso": local.isoformat(timespec="seconds"),
            "human": format_human(local, fmt),
            "tz_label": local.strftime("%Z"),
            "utc_iso": utc.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "weekday": local.strftime("%A"),
            "is_dst": bool(local.dst()),
            "utc_offset": local.strftime("%z"),
            "time_format": fmt,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
