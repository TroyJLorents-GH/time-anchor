---
description: Log the start of this session in time-anchor
---

Run `start_session.py` and render the result as a markdown table. Use the script's canonical `now_human` and `started_human` fields verbatim. Do not reformat any timestamps yourself.

```bash
python <skill-path>/scripts/start_session.py
```

**Output format (exact):**

| Field | Value |
|---|---|
| Now | {now_human} |
| Session ID | `{session_id}` |
| Claude instance | {claude_session_id} |
| Started | {started_human} |
| Reused | {"yes — existing open session for this Claude Code instance" if reused else "no — fresh session"} |

No commentary. Just the table.
