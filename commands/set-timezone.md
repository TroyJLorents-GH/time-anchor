---
description: Set or change the user's timezone for time-anchor
argument-hint: "[optional IANA name e.g. America/Phoenix]"
---

Use the time-anchor skill to set the user's timezone.

## Flow

**1. Direct IANA path.** If `$ARGUMENTS` is non-empty and looks like a valid IANA name (matches pattern `Region/City` or known special zones like `UTC`), call `set_timezone.py "$ARGUMENTS"` immediately. Done.

**2. Auto-detect path.** Otherwise run `detect_timezone.py`. If `best` is non-null:
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
