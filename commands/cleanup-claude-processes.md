---
description: Find and kill stale Claude Code processes (zombies from terminals closed via X button).
argument-hint: "[--kill-orphans | --kill-all | --older-than <hours>]"
---

Windows leaks `claude.exe` processes when terminal windows are closed via the X button instead of `/exit` or Ctrl-C. They keep running, eating RAM, until reboot or manual kill. macOS/Linux are usually cleaner but the same script works there too.

## Flow

**1. List first.** Always run a dry-run first to show the user what's there:

```bash
python <skill-path>/scripts/cleanup_processes.py
```

This prints JSON with all `claude-code` processes — PID, start time, whether it's an orphan (older than threshold), and which one is the current terminal's ancestor (`current_pid`).

**2. Render a table** to the user — exclude the current process row, mark orphans:

| PID | Started | Orphan? |
|---|---|---|
| {pid} | {started_at} | yes / no |

Then print: _Current terminal: PID `{current_pid}`. This will not be killed._

**3. Pass-through args.** If `$ARGUMENTS` is non-empty (e.g. `--kill-orphans`, `--kill-all`, `--older-than 4`), append them and run:

```bash
python <skill-path>/scripts/cleanup_processes.py $ARGUMENTS
```

**4. Otherwise, ask via `AskUserQuestion`:**

> *"Found {N} extra Claude Code processes. {M} look like orphans (started > 1h ago). What do you want to do?"*

Options:
- `Kill orphans only` — safer; only kills processes older than the threshold
- `Kill all but current terminal` — nukes every other Claude Code instance, including any other terminals you have open. They'll need to be restarted.
- `Cancel` — do nothing

Map to `--kill-orphans` / `--kill-all` / no-op.

**5. After kill, render the result:**

> _Killed {killed.length} processes: PIDs {killed}._

If `failed.length > 0`, also note: _Could not kill: {failed} (may have already exited or required elevation)._

If user picks "Kill all but current", warn first: *"This will close any other Claude Code terminals you have open right now. They'll need to be restarted. Continue?"* — confirm with a second `AskUserQuestion` (`Yes / Cancel`) before running.

## Notes

- The script identifies "current" by walking up the parent process chain from the Python interpreter. The first `claude.exe` (or `claude` on Unix) with `claude-code` in the command line is the active terminal — that PID is preserved.
- `--older-than` defaults to 1 hour. Bump it (`--older-than 4`) if you want to be more conservative about what counts as a zombie.
- This is host-wide. There's no per-project filter — every Claude Code process on the machine is in scope.
