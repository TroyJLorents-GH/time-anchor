---
description: Manually reset the time-anchor session timer. Sets started_at to now.
---

Run `reset_session.py` and render the result as a markdown table.

```bash
python <skill-path>/scripts/reset_session.py
```

**Output format (exact):**

| Field | Value |
|---|---|
| Session reset at | {started_human} |
| Previous start | {previous_started_at or "(none)"} |

No commentary.
