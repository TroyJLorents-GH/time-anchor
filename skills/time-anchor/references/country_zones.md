# Country → IANA timezones

When the user names a country in the `/set-timezone` free-text flow, look it up here. Each entry lists zones in priority order. Show the first 4 via `AskUserQuestion` plus an `Other` option that reveals the rest.

If the user names a city, prefer matching directly to the IANA name in `timezones.md` instead.

---

## United States 🇺🇸 (7+ zones)

1. `America/New_York` — **Eastern** (NYC, Boston, Atlanta, Miami, DC)
2. `America/Chicago` — **Central** (Chicago, Houston, Dallas, Minneapolis)
3. `America/Denver` — **Mountain w/ DST** (Denver, Salt Lake City, Albuquerque)
4. `America/Phoenix` — **Mountain no-DST** (most of Arizona)
5. `America/Los_Angeles` — **Pacific** (LA, San Francisco, Seattle, Las Vegas)
6. `America/Anchorage` — **Alaska**
7. `Pacific/Honolulu` — **Hawaii**
8. `America/Indiana/Indianapolis` — Eastern with Indiana DST history
9. `America/Detroit` — Eastern (Michigan)
10. `America/Adak` — Aleutian Islands
11. `America/Puerto_Rico` — Atlantic (no DST)
12. `Pacific/Guam` — Chamorro (Guam, Northern Marianas)
13. `Pacific/Pago_Pago` — Samoa Time

**Recommended drill-down:** show 1–4 first; on `Other`, show 5–7 + `More` for territories/exotic.

## Canada 🇨🇦 (6 zones)

1. `America/Toronto` — Eastern (Toronto, Ottawa, Montreal)
2. `America/Vancouver` — Pacific (Vancouver, Victoria)
3. `America/Edmonton` — Mountain (Edmonton, Calgary)
4. `America/Winnipeg` — Central (Winnipeg)
5. `America/Halifax` — Atlantic (Halifax, NB, NS)
6. `America/St_Johns` — Newfoundland (UTC-3:30)
7. `America/Regina` — Saskatchewan (Central, no DST)
8. `America/Whitehorse` — Yukon (no DST)

## Mexico 🇲🇽 (4 zones)

1. `America/Mexico_City` — Central (Mexico City, Guadalajara)
2. `America/Tijuana` — Pacific (Tijuana, Mexicali)
3. `America/Hermosillo` — Mountain no-DST (Sonora)
4. `America/Cancun` — Eastern (Cancún, Quintana Roo)
5. `America/Mazatlan` — Mountain (Mazatlán, Chihuahua)

## Brazil 🇧🇷 (4 zones)

1. `America/Sao_Paulo` — BRT, most of Brazil (São Paulo, Rio, Brasília)
2. `America/Manaus` — Amazon (Manaus, Cuiabá)
3. `America/Belem` — Eastern Brazil (Belém)
4. `America/Noronha` — Fernando de Noronha (UTC-2)
5. `America/Rio_Branco` — Acre (UTC-5)

## Argentina 🇦🇷

1. `America/Argentina/Buenos_Aires` — primary (Buenos Aires, most of country)
2. `America/Argentina/Cordoba`
3. `America/Argentina/Mendoza`
4. `America/Argentina/Ushuaia`

## Chile 🇨🇱

1. `America/Santiago` — mainland (Santiago, Valparaíso)
2. `Pacific/Easter` — Easter Island
3. `America/Punta_Arenas` — Magallanes region

## Russia 🇷🇺 (11 zones)

1. `Europe/Moscow` — Moscow, St. Petersburg
2. `Asia/Yekaterinburg` — Yekaterinburg
3. `Asia/Novosibirsk` — Novosibirsk
4. `Asia/Krasnoyarsk` — Krasnoyarsk
5. `Asia/Irkutsk` — Irkutsk
6. `Asia/Yakutsk` — Yakutsk
7. `Asia/Vladivostok` — Vladivostok
8. `Asia/Magadan` — Magadan
9. `Asia/Kamchatka` — Petropavlovsk-Kamchatsky
10. `Europe/Kaliningrad` — Kaliningrad
11. `Europe/Samara` — Samara

## Australia 🇦🇺 (5 zones)

1. `Australia/Sydney` — Eastern (Sydney, Melbourne, Canberra, Hobart)
2. `Australia/Perth` — Western (Perth)
3. `Australia/Brisbane` — Eastern no-DST (Brisbane, Queensland)
4. `Australia/Adelaide` — Central (Adelaide)
5. `Australia/Darwin` — Central no-DST (Darwin, NT)
6. `Australia/Hobart` — Tasmania (DST differs from Sydney)
7. `Australia/Lord_Howe` — Lord Howe Island (UTC+10:30/+11)

## Indonesia 🇮🇩 (3 zones)

1. `Asia/Jakarta` — Western (Jakarta, Sumatra, Java)
2. `Asia/Makassar` — Central (Bali, Sulawesi, Kalimantan)
3. `Asia/Jayapura` — Eastern (Papua)

## Spain 🇪🇸

1. `Europe/Madrid` — mainland (Madrid, Barcelona)
2. `Atlantic/Canary` — Canary Islands
3. `Africa/Ceuta` — Ceuta, Melilla

## Portugal 🇵🇹

1. `Europe/Lisbon` — mainland (Lisbon, Porto)
2. `Atlantic/Azores` — Azores
3. `Atlantic/Madeira` — Madeira

## United Kingdom 🇬🇧

1. `Europe/London` — England, Scotland, Wales, NI

## France 🇫🇷

1. `Europe/Paris` — mainland
2. `Indian/Reunion` — Réunion
3. `America/Martinique` — Martinique
4. `America/Guadeloupe` — Guadeloupe
5. `Pacific/Noumea` — New Caledonia
6. `Pacific/Tahiti` — French Polynesia

## Germany / Italy / Netherlands / Belgium / Austria / Switzerland / Sweden / Norway / Denmark / Poland / Czechia

Single zone — `Europe/Berlin`, `Europe/Rome`, `Europe/Amsterdam`, `Europe/Brussels`, `Europe/Vienna`, `Europe/Zurich`, `Europe/Stockholm`, `Europe/Oslo`, `Europe/Copenhagen`, `Europe/Warsaw`, `Europe/Prague` respectively.

## India 🇮🇳

1. `Asia/Kolkata` — entire country (UTC+5:30, no DST)

## China 🇨🇳

1. `Asia/Shanghai` — entire country (officially one zone, UTC+8)
2. `Asia/Urumqi` — Xinjiang local (informally used)

## Japan 🇯🇵

1. `Asia/Tokyo` — entire country

## South Korea 🇰🇷

1. `Asia/Seoul`

## Kazakhstan 🇰🇿

1. `Asia/Almaty` — eastern (Almaty, Astana/Nur-Sultan)
2. `Asia/Aqtobe` — western

## Mongolia

1. `Asia/Ulaanbaatar` — most of country
2. `Asia/Hovd` — western Mongolia

## Antarctica

Various stations — `Antarctica/McMurdo`, `Antarctica/Palmer`, `Antarctica/Casey`, etc. Ask which station.

---

**Single-zone countries (no disambiguation needed):**
Most countries fit here — UK, France (mainland), Germany, Japan, India, Korea, Singapore, Thailand, Vietnam, Philippines, most of Africa, most of South America (apart from Brazil/Chile/Argentina), most of Europe.

If user names a country not listed above, use your geographic knowledge to map to the canonical zone (usually `Continent/Capital`) and confirm with one Yes/No `AskUserQuestion`.
