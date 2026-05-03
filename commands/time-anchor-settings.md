---
description: View or change time-anchor settings — idle reset hours and time format.
argument-hint: "[--idle <hours|never>] [--format <12h|24h>]"
---

If `$ARGUMENTS` is non-empty (e.g. `--idle 8 --format 24h`), pass them through and skip the interactive flow:

```bash
python <skill-path>/scripts/update_settings.py $ARGUMENTS
```

If `$ARGUMENTS` is empty, run the interactive flow:

1. Print current settings by running:
   ```bash
   python <skill-path>/scripts/update_settings.py
   ```
2. Show the user the current values as a table.
3. Use `AskUserQuestion` to ask: "Change a setting?" with options:
   - `Idle reset hours`
   - `Time format`
   - `No change` (cancel)
4. If `Idle reset hours`: ask via `AskUserQuestion` with options `1 hour`, `4 hours`, `8 hours`, `24 hours`, `Never`. Map their pick to the matching arg (`--idle 1` / `--idle 4` / `--idle 8` / `--idle 24` / `--idle never`).
5. If `Time format`: ask via `AskUserQuestion` with three options, each labeled with a concrete example so the user doesn't have to know the acronyms:
   - `12-hour AM/PM` → example: `1:00 PM`
   - `24-hour` → example: `13:00`
   - `Military` → example: `1300`

   Map to `--format 12h`, `--format 24h`, or `--format military`.
6. Run `update_settings.py` with the chosen flag(s).

**Output format (exact):**

| Field | Value |
|---|---|
| Idle reset | {settings.idle_reset_hours or "never"} hours |
| Time format | {settings.time_format} |

If any settings changed, prepend:

> _Updated: {comma-list of changed keys}._

No commentary outside the table or that one-line update notice.
