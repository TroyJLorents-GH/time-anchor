---
name: time-anchor
description: Anchor Claude to the real, current time in the user's local timezone. Use this skill whenever the user asks what time/day/date it is, mentions time zones, schedules anything ("tomorrow at 3pm", "in two hours", "next Tuesday"), references session timing ("how long has my session been running"), or whenever the conversation involves any time-sensitive context where Claude's frozen training-cutoff clock would be wrong. Also use this skill on the very first time-related interaction so the user can pick their timezone. Persists timezone, settings, and a single rolling session in a memory file (its own, or one shared with another memory plugin if configured).
---

# time-anchor

Claude has no built-in clock. Each session starts cold, training data is frozen, and any "current time" Claude states from memory is a hallucination. This skill solves that by:

1. Storing the user's timezone in a memory file (set once on first use).
2. Reading the actual system clock via short Python scripts that bash can execute.
3. Tracking a single rolling session timer (started_at, last_active_at, total commands) that auto-resets after configurable idle.

The trick: the *Python scripts* in this skill have access to the host OS clock when executed via `bash`. Claude itself doesn't know the time, but Claude can run `python now.py` and the output IS the time. **Always trust the script output over any internal sense of "what time it probably is."**

## When to use this skill

Trigger this skill (run the appropriate script) for any of:

- User asks "what time is it" / "what's today's date" / "what day of the week is it"
- User schedules something relative to now ("in 3 hours", "tomorrow morning", "next Friday at 2pm")
- User mentions or asks about timezones, UTC offsets, daylight saving
- User asks "how long has my session been running"
- The first time a user asks anything time-related — run `init.py` to either confirm the existing setting or run setup

Do NOT skip this skill just because Claude "thinks it knows" the time. Claude does not. The system prompt may give a date but rarely the time, and almost never the user's local timezone. Always run the script.

## Setup (first run)

Check whether the memory file has a timezone:

```bash
python <skill-path>/scripts/init.py
```

If `init.py` returns `STATUS: NEEDS_SETUP`, run the three-stage flow:

**Stage 1 — auto-detect.**
```bash
python <skill-path>/scripts/detect_timezone.py
```
Returns JSON with `best` (most reliable IANA name) detected from `$TZ`, `/etc/timezone`, `/etc/localtime`, or Windows `tzutil` + the bundled CLDR map. Covers ~85% of users silently.

**Stage 2 — confirm.** If `best` is non-null, ask via `AskUserQuestion` with two options: `Use {best.timezone}` and `Pick a different one`. If user accepts, jump straight to `set_timezone.py`. If `best` is null, skip to stage 3.

**Stage 3 — free-text fallback.** Ask the user: *"What city or country are you in?"* Use `lookup_country.py` to get candidate IANA zones from `assets/country_zones.json` (covers ~200 countries). Print the full list, paginate the picker via `AskUserQuestion` (4 options + "Show next batch" / "Type IANA name").

**Then save:**
```bash
python <skill-path>/scripts/set_timezone.py "America/Phoenix"
```

`set_timezone.py` validates the IANA name via Python's `zoneinfo`. After it saves, you're ready to use the skill.

## Daily operations

### Get the current time

```bash
python <skill-path>/scripts/now.py
```

Returns JSON with `human` (rendered per user's `time_format` setting — "4:19 PM MST" or "16:19 MST"), `iso`, `tz_label`, etc. Use the `human` field verbatim when speaking to the user.

### Resolve a relative time

When the user says "tomorrow at 3pm" or "in 2 hours", compute it from `now.py`'s output. For complex parsing, write a small inline Python snippet using the stored timezone.

### Show session info

```bash
python <skill-path>/scripts/session_info.py
```

Returns the rolling session: `session_started_human`, `elapsed_human`, `lifetime_command_count`, `idle_reset_label`. Every command call (including this one) bumps `last_active_at`. If the gap exceeds `settings.idle_reset_hours` (default 4h), the session auto-resets — `just_reset: true` and `reset_reason` are set when that happens.

### Manually reset the session

```bash
python <skill-path>/scripts/reset_session.py
```

Sets `started_at` to now. For when the user wants to start a fresh "session" without waiting for idle.

### View or change settings

```bash
python <skill-path>/scripts/update_settings.py                           # read
python <skill-path>/scripts/update_settings.py --idle 8 --format 24h     # update
python <skill-path>/scripts/update_settings.py --idle never              # disable auto-reset
```

Two settings:
- `idle_reset_hours` (number or null for "never") — auto-reset threshold. Default 4.
- `time_format` (`"12h"` or `"24h"`) — affects how `now.py`/`session_info.py` render times. Default `"12h"`.

### Change timezone later

```bash
python <skill-path>/scripts/set_timezone.py "Europe/London"
```

Overwrites the stored timezone. Or run the full `/set-timezone` setup flow again.

## Memory file format (v2.0)

```json
{
  "version": "2.0",
  "timezone": "America/Phoenix",
  "installed_at": "2026-05-02T16:19:37-07:00",
  "memory_backend": "self",
  "settings": {
    "idle_reset_hours": 4,
    "time_format": "12h"
  },
  "session": {
    "started_at": "2026-05-02T09:14:00-07:00",
    "last_active_at": "2026-05-02T16:19:37-07:00"
  },
  "lifetime_command_count": 47
}
```

`memory_backend: "external"` means the file is shared with another memory plugin (the user pointed `$TIME_ANCHOR_MEMORY_PATH` at it). Time-anchor's data is namespaced under a top-level `time_anchor` key when sharing a file.

## Reference files

- `references/timezones.md` — every IANA timezone, grouped by region.
- `assets/country_zones.json` — country → IANA zone mapping (~200 countries).
- `assets/windows_zones.json` — Windows zone name → IANA mapping (CLDR).
- `assets/memory_template.json` — empty memory structure for bootstrap.

## Notes for Claude

- Never guess the time. If a script fails, tell the user instead of fabricating a value.
- The system prompt's date may be stale or may use UTC; the user's local date can differ. Always prefer the script output.
- When rendering time, use the `human` / `*_human` fields verbatim. Do NOT reformat ISO strings yourself — Claude reformats inconsistently across turns and sometimes hallucinates wrong tz abbreviations.
- The skill keeps a single rolling session, not per-terminal. Don't try to track sessions individually; the design intentionally drops that complexity.
