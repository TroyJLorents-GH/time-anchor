<div align="center">

# 🕛 time-anchor

> Anchor Claude to the real, current time in your local timezone.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin format: Claude Code](https://img.shields.io/badge/Claude_Code-plugin-7C3AED.svg)](https://claude.com/claude-code)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](.claude-plugin/plugin.json)

</div>

Claude has no built-in clock. Each session starts cold, training data is frozen, and any "current time" Claude states is a hallucination. **time-anchor** fixes that.

Auto-detects your timezone on install (no API key, no network call), reads the host system clock when you ask for the time, and tracks session start/end so Claude can answer *"how long have we been talking"* and *"what did I say 10 minutes ago."*

## Install

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.sh | bash
```

Restart Claude Code. That's it.

## First-time setup

The first time you ask anything time-related, the skill auto-detects your timezone and asks you to confirm:

```
You: what time is it?
Claude: Detected America/Phoenix from your system. Use this? [Yes / Pick different]
You: Yes
Claude: Saturday, May 2, 2026 at 2:35 PM MST.
```

Or run `/set-timezone` directly. ~85% of users get auto-detected; the rest type a city or country and pick from a list.

## Slash commands

| Command | What it does |
|---|---|
| `/current-time` | Print the current local time |
| `/set-timezone [IANA]` | Set or change timezone — auto-detects, then walks through a country picker. Pass an IANA name like `America/Phoenix` to skip. |
| `/start-session-time` | Log the start of this session |
| `/end-session-time` | Close the session, report duration |
| `/session-time [N]` | Current session info + active sessions. Pass N to also show last N closed. |
| `/standup` | "While you were away" — session gap + activity from other plugins (schedule, telegram, etc.) |
| `/cleanup-sessions [hours]` | Auto-close stale-open records older than N hours (default 12) |

## Demo

```
❯ /current-time
Saturday, May 2, 2026 at 2:35 PM MST

❯ /session-time
| Now | Saturday, May 2, 2026 at 2:35 PM MST |
| Current session | 60710ac9ab6b |
| Started | 2:28 PM MST |
| Elapsed | 7m 14s |
| Total sessions | 12 |

❯ Claude, schedule a follow-up for tomorrow at 3pm
Got it — that's Sunday, May 3, 2026 at 3:00 PM MST (UTC-7).
I'll write it as 2026-05-03T15:00:00-07:00.

❯ Claude, how long have we been talking?
This session started at 2:28 PM MST. We've been at it for 7 minutes.
```

## How it works

The trick: **Python scripts in the skill read the host OS clock when Claude executes them via bash.** Claude itself stays clockless, but it now has a tool it can query.

```
User asks time → Claude runs python now.py → reads system clock → returns live timestamp
```

Three-stage timezone setup runs once on first use:

1. **Auto-detect** — checks `$TZ`, `/etc/localtime`, or `tzutil` (Windows) against the bundled CLDR map. Resolves silently for ~85% of users.
2. **Confirm** — single Yes / Pick-different prompt.
3. **Free-text fallback** — user types a city or country, picker covers all ~200 countries with full IANA zone lists.

State persists in `~/.claude/skills/time-anchor/memory.json` (per-user, local only).

## Privacy

- **No network calls.** Detection and country lookup use bundled data.
- **No telemetry.** Nothing leaves your machine.
- **Memory is local.** Lives in `~/.claude/` on your filesystem.

## Optional: auto session tracking

Default install logs sessions when you run `/start-session-time` and `/end-session-time` manually. To auto-log on every Claude Code launch, add a `SessionStart` hook to `~/.claude/settings.json` (merge with existing `hooks` if present):

**Windows:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python C:/Users/YOUR_USERNAME/.claude/skills/time-anchor/scripts/start_session.py"
      }]
    }]
  }
}
```

**macOS / Linux:** same, but `command: "python3 ~/.claude/skills/time-anchor/scripts/start_session.py"`.

Use forward slashes on Windows paths — bash escapes backslashes and breaks the hook.

For multi-terminal users: each Claude Code instance is tracked independently, no cross-terminal interference. Periodically run `/cleanup-sessions` to purge orphaned records (terminals you closed without `/end-session-time`).

## FAQ

**Does this work in claude.ai (the web chat)?** No — claude.ai can't execute Python. Targets Claude Code, Agent SDK, and agentic harnesses where Claude has bash + Python.

**How accurate is auto-detect?** ~85% on first try. Falls back to manual picker for the rest.

**Can I share session data with another memory plugin?** Yes — set `$TIME_ANCHOR_MEMORY_PATH` to that plugin's JSON file. time-anchor namespaces under a `time_anchor` key so it doesn't clobber the host plugin's data.

**Can I install via `/plugin`?** Yes, if your CC version supports plugin marketplaces:
```
/plugin marketplace add TroyJLorents-GH/time-anchor
/plugin install time-anchor@time-anchor-plugins
```
Slash commands then namespace as `/time-anchor:current-time`. The one-liner install above is more universal (no GitHub auth needed).

## Roadmap

- v0.2 — Optional Google Places API for fuzzy city autocomplete + lat/lng zone resolution
- v0.2 — Auto session tracking baked into installer
- v0.3 — Multi-user memory backends

## License

MIT. See [LICENSE](LICENSE).

Built by [Troy Lorents](https://github.com/TroyJLorents-GH). Bundled data: IANA `tzdata` zone1970.tab + CLDR `windowsZones.xml`.
