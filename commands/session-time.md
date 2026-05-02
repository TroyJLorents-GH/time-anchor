---
description: Show current session info and recent sessions from time-anchor
argument-hint: "[N — number of recent sessions to include, default 5]"
---

Use the time-anchor skill to show session info.

Run `session_info.py $ARGUMENTS` (default to `5` if no argument).

**Render rules — do not reformat the time:**

- Use the script's `now_human` field verbatim for the timestamp line. Do NOT rebuild it from the ISO string — Claude reformats inconsistently across sessions and sometimes hallucinates the wrong tz abbreviation (e.g. "PDT" for Phoenix, which is MST year-round).
- Use the script's `tz_label` field for any "MST"/"PST"/etc abbreviations.
- Show `claude_session_id` (the Claude Code instance ID) below the time-anchor `session_id` when reporting the current session, so users can debug multi-window confusion.

**Output format (terse — no commentary, no offers to verify):**

```
{now_human}

Current: {session_id} (claude {claude_session_id}) · started {recent.started_at} · elapsed {format duration} · {message_count} msgs
Total sessions: {total_sessions}

Recent:
  · {session_id}  {started_at} → {ended_at or "active"}  ({duration})
```

If `current_session` is null, report `Current: none active in this Claude Code instance.` and still render the recent table.
