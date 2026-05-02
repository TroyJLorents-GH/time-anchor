---
description: Log the start of this session in time-anchor
---

Use the time-anchor skill to log the session start.

Run `start_session.py` and report the new `session_id` and start timestamp to the user. If a session was already open within the last 30 minutes, the script reuses it — mention that to the user instead of pretending a new one was created.
