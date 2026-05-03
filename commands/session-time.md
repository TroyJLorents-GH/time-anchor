---
description: Show the rolling session — when it started, elapsed, total commands, active terminals.
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
| Claude Code processes | {active_terminals if not null else "—"} |
| Idle reset | {idle_reset_label} |

If `just_reset` is true, prepend a single line above the table:

> _Session reset — reason: {reset_reason}._

`active_terminals` (rendered as "Claude Code processes") counts every `claude.exe` (or `claude` on Unix) process whose command line includes `claude-code`. This excludes the Claude Desktop app's child processes, but **includes orphaned/zombie Claude Code processes** from terminal windows closed via the X button (Windows leaks them). If the count is higher than the number of terminal windows you have open, run `/cleanup-claude-processes` to kill the zombies. If null, render `—` (means we couldn't detect).

No commentary outside the table or that one-line reset notice.
