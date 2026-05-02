---
description: Set or change the user's timezone for time-anchor
argument-hint: "[optional IANA name e.g. America/Phoenix]"
---

Use the time-anchor skill to set the user's timezone.

If `$ARGUMENTS` is provided and looks like a valid IANA name (e.g. `America/Phoenix`, `Europe/Berlin`), call `set_timezone.py "$ARGUMENTS"` directly.

Otherwise run the full setup flow:

1. `detect_timezone.py` to auto-detect from the host OS.
2. If a candidate is found, confirm with `AskUserQuestion`: "Use {detected}?" / "Pick a different one".
3. On reject or no detection, ask the user free-text for their city or country, map it to the closest IANA name from `references/timezones.md`, then call `set_timezone.py`.

Confirm the saved timezone with the user when done.
