---
description: View or change time-anchor settings — idle reset hours and time format.
argument-hint: "[optional: --idle <hours|never> --format <12h|24h>]"
---

If `$ARGUMENTS` is empty: just print current settings.

```bash
python <skill-path>/scripts/update_settings.py
```

If `$ARGUMENTS` contains values, pass them through:

```bash
python <skill-path>/scripts/update_settings.py $ARGUMENTS
```

If the user wants to change settings interactively (no args), use `AskUserQuestion` with TWO questions:

1. **Idle reset:** options `1 hour`, `4 hours` (default), `8 hours`, `24 hours`, `Never`. Map: `1` / `4` / `8` / `24` / `never`.
2. **Time format:** options `12-hour AM/PM` (default), `24-hour military`. Map: `12h` / `24h`.

Then run `update_settings.py --idle <chosen> --format <chosen>` to apply.

**Output format (exact):**

| Field | Value |
|---|---|
| Idle reset | {settings.idle_reset_hours or "never"} hours |
| Time format | {settings.time_format} |

If any settings changed, prepend:

> _Updated: {changed keys}._

No commentary outside the table.
