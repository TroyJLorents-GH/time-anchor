---
description: View or change time-anchor settings — idle reset hours and time format.
argument-hint: "[--idle <hours|never>] [--format <12h|24h|military>]"
---

If `$ARGUMENTS` is non-empty (e.g. `--idle 8 --format 24h`), pass them through and skip the interactive flow:

```bash
python <skill-path>/scripts/update_settings.py $ARGUMENTS
```

If `$ARGUMENTS` is empty, run the interactive flow:

1. Print current settings:
   ```bash
   python <skill-path>/scripts/update_settings.py
   ```
2. Show the user the current values as a table.
3. **Ask both pickers in a single `AskUserQuestion` call** (one LLM turn, no inter-question lag). Two questions in one tool call:

   **Q1 — `Idle reset hours`:**
   - `Keep current` (no change)
   - `1 hour`
   - `4 hours`
   - `8 hours`

   The picker caps at 4 options. If the user wants `24 hours` or `Never`, they pick "Other" and type it. Map their pick:
   - `Keep current` → omit `--idle`
   - `1 hour` / `4 hours` / `8 hours` → `--idle 1` / `--idle 4` / `--idle 8`
   - Other text containing `24` → `--idle 24`
   - Other text containing `never` (case-insensitive) → `--idle never`
   - Any other number N → `--idle N`

   **Q2 — `Time format`:** show concrete examples so the user doesn't need to know the acronyms (all three render the same moment, 1 PM):
   - `Keep current` (no change)
   - `12-hour AM/PM` → example: `1:00 PM`
   - `24-hour` → example: `13:00`
   - `Military` → example: `1300`

   Map: `Keep current` → omit `--format`; others → `--format 12h` / `--format 24h` / `--format military`.

4. Run `update_settings.py` with whichever flags were picked. If both were "Keep current", skip the script call.

**Output format (exact):**

| Field | Value |
|---|---|
| Idle reset | {settings.idle_reset_hours or "never"} hours |
| Time format | {settings.time_format} |

If any settings changed, prepend:

> _Updated: {comma-list of changed keys}._

If nothing changed (both "Keep current"), prepend:

> _No changes._

No commentary outside the table or that one-line update notice.
