#!/usr/bin/env python3
"""Set the user's timezone. Validates against the IANA database before saving.

Usage:
    python set_timezone.py America/New_York
"""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from _common import emit, load_memory, save_memory


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python set_timezone.py <IANA_TIMEZONE>", file=sys.stderr)
        print("Example: python set_timezone.py America/Chicago", file=sys.stderr)
        return 1

    tz_name = sys.argv[1].strip()

    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        print(
            f"ERROR: '{tz_name}' is not a valid IANA timezone.\n"
            f"See references/timezones.md for the full list. "
            f"Common formats look like: America/Los_Angeles, Europe/Berlin, "
            f"Asia/Tokyo, Australia/Sydney, UTC.",
            file=sys.stderr,
        )
        return 1

    data, path, backend = load_memory()

    is_first_install = data.get("timezone") is None
    previous = data.get("timezone")

    now = datetime.now(tz)
    data["timezone"] = tz_name
    data["memory_backend"] = backend
    if is_first_install:
        data["installed_at"] = now.isoformat()

    save_memory(data, path, backend)

    # %-I and %-d are GNU-only; fall back gracefully on Windows
    try:
        human = now.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")
    except ValueError:
        human = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    emit(
        {
            "ok": True,
            "timezone": tz_name,
            "previous_timezone": previous,
            "first_install": is_first_install,
            "now": now.isoformat(),
            "human": human,
            "memory_path": str(path),
            "backend": backend,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
