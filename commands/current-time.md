---
description: Show the current local time in the user's timezone (via time-anchor skill)
---

Use the time-anchor skill to fetch and report the current local time.

Run `now.py` and present the `human` field of the JSON output to the user. If the timezone is not yet set (script returns an error), invoke the `/set-timezone` flow first.
