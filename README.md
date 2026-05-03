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

**Recommended — Claude Code plugin marketplace** (works everywhere, handles updates):

```
/plugin marketplace add TroyJLorents-GH/time-anchor
/plugin install time-anchor@time-anchor-plugins
```

**Or one-liner installer** (no GitHub auth needed, copies files directly):

Windows (PowerShell):
```powershell
iwr -useb https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.ps1 | iex
```

macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.sh | bash
```

Restart Claude Code. Done.

## First-time setup

Ask Claude anything time-related. A short 3-question wizard runs once:

```
You: what time is it?

Claude: Detected America/Phoenix from your system. Use this? [Yes / Pick different]
You: Yes

Claude: How long of idle time before your session timer resets?
        [1 hour / 4 hours / 8 hours / 24 hours / Never]
You: 4 hours

Claude: How should I display the time? Same moment in three formats:
        - 12-hour AM/PM   →  1:00 PM
        - 24-hour         →  13:00
        - Military        →  1300
You: 12-hour AM/PM

Claude: Saturday, May 2, 2026 at 4:19 PM MST.
```

~85% of users get auto-detected on Q1; the rest type a city or country and pick from a list. Q2 + Q3 are quick picks. Run later via `/set-timezone` (timezone) or `/time-anchor-settings` (idle + format).

## Slash commands

| Command | What it does |
|---|---|
| `/current-time` | Print the current local time |
| `/set-timezone [IANA]` | Set or change timezone — auto-detect + country picker. Pass `America/Phoenix` etc. to skip the picker. |
| `/session-time` | Show the rolling session: started, elapsed, total commands, active terminals. Auto-resets after idle threshold. |
| `/reset-session` | Manually reset the session timer to now |
| `/time-anchor-settings` | View or change settings — idle reset hours, time format. Interactive picker, no flags needed. |

## How sessions work (it's just one)

There's a single rolling session, not per-terminal. Every time-anchor command bumps `last_active_at`. If the gap between commands exceeds your idle threshold (default 4 hours), the session auto-resets — like an inactivity timeout.

Want a different threshold? `/time-anchor-settings` → pick `1h`, `4h`, `8h`, `24h`, or `Never`. Want to manually reset? `/reset-session`.

This sidesteps the cross-terminal confusion that comes from trying to track each Claude Code instance separately. One number, one mental model.

## Settings

Two knobs:

- **`idle_reset_hours`** — auto-reset after this many hours idle. Default `4`. Set to `Never` to disable auto-reset.
- **`time_format`** — choose one (all show 1 PM):
  - `12h` (default) → `1:00 PM MST`
  - `24h` → `13:00 MST`
  - `military` → `1300 MST`

### Three ways to edit, all hit the same `memory.json`:

**1. Slash command in Claude Code (easiest, interactive):**
```
/time-anchor-settings
```
Prints current values, then asks what you want to change with button pickers.

**2. Slash command with flags (skip the picker):**
```
/time-anchor-settings --idle 8 --format 24h
/time-anchor-settings --idle never
/time-anchor-settings --format military
```

**3. From a regular terminal (outside Claude Code):**

Bash / macOS / Linux:
```bash
python ~/.claude/skills/time-anchor/scripts/update_settings.py --idle 8 --format 24h
```
Windows PowerShell:
```powershell
python "$HOME\.claude\skills\time-anchor\scripts\update_settings.py" --idle 8 --format 24h
```

Run with no flags to print the current values.

## Demo

```
❯ /current-time
Saturday, May 2, 2026 at 4:19 PM MST

❯ /session-time
| Now | Saturday, May 2, 2026 at 4:19 PM MST |
| Session started | 9:14 AM MST |
| Elapsed | 7h 5m |
| Total commands | 47 |
| Active terminals | 3 |
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

First-run wizard runs once:

1. **Timezone** — auto-detect via `$TZ`, `/etc/localtime`, or `tzutil` (Windows) against the bundled CLDR map. Confirm with Yes / Pick-different. Free-text fallback covers all ~200 countries with full IANA zone lists.
2. **Idle reset** — pick `1h / 4h / 8h / 24h / Never`.
3. **Time format** — pick `12-hour AM/PM (1:00 PM)`, `24-hour (13:00)`, or `Military (1300)`.

State persists in `~/.claude/skills/time-anchor/memory.json` (per-user, local only).

## Privacy

- **No network calls.** Detection and country lookup use bundled data.
- **No telemetry.** Nothing leaves your machine.
- **Memory is local.** Lives in `~/.claude/`.

## FAQ

**Does this work in claude.ai (the web chat)?** No — claude.ai can't execute Python. Targets Claude Code, Agent SDK, and agentic harnesses where Claude has bash + Python.

**Does session time track per-terminal?** No. Single rolling session across all your Claude Code activity. We tried per-terminal in v0.1; it created confusion (orphan records, cross-terminal collisions, version-dependent env-var quirks). v0.2 simplified to one rolling session — much less to think about.

**Can I share session data with another memory plugin?** Yes — set `$TIME_ANCHOR_MEMORY_PATH` to that plugin's JSON file. time-anchor namespaces under a `time_anchor` key so it doesn't clobber the host plugin's data.

## What's new in v0.2

- Single rolling session (not per-terminal). Configurable idle reset.
- Three time formats: `12h` (1:00 PM), `24h` (13:00), `military` (1300) — pickers show concrete examples so you don't need to know acronyms.
- First-run setup wizard: timezone → idle reset → time format, all in one go.
- `/session-time` shows live count of running `claude` processes (active terminals).
- New: `/reset-session`, `/time-anchor-settings`.
- Removed: `/start-session-time`, `/end-session-time`, `/cleanup-sessions`, `/standup`. The session model is automatic now.
- Removed: SessionStart hook requirement. Sessions auto-track on every command.

## License

MIT. See [LICENSE](LICENSE).

Built by [Troy Lorents](https://github.com/TroyJLorents-GH). Bundled data: IANA `tzdata` zone1970.tab + CLDR `windowsZones.xml`.
