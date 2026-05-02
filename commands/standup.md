---
description: "While you were away" report — session gap + scheduled fires + missed messages from other plugins
---

Run a "standup" report covering the gap since the last active session.

## Steps

1. Run `time-anchor`'s `session_info.py 1` to get current session start + elapsed time. The "away gap" is everything between the previous session's `ended_at` and now (or the current session's `started_at` if there's no prior session).

2. Best-effort scan for activity that fired during that gap by checking these locations (silently skip any that don't exist):

   - `~/.claude/skills/schedule/state.json`, `~/.claude/skills/schedule/fires.log`, or similar — recent cron fires
   - `~/.claude/skills/telegram/messages.json` or `~/.claude/skills/telegram/inbox/` — inbound messages
   - `~/.claude/skills/imessage/messages.json` or similar
   - `~/.claude/skills/remember/memory.json` — anything new logged by remember
   - `~/.claude/logs/*.log` — any plugin event logs with parseable timestamps
   - Any other skill folder under `~/.claude/skills/` with a `*.json` or `*.log` that has timestamp fields ≥ the gap start

3. Filter each source to events with timestamp ≥ gap start. Group by source.

## Output format

Terse. No commentary, no "should I verify" offers. Just data.

```
Standup · gap 11h 26m (Fri 11:04 PM → Sat 10:30 AM MST)

Schedule fires (2):
  · 06:00 — Ventura niche scan
  · 07:00 — 1dc90635 digest + cf891375 X+IG drafts

Telegram (0)
iMessage (0)
remember (1):
  · 09:14 — saved checkpoint feedback
```

If a source has zero events, render `Source name (0)` on its own line. If a source path doesn't exist at all, omit the line entirely.

If no other plugins have data, just render the time-anchor gap line and state "No adjacent plugin activity detected."

## Notes

- Treat each plugin's data format as opaque — don't assume schemas. Use file modification times and any `timestamp`/`ts`/`created_at`/`fired_at` fields you can find. Skip silently on parse errors.
- This is best-effort cross-skill discovery. As more plugins ship with predictable state-file paths, this becomes more accurate.
