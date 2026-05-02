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

Map their answer using `references/country_zones.md` (ordered country lists for multi-zone countries) and `references/timezones.md` (full IANA list).

**Show ALL zones for the country, never just the top 4.** Claude Code's `AskUserQuestion` tool caps at ~5 options per pick, so paginate:

1. **Print the full numbered list of zones for that country in chat as plain markdown** (read directly from `references/country_zones.md`). The user must be able to see every option before selecting.
2. **Then** show a paginated `AskUserQuestion`: first 4 zones + a `More zones (5–8)` option that re-prompts with the next batch + a final `Type IANA name directly` option that lets the user paste the canonical name from the printed list.
3. Loop the picker until the user selects a zone.

| User input pattern | What to do |
|---|---|
| Single-zone country (India, Japan, UK, Germany) | Confirm the 1 canonical zone with Yes/No. |
| Multi-zone country (US, Russia, Canada, Brazil, Australia, Mexico, Indonesia, Spain, Argentina, etc.) | Print full list from `country_zones.md`, then paginated picker as above. |
| Specific city | Map directly to the matching IANA zone, confirm with Yes/No. |
| Region (e.g. "Eastern Europe") | Print full list of zones in that region from `timezones.md`, then paginated picker. |

**US-specific note:** `America/Phoenix` (Arizona, no-DST) MUST appear in the printed list and reachable via the picker — picking `America/Denver` for an Arizonan is wrong half the year.

If a country has more zones than `country_zones.md` documents (e.g. less common ones in Antarctica, France's overseas territories), fall back to grepping `references/timezones.md` for the country code prefix and include all matches.

**4. Save.** Once a zone is selected, call:

```bash
python <skill-path>/scripts/set_timezone.py "<IANA_NAME>"
```

Confirm to the user with the human-readable timezone name and current local time.

## Notes

- Searchable full-IANA-list picker is not available in Claude Code's UI. If the user wants to type the IANA name directly, they can run `/set-timezone America/Phoenix` (or any valid IANA name) and step 1 handles it.
- Never invent zones. Only use names that exist in `zoneinfo.available_timezones()` — `set_timezone.py` rejects invalid input regardless.
