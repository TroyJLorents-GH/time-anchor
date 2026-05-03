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
- If accepted, call `set_timezone.py` with the detected zone. Continue to step 5.

**3. Free-text path.** If detection fails or user picks "different", ask in chat: *"What city, country, or region are you in?"*

Then run the lookup script — it returns the FULL ordered list of IANA zones for that country/territory from the bundled `assets/country_zones.json` (covers ~200 countries):

```bash
python <skill-path>/scripts/lookup_country.py "<their answer>"
```

Output is JSON: `{"query": ..., "matched": ..., "zones": [...]}`.

**Then present ALL zones to the user, not a truncated subset.** Claude Code's `AskUserQuestion` tool caps at ~5 options per pick, so:

1. **Print the full numbered list** of every zone returned in chat as plain markdown so the user sees every option.
2. **Then** show a paginated `AskUserQuestion`: 4 zones + `Show next batch` + (on final batch) `Type IANA name directly`.
3. Loop until the user picks a zone, then call `set_timezone.py "<chosen>"`.

| User input pattern | What to do |
|---|---|
| Country name (any of ~200 countries) | Run `lookup_country.py`, print full list, paginated picker. |
| City name | Map directly to its IANA zone (`references/timezones.md`), confirm Yes/No. |
| Region (e.g. "Eastern Europe", "Pacific Islands") | Print all matching zones from `references/timezones.md` for that region prefix, paginated picker. |
| Single-zone country (most countries) | `lookup_country.py` returns 1 zone — confirm Yes/No. |

**US-specific note:** `lookup_country.py "United States"` returns 29 US zones starting with the 7 most common (Eastern, Central, Mountain w/ DST, **Phoenix no-DST**, Pacific, Alaska, Hawaii). Always page through to make `America/Phoenix` reachable — Arizona doesn't observe DST, so picking `America/Denver` for an Arizonan is wrong half the year.

**Fallback:** If `lookup_country.py` exits 1 (unknown country), tell the user, then ask them to clarify or type an IANA name directly. Never guess silently.

**4. Save timezone.** Once a zone is selected, call:

```bash
python <skill-path>/scripts/set_timezone.py "<IANA_NAME>"
```

**5. First-run wizard — only on fresh install.**

Determine "fresh install" by running this BEFORE step 1:

```bash
python <skill-path>/scripts/init.py
```

If init prints `STATUS: NEEDS_SETUP` (exit 2), this is a fresh install — remember this and continue through step 5 after saving the timezone. If init prints `READY` (exit 0), the user is just changing their timezone — stop after step 4. Use `/time-anchor-settings` to change idle or format separately.

**5a. Idle reset.** Use `AskUserQuestion`:

> *"How long should idle time be before your session timer resets? (Every command bumps the timer; if you go idle longer than this, the next command starts a fresh session.)"*

Options:
- `1 hour` — short bursts
- `4 hours` — default, typical workday
- `8 hours` — full work shift
- `24 hours` — daily reset
- `Never` — only manual `/reset-session`

Map pick to `--idle 1` / `--idle 4` / `--idle 8` / `--idle 24` / `--idle never`.

**5b. Time format.** Use `AskUserQuestion`:

> *"How should I display the time? (Same moment in three formats:)"*

Options — show example for each:
- `12-hour AM/PM` → example: **`1:00 PM`**
- `24-hour` → example: **`13:00`**
- `Military` → example: **`1300`**

Map pick to `--format 12h` / `--format 24h` / `--format military`.

**5c. Save settings:**

```bash
python <skill-path>/scripts/update_settings.py --idle <pick> --format <pick>
```

**6. Confirm.** Print a final summary table to the user with their timezone, idle setting, time format, and the current local time (rendered in their chosen format). Done.

## Notes

- Searchable full-IANA-list picker is not available in Claude Code's UI. If the user wants to type the IANA name directly, they can run `/set-timezone America/Phoenix` (or any valid IANA name) and step 1 handles it.
- Never invent zones. Only use names that exist in `zoneinfo.available_timezones()` — `set_timezone.py` rejects invalid input regardless.
- Step 5 (the wizard tail) runs **only on first-time setup**. If the user is just changing their timezone, skip it — they can use `/time-anchor-settings` for the other two.
