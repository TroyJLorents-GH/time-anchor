---
description: Show current session info and active sessions. Pass N to also include last N closed sessions.
argument-hint: "[N — optional, number of recently CLOSED sessions to also show, default 0]"
---

Run `session_info.py 50` (we always pull a buffer; render filters below).

```bash
python <skill-path>/scripts/session_info.py 50
```

**Render rules — do NOT reformat timestamps:**

- Use the script's canonical `now_human`, `started_human`, `ended_human`, `elapsed_human`, `duration_human` fields verbatim.
- Use `tz_label` for any timezone abbreviation. Never infer "PDT"/"EDT" — the script tells you exactly what to display.
- No commentary, no offers to verify.

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

**Active sessions (across all Claude Code instances):**

Filter `recent_sessions` to entries where `ended_at` is null. Render as:

| ID | Started | Elapsed | Instance |
|---|---|---|---|
| `{session_id}` | {started_human} | {duration_human} | {claude_session_id or "—"} |
| ... |

If no other active sessions besides current, render: _Only this terminal is currently tracked. Other terminals you have open won't appear here until they run `/start-session-time` once._

**Recently closed sessions (last 5 by default):**

Determine N: if `$ARGUMENTS` is a positive integer, use it. If empty, use **5**. If `0`, omit this section entirely.

Filter `recent_sessions` to entries WITH `ended_at`, take the LAST N.

| ID | Started | Ended | Duration |
|---|---|---|---|
| `{session_id}` | {started_human} | {ended_human} | {duration_human} |
| ... |

If `current_session` is null, replace the first table with:

| Field | Value |
|---|---|
| Now | {now_human} |
| Current | _none active in this Claude Code instance — run `/start-session-time` to log a new one_ |
| Total sessions | {total_sessions} |
