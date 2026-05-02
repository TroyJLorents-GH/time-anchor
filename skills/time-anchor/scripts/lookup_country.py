#!/usr/bin/env python3
"""Look up IANA timezones for a country/territory name.

Usage:
    python lookup_country.py "United States"
    python lookup_country.py "spain"
    python lookup_country.py "Russia"

Output is JSON:
    {"query": "...", "matched": "united states",
     "zones": ["America/New_York", "America/Chicago", ...]}

Exits 0 on match, 1 if no country found. Uses substring fallback if exact
key match fails (e.g. "states" -> "united states").
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "country_zones.json"


def normalize(s: str) -> str:
    return " ".join(s.strip().lower().split())


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python lookup_country.py <country-name>", file=sys.stderr
        )
        return 1

    query = " ".join(sys.argv[1:])
    norm = normalize(query)

    if not ASSETS.exists():
        print(f"ERROR: country_zones.json not found at {ASSETS}", file=sys.stderr)
        return 1

    raw = json.loads(ASSETS.read_text(encoding="utf-8"))
    data = {k: v for k, v in raw.items() if not k.startswith("_")}

    # Exact match
    if norm in data:
        print(json.dumps({"query": query, "matched": norm, "zones": data[norm]}, indent=2))
        return 0

    # Substring match — collect any country whose normalized key contains the
    # query (or vice versa). Pick the shortest matching key (typically the
    # most specific).
    candidates = [k for k in data if norm in k or k in norm]
    if candidates:
        best = min(candidates, key=len)
        print(json.dumps({"query": query, "matched": best, "zones": data[best]}, indent=2))
        return 0

    print(json.dumps({"query": query, "matched": None, "zones": []}, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
