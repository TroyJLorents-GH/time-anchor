#!/usr/bin/env python3
"""Read or update time-anchor user settings.

Usage:
    python update_settings.py                           # print current settings
    python update_settings.py --idle 4                  # idle_reset_hours = 4
    python update_settings.py --idle never              # disable idle reset
    python update_settings.py --format 12h              # 12-hour AM/PM
    python update_settings.py --format 24h              # 24-hour military
    python update_settings.py --idle 8 --format 24h     # both at once
"""

import sys

from _common import emit, load_memory, save_memory


def main() -> int:
    args = sys.argv[1:]
    data, path, backend = load_memory()
    settings = data.setdefault(
        "settings", {"idle_reset_hours": 4, "time_format": "12h"}
    )

    changed: dict = {}
    i = 0
    while i < len(args):
        flag = args[i]
        if flag == "--idle" and i + 1 < len(args):
            val = args[i + 1].strip().lower()
            if val in ("never", "none", "0", "off"):
                settings["idle_reset_hours"] = None
                changed["idle_reset_hours"] = None
            else:
                try:
                    n = float(val)
                    if n <= 0:
                        settings["idle_reset_hours"] = None
                        changed["idle_reset_hours"] = None
                    else:
                        settings["idle_reset_hours"] = n if n != int(n) else int(n)
                        changed["idle_reset_hours"] = settings["idle_reset_hours"]
                except ValueError:
                    print(
                        f"ERROR: --idle expects a number of hours or 'never', got '{val}'",
                        file=sys.stderr,
                    )
                    return 1
            i += 2
        elif flag == "--format" and i + 1 < len(args):
            val = args[i + 1].strip().lower()
            if val in ("12h", "12", "ampm", "am/pm"):
                settings["time_format"] = "12h"
                changed["time_format"] = "12h"
            elif val in ("24h", "24", "military"):
                settings["time_format"] = "24h"
                changed["time_format"] = "24h"
            else:
                print(
                    f"ERROR: --format expects '12h' or '24h', got '{val}'",
                    file=sys.stderr,
                )
                return 1
            i += 2
        else:
            print(f"ERROR: unknown argument '{flag}'", file=sys.stderr)
            return 1

    if changed:
        save_memory(data, path, backend)

    emit(
        {
            "ok": True,
            "settings": settings,
            "changed": changed,
            "memory_path": str(path),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
