#!/usr/bin/env python3
"""Check whether time-anchor is set up. Exit 0 if ready, exit 2 if needs setup."""

import sys

from _common import load_memory, now_in_tz


def main() -> int:
    data, path, backend = load_memory()

    if not data.get("timezone"):
        print(
            f"STATUS: NEEDS_SETUP\n"
            f"memory_path: {path}\n"
            f"backend: {backend}\n"
            f"\n"
            f"No timezone is recorded yet. Run setup flow:\n"
            f"  1. python detect_timezone.py    (auto-detects from host OS)\n"
            f"  2. Confirm with user via AskUserQuestion (or ask free-text city/country)\n"
            f"  3. python set_timezone.py <IANA_NAME>",
            file=sys.stderr,
        )
        return 2

    now = now_in_tz(data)
    print(
        '{\n'
        f'  "status": "READY",\n'
        f'  "timezone": "{data["timezone"]}",\n'
        f'  "now": "{now.isoformat() if now else None}",\n'
        f'  "memory_path": "{path}",\n'
        f'  "backend": "{backend}",\n'
        f'  "session_count": {len(data.get("sessions", []))}\n'
        '}'
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
