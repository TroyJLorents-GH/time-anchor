---
description: Auto-close stale-open time-anchor sessions older than the threshold (default 12 hours)
argument-hint: "[hours — threshold age, default 12. Pass 0 to close all stale-open records.]"
---

Run `cleanup_sessions.py $ARGUMENTS` (default 12 if no argument). Never closes the session belonging to THIS Claude Code instance.

```bash
python <skill-path>/scripts/cleanup_sessions.py $ARGUMENTS
```

**Output format (exact):**

If `closed_count: 0`:

> No stale-open sessions to close (threshold: {threshold_hours}h).

Otherwise:

| Closed | Session | Started | Ended | Duration |
|---|---|---|---|---|
| auto | `{session_id}` | {started_human} | {ended_human} | {duration_human} |
| ... |

Footer: `Closed {closed_count} stale session(s). Threshold: {threshold_hours}h.`

No commentary outside the table or single-line message.
