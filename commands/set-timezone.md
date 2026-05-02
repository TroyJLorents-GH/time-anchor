---
description: Set or change the user's timezone for time-anchor
argument-hint: "[optional IANA name e.g. America/Phoenix]"
---

Use the time-anchor skill to set or **change** the user's timezone.

**IMPORTANT:** Invoking this command always runs the flow below, even if a timezone is already saved. Do NOT short-circuit with "TZ is already set" — the user invoked `/set-timezone` because they want to set or change it. If a timezone already exists, mention it ("Current: America/Phoenix") and continue.

## Flow

**1. Direct IANA path.** If `$ARGUMENTS` is non-empty AND matches a valid IANA pattern (`Region/City` like `America/Phoenix`, or special names like `UTC`, `GMT`), call `set_timezone.py "$ARGUMENTS"` immediately. The script validates against `zoneinfo` and rejects invalid names — if it errors, fall through to step 2.

**2. Auto-detect path.** If `$ARGUMENTS` is empty OR was an invalid/partial name (e.g. just `America` or `Phoenix`), run `detect_timezone.py`. If `best` is non-null:
- Use `AskUserQuestion` with two options: `Use {best.timezone}` and `Pick a different one`.
- If accepted, call `set_timezone.py` with the detected zone. Done.

**3. Free-text path.** If detection fails or user picks "different", ask in chat: *"What city, country, or region are you in?"*

Map their answer to candidate IANA zones using `references/timezones.md` (full IANA list bundled with this skill) + your own knowledge of city/country geography. Present candidates via `AskUserQuestion`:

| User input pattern | Candidates to show |
|---|---|
| Single-zone country (India, Japan, UK, Germany) | The 1 canonical zone — confirm with Yes/No. |
| Multi-zone country (US, Russia, Brazil, Australia, Canada, Mexico, Indonesia) | Top 4 by population + `Other` option. |
| Specific city | The exact zone + 1-2 zones in same UTC offset within ~500 mi as alternatives. |
| Region (e.g. "Eastern Europe", "Pacific Islands") | 4 most populous zones in that region + `Other`. |

If the user picks `Other`, drill down: show the next set of zones in that region (use `references/timezones.md`), again capped at 4 + `Other`. Repeat until they pick a specific zone.

**4. Save.** Once a zone is selected, call:

```bash
python <skill-path>/scripts/set_timezone.py "<IANA_NAME>"
```

Confirm to the user with the human-readable timezone name and current local time.

## Notes

- Searchable full-IANA-list picker is not available in Claude Code's UI. If the user wants to type the IANA name directly, they can run `/set-timezone America/Phoenix` (or any valid IANA name) and step 1 handles it.
- Never invent zones. Only use names that exist in `zoneinfo.available_timezones()` — `set_timezone.py` rejects invalid input regardless.
