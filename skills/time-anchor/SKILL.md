---
name: time-anchor
description: Anchor Claude to the real, current time in the user's local timezone. Use this skill whenever the user asks what time/day/date it is, mentions time zones, schedules anything ("tomorrow at 3pm", "in two hours", "next Tuesday"), references session timing ("when did we start this", "how long have we been talking"), or whenever the conversation involves any time-sensitive context where Claude's frozen training-cutoff clock would be wrong. Also use this skill on the very first interaction in a project so the user can pick their timezone, and at the start and end of every session to log session boundaries. Persists the user's timezone preference and session log in a memory file (its own, or one shared with another memory plugin if configured).
---

# Time Anchor

Claude has no built-in clock. Each session starts cold, training data is frozen, and any "current time" Claude states from memory is a hallucination. This skill solves that by:

1. Storing the user's timezone in a memory file (set once at install).
2. Reading the actual system clock via short Python scripts and converting to that timezone.
3. Logging session start, session end, and message timestamps so Claude can answer "when did we start", "how long ago did I say X", etc.

The trick: the *Python scripts* in this skill have access to the host OS clock when executed via `bash`. Claude itself doesn't know the time, but Claude can run `python now.py` and the output IS the time. Always trust the script output over any internal sense of "what time it probably is."

## When to use this skill

Trigger this skill (run the appropriate script) for any of:

- User asks "what time is it" / "what's today's date" / "what day of the week is it"
- User schedules something relative to now ("in 3 hours", "tomorrow morning", "next Friday at 2pm")
- User mentions or asks about timezones, UTC offsets, daylight saving
- User asks about session timing ("when did this conversation start", "how long ago did I send X")
- The first message of any conversation that doesn't already have timezone context (run `init.py` to either confirm an existing setting or run setup)
- The conversation appears to be wrapping up (run `end_session.py` to log the end)

Do NOT skip this skill just because Claude "thinks it knows" the time. Claude does not. The system prompt may give a date but rarely the time, and almost never the user's local timezone. Always run the script.

## Setup (first run)

The first time this skill is invoked, check whether the memory file exists:

```bash
python /path/to/time-anchor/scripts/init.py
```

`init.py` does the following:

1. Looks for an existing memory file (in priority order):
   - `$TIME_ANCHOR_MEMORY_PATH` if env var is set (lets users point at a shared memory plugin file)
   - `~/.claude/memory/time-anchor.json`
   - `~/.claude/skills/time-anchor/memory.json` (default — created if nothing else exists)
2. If no timezone is recorded, prints `STATUS: NEEDS_SETUP` and exits non-zero.
3. If a timezone IS recorded, prints the current memory state as JSON and exits 0.

When `init.py` returns `NEEDS_SETUP`, run the three-stage setup flow. Do **not** print a numbered list of "common picks" — Claude Code has no native searchable picker, so quick-pick lists are noise.

**Stage 1 — auto-detect.** Run:

```bash
python /path/to/time-anchor/scripts/detect_timezone.py
```

Output is JSON with `best`, `candidates`, and `raw` fields. `best` is the most reliable IANA name detected from the host OS (uses `$TZ`, `/etc/timezone`, `/etc/localtime`, or `tzutil /g` + the bundled CLDR map in `assets/windows_zones.json`). Detection covers ~85% of users silently.

**Stage 2 — confirm.** If `best` is non-null, ask the user with the `AskUserQuestion` tool — exactly two options:

- `Use {best.timezone}` — accept the detected zone
- `Pick a different one` — fall through to stage 3

If the user accepts, jump straight to `set_timezone.py`. If `best` is null, skip to stage 3.

**Stage 3 — free-text fallback.** Ask the user a short open question via `AskUserQuestion` with `multiSelect: false` and no preset options (or just ask in chat): *"What city or country are you in?"*

Take their answer (e.g. "Phoenix", "Bangalore", "near Munich") and map it to the correct IANA name. Use `references/timezones.md` for the canonical list — it has all 498 IANA zones grouped by region. Pick the zone for the closest major city in their UTC offset. If ambiguous, ask one clarifying question.

**Then save:**

```bash
python /path/to/time-anchor/scripts/set_timezone.py "America/Phoenix"
```

`set_timezone.py` validates the IANA name via Python's `zoneinfo` and rejects invalid input. After it saves, run `start_session.py` to log the session start.

## Daily operations

### Get the current time

```bash
python /path/to/time-anchor/scripts/now.py
```

Output is JSON like:
```json
{
  "timezone": "America/New_York",
  "iso": "2026-05-01T14:30:22-04:00",
  "human": "Friday, May 1, 2026 at 2:30 PM EDT",
  "utc_iso": "2026-05-01T18:30:22Z",
  "weekday": "Friday",
  "is_dst": true
}
```

Use the `human` field when speaking to the user; use `iso` when computing or comparing.

### Resolve a relative time

When the user says "tomorrow at 3pm" or "in 2 hours", compute it from `now.py`'s output rather than guessing. For complex parsing, write a small inline Python snippet that imports `zoneinfo` and uses the stored timezone.

### Log a session start

```bash
python /path/to/time-anchor/scripts/start_session.py
```

Returns the new `session_id` and start timestamp. Run this once at the beginning of a fresh conversation. If the most recent session in memory has no `ended_at` and started within the last 30 minutes, the script will reuse it instead of creating a duplicate (so re-running is safe).

### Log a message timestamp

```bash
python /path/to/time-anchor/scripts/log_message.py user "first 80 chars of message"
python /path/to/time-anchor/scripts/log_message.py assistant "first 80 chars of reply"
```

Optional but useful for "what did I say 10 minutes ago" type queries.

### End a session

```bash
python /path/to/time-anchor/scripts/end_session.py
```

Closes the most recent open session with the current timestamp.

### Change timezone later

```bash
python /path/to/time-anchor/scripts/set_timezone.py "Europe/London"
```

Overwrites the stored timezone. Sessions logged before the change keep their original offset (they are stored as ISO strings with the offset baked in).

## Memory file format

```json
{
  "version": "1.0",
  "timezone": "America/New_York",
  "installed_at": "2026-05-01T14:30:00-04:00",
  "memory_backend": "self|external",
  "external_path": null,
  "sessions": [
    {
      "session_id": "0f3c...",
      "started_at": "2026-05-01T14:30:00-04:00",
      "ended_at": "2026-05-01T15:45:00-04:00",
      "messages": [
        {"ts": "2026-05-01T14:30:05-04:00", "role": "user", "preview": "hi claude"},
        {"ts": "2026-05-01T14:30:08-04:00", "role": "assistant", "preview": "hello!"}
      ]
    }
  ]
}
```

`memory_backend: "external"` means the file is being read from another memory plugin's storage (the user pointed `TIME_ANCHOR_MEMORY_PATH` at it). Writing still works — the schema above is namespaced under a top-level `time_anchor` key when writing to a shared file, so it doesn't collide with the host plugin's data.

## Reference files

- `references/timezones.md` — every IANA timezone, grouped by region. Read this when the user is choosing or changing their zone.
- `assets/memory_template.json` — the empty memory structure used to bootstrap a new file.

## Notes for Claude

- Never guess the time. If a script fails, tell the user instead of fabricating a value.
- The system prompt's date may be stale or may use UTC; the user's local date can differ. Always prefer the script.
- When you log a session start at the top of a conversation, mention it briefly to the user ("logged session start at 2:30 PM EDT") so they know the skill ran.
- Keep message previews short (the script truncates to 80 chars) — this is for Claude's recall, not full transcript storage.
