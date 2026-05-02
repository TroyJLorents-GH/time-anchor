---
description: Log the end of the current session in time-anchor
---

Run `end_session.py` and render the result as a markdown table. Use the script's canonical `now_human`, `started_human`, `ended_human`, `duration_human` fields verbatim — do not reformat any timestamps yourself.

```bash
python <skill-path>/scripts/end_session.py
```

**Output format (exact):**

If `closed: true`:

| Field | Value |
|---|---|
| Now | {now_human} |
| Closed session | `{session_id}` |
| Claude instance | {claude_session_id} |
| Started | {started_human} |
| Ended | {ended_human} |
| Duration | {duration_human} |
| Messages | {message_count} |

> Continuing in this terminal? Run `/start-session-time` to log a new session.

If `closed: false` (no matching open session for this Claude Code instance):

> No open session for this Claude Code instance to close.

No commentary outside the table or single-line message.
