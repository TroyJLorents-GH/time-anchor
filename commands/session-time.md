---
description: Show current session info and recent sessions from time-anchor
argument-hint: "[N — number of recent sessions to include, default 5]"
---

Run `session_info.py $ARGUMENTS` (default to `5` if no argument).

**Render rules — do NOT reformat timestamps:**

- Use the script's canonical `now_human`, `started_human`, `ended_human`, `elapsed_human`, `duration_human` fields verbatim.
- Use `tz_label` for any timezone abbreviation. Never infer "PDT"/"EDT"/etc — the script tells you exactly what to display.
- Render output as two markdown tables exactly as below — no extra prose, no commentary, no offers to verify.

**Output format (exact):**

| Field | Value |
|---|---|
| Now | {now_human} |
| Current session | `{current_session.session_id}` |
| Claude instance | {current_session.claude_session_id} |
| Started | {current_session.started_human} |
| Elapsed | {current_session.elapsed_human} |
| Messages | {current_session.message_count} |
| Total sessions | {total_sessions} |

**Recent sessions:**

| ID | Started | Ended | Duration |
|---|---|---|---|
| `{session_id}` | {started_human} | {ended_human or "active"} | {duration_human} |
| ... |

If `current_session` is null, replace the first table's body with a single row:

| Field | Value |
|---|---|
| Now | {now_human} |
| Current | _none active in this Claude Code instance_ |
| Total sessions | {total_sessions} |

Then still render the recent table as normal.
