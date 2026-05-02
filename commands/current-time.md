---
description: Show the current local time in the user's timezone (via time-anchor skill)
---

Run `now.py` and render its output as the markdown table below. Use ONLY the canonical fields the script emits — do not reformat ISO strings or guess timezone abbreviations yourself.

```bash
python <skill-path>/scripts/now.py
```

**Output format (exact):**

| Field | Value |
|---|---|
| Now | {human} |
| Timezone | {timezone} ({tz_label}, UTC{utc_offset hh:mm}) |
| ISO | {iso} |
| UTC | {utc_iso} |
| DST | {"yes" if is_dst else "no"} |

No commentary, no extra prose. Just the table.

If the script errors with `no timezone set`, tell the user to run `/set-timezone` first.
