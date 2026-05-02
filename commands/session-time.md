---
description: Show the rolling session — when it started, elapsed, total commands. Auto-resets after idle threshold.
---

Run `session_info.py` and render the result as a markdown table. Use the script's canonical fields verbatim — do NOT reformat timestamps.

```bash
python <skill-path>/scripts/session_info.py
```

**Output format (exact):**

| Field | Value |
|---|---|
| Now | {now_human} |
| Session started | {session_started_human} |
| Elapsed | {elapsed_human} |
| Total commands | {lifetime_command_count} |
| Idle reset | {idle_reset_label} |

If `just_reset` is true, prepend a single line above the table:

> _Session reset — reason: {reset_reason}._

No commentary outside the table or that one-line reset notice.
