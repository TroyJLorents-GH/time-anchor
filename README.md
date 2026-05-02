# time-anchor

> Anchor Claude to the real, current time in your local timezone.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin format: Claude Code](https://img.shields.io/badge/Claude_Code-plugin-7C3AED.svg)](https://claude.com/claude-code)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](.claude-plugin/plugin.json)

Claude has no built-in clock. Each session starts cold, training data is frozen in time, and any "current time" Claude states from memory is a hallucination. **time-anchor** fixes that.

It auto-detects your timezone on install (no API key, no network call), reads the host system clock when you ask for the time, and logs every session start and end so Claude can answer questions like *"how long have we been talking"* or *"what did I say 10 minutes ago"*.

## Demo

```
You: what time is it?
Claude: Friday, May 1, 2026 at 10:01 PM MST.

You: schedule a follow-up for tomorrow at 3pm
Claude: Got it — that's Saturday, May 2, 2026 at 3:00 PM MST (UTC-7).
        I'll write it as 2026-05-02T15:00:00-07:00.

You: how long have we been talking?
Claude: This session started at 9:43 PM MST. We've been at it for 18 minutes.
```

## Install

### One-line install (recommended)

In any Claude Code session:

```
/plugin marketplace add TroyJLorents-GH/time-anchor
/plugin install time-anchor@time-anchor-plugins
```

Restart Claude Code. The first time the skill runs, it will auto-detect your timezone and ask you to confirm.

### Manual install

If you'd rather drop it into your global skills directory directly:

```bash
git clone https://github.com/TroyJLorents-GH/time-anchor.git
cp -r time-anchor/skills/time-anchor ~/.claude/skills/time-anchor
cp time-anchor/commands/*.md ~/.claude/commands/
```

## Slash commands

| Command | What it does |
|---|---|
| `/current-time` | Print the current local time |
| `/set-timezone [IANA]` | Set or change timezone — auto-detects, then walks you through a country picker if needed. Pass an IANA name like `America/Phoenix` to skip the picker. |
| `/start-session-time` | Log the start of this session |
| `/end-session-time` | Close the session and report duration |
| `/session-time [N]` | Show current session info + last N sessions (default 5) |

When installed as a plugin, commands are namespaced as `/time-anchor:current-time`, `/time-anchor:set-timezone`, etc.

## How it works

The trick: **Python scripts in this skill have access to the host OS clock when executed via `bash`.** Claude itself doesn't know the time, but Claude can run `python now.py` and the output IS the time.

```
User → /current-time  →  Claude invokes time-anchor skill
                             ↓
                         Bash: python now.py
                             ↓
                    Reads system clock, applies stored timezone
                             ↓
                    Returns: "Friday, May 1, 2026 at 10:01 PM MST"
```

### Three-stage timezone setup

When the skill runs the first time, it walks through three stages — only the first usually fires:

1. **Auto-detect** — `detect_timezone.py` checks `$TZ`, `/etc/timezone`, `/etc/localtime` (Linux/Mac), or `tzutil /g` + the bundled CLDR Windows-to-IANA map (Windows). Resolves silently for ~85% of users.
2. **Confirm** — Single `Yes` / `Pick a different one` prompt.
3. **Free-text fallback** — User types a city or country. Skill calls `lookup_country.py` against a bundled `country_zones.json` (~200 countries → full IANA zone lists), then paginates the picker so every zone is reachable. **All zones are surfaced** — no silent truncation. Critical for places like Arizona that don't observe DST.

### Memory

State is persisted in a JSON file. The skill resolves its memory location in this priority order:

1. `$TIME_ANCHOR_MEMORY_PATH` env var → use whatever file you point it at (e.g. another memory plugin's JSON). time-anchor namespaces its data under a `time_anchor` key so it doesn't clobber the host plugin's existing keys.
2. `~/.claude/memory/time-anchor.json` if present.
3. `~/.claude/skills/time-anchor/memory.json` (default — created on demand).

Schema:

```json
{
  "version": "1.0",
  "timezone": "America/Phoenix",
  "installed_at": "2026-05-01T22:01:09-07:00",
  "memory_backend": "self",
  "sessions": [
    {
      "session_id": "0f3c...",
      "started_at": "2026-05-01T21:43:00-07:00",
      "ended_at": "2026-05-01T22:01:00-07:00",
      "messages": []
    }
  ]
}
```

## Privacy

- **No network calls.** Auto-detect uses only the host OS. Country lookup uses a bundled JSON file.
- **No telemetry.** Nothing leaves your machine.
- **Memory is local.** Lives in `~/.claude/` on your filesystem. Nothing syncs to a server.

## FAQ

**Does this work in claude.ai (the chat interface)?**
No — claude.ai can't execute Python. This skill targets environments where Claude has bash + Python: Claude Code, Claude Agent SDK, agentic harnesses.

**How accurate is auto-detect?**
~85%+ on first try. Linux/Mac read the OS timezone directly. Windows uses `tzutil` + a bundled CLDR map covering ~130 Windows zone names. The remaining ~15% (containers, exotic envs, mismatched OS settings) fall through to manual confirm.

**Can I change my timezone later?**
Yes — `/set-timezone` runs the full flow every time, even if a timezone is already saved. Or pass an IANA name directly: `/set-timezone Europe/Berlin`.

**What about cities that share an IANA zone with somewhere else?**
The flow asks for *city or country*. For specific cities, Claude maps directly to the matching IANA zone and asks you to confirm with Yes/No. For countries, you see every zone in that country.

**Does it survive across sessions?**
Yes — your timezone and session history persist in the memory file. Future sessions read it back automatically.

## Roadmap

- v0.2 — Optional Google Places API integration for fuzzy city autocomplete and lat/lng-based timezone resolution (border cities, ambiguous names).
- v0.2 — Session message logging via `log_message.py` wired into a Claude Code hook (currently manual).
- v0.3 — Multi-user memory backends, sync to encrypted store.

## Contributing

Issues and PRs welcome at <https://github.com/TroyJLorents-GH/time-anchor/issues>.

If you find a country that auto-detects wrong, or one with timezones missing from `country_zones.json`, please file an issue with: your OS, what `tzutil /g` (Windows) or `cat /etc/timezone` (Linux/Mac) returns, and what the correct IANA zone should be.

## License

MIT — see [LICENSE](LICENSE).

## Credits

Built by [Troy Lorents](https://github.com/TroyJLorents-GH) ([@AutomateFlows](https://github.com/TroyJLorents-GH)).

Bundled data: IANA `tzdata` zone1970.tab country mappings; CLDR `windowsZones.xml` (Unicode Common Locale Data Repository).
