<div align="center">

# 🕛 time-anchor

> Anchor Claude to the real, current time in your local timezone.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Plugin format: Claude Code](https://img.shields.io/badge/Claude_Code-plugin-7C3AED.svg)](https://claude.com/claude-code)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](.claude-plugin/plugin.json)

</div>

Claude has no built-in clock. Each session starts cold, training data is frozen, and any "current time" Claude states is a hallucination. **time-anchor** fixes that.

Auto-detects your timezone on install (no API key, no network call), reads the host system clock when you ask for the time, and tracks a single rolling session timer that resets after idle. All local. Simple.

## Install

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.sh | bash
```

Restart Claude Code. Done.

## First-time setup

Ask Claude anything time-related. The skill auto-detects your timezone:

```
You: what time is it?
Claude: Detected America/Phoenix from your system. Use this? [Yes / Pick different]
You: Yes
Claude: Saturday, May 2, 2026 at 4:19 PM MST.
```

~85% of users get auto-detected; the rest type a city or country and pick from a list.

## Slash commands

| Command | What it does |
|---|---|
| `/current-time` | Print the current local time |
| `/set-timezone [IANA]` | Set or change timezone — auto-detect + country picker. Pass `America/Phoenix` etc. to skip the picker. |
| `/session-time` | Show the rolling session: started, elapsed, total commands. Auto-resets after idle threshold. |
| `/reset-session` | Manually reset the session timer to now |
| `/time-anchor-settings` | View or change settings — idle reset hours, time format |

## How sessions work (it's just one)

There's a single rolling session, not per-terminal. Every time-anchor command bumps `last_active_at`. If the gap between commands exceeds your idle threshold (default 4 hours), the session auto-resets — like an inactivity timeout.

Want a different threshold? `/time-anchor-settings` → pick `1h`, `4h`, `8h`, `24h`, or `Never`. Want to manually reset? `/reset-session`.

This sidesteps the cross-terminal confusion that comes from trying to track each Claude Code instance separately. One number, one mental model.

## Settings

Two knobs:

- **`idle_reset_hours`** — auto-reset after this many hours idle. Default `4`. Set to `null` for "never auto-reset."
- **`time_format`** — `12h` (default, "4:19 PM MST") or `24h` ("16:19 MST").

Change via `/time-anchor-settings` or pass directly:

```
/time-anchor-settings --idle 8 --format 24h
/time-anchor-settings --idle never
```

## Demo

```
❯ /current-time
Saturday, May 2, 2026 at 4:19 PM MST

❯ /session-time
| Now | Saturday, May 2, 2026 at 4:19 PM MST |
| Session started | 9:14 AM MST |
| Elapsed | 7h 5m |
| Total commands | 47 |
| Idle reset | 4h |

❯ Claude, schedule a follow-up for tomorrow at 3pm
Got it — that's Sunday, May 3, 2026 at 3:00 PM MST (UTC-7).

❯ Claude, how long has my session been running?
7 hours and 5 minutes — started at 9:14 AM today.
```

## How it works

The trick: **Python scripts in the skill read the host OS clock when Claude executes them via bash.** Claude itself stays clockless, but it now has a tool it can query.

```
User asks time → Claude runs python now.py → reads system clock → returns live timestamp
```

Three-stage timezone setup runs once on first use:

1. **Auto-detect** — checks `$TZ`, `/etc/localtime`, or `tzutil` (Windows) against the bundled CLDR map. Resolves silently for ~85% of users.
2. **Confirm** — single Yes / Pick-different prompt.
3. **Free-text fallback** — type a city or country, picker covers all ~200 countries with full IANA zone lists.

State persists in `~/.claude/skills/time-anchor/memory.json` (per-user, local only).

## Privacy

- **No network calls.** Detection and country lookup use bundled data.
- **No telemetry.** Nothing leaves your machine.
- **Memory is local.** Lives in `~/.claude/`.

## FAQ

**Does this work in claude.ai (the web chat)?** No — claude.ai can't execute Python. Targets Claude Code, Agent SDK, and agentic harnesses where Claude has bash + Python.

**Does session time track per-terminal?** No. Single rolling session across all your Claude Code activity. We tried per-terminal in v0.1; it created confusion (orphan records, cross-terminal collisions, version-dependent env-var quirks). v0.2 simplified to one rolling session — much less to think about.

**Can I share session data with another memory plugin?** Yes — set `$TIME_ANCHOR_MEMORY_PATH` to that plugin's JSON file. time-anchor namespaces under a `time_anchor` key so it doesn't clobber the host plugin's data.

**Can I install via `/plugin`?** Yes:
```
/plugin marketplace add TroyJLorents-GH/time-anchor
/plugin install time-anchor@time-anchor-plugins
```
The one-liner above is more universal (no GitHub auth needed).

## What's new in v0.2

- Single rolling session (not per-terminal). Configurable idle reset.
- Time format setting: 12h AM/PM or 24h military.
- New: `/reset-session`, `/time-anchor-settings`.
- Removed: `/start-session-time`, `/end-session-time`, `/cleanup-sessions`, `/standup`. The session model is automatic now.
- Removed: SessionStart hook requirement. Sessions auto-track on every command.

## License

MIT. See [LICENSE](LICENSE).

Built by [Troy Lorents](https://github.com/TroyJLorents-GH). Bundled data: IANA `tzdata` zone1970.tab + CLDR `windowsZones.xml`.
