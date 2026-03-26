# Counted

Constituent pressure tool for the US Senate Iran war funding vote. Scores all 100 senators by how responsive they are likely to be to constituent calls, then makes it easy to actually make the call.

Static site, no backend, no accounts. Your zip code never leaves the browser.

## Context

62% of Americans oppose the Iran war. The Senate votes on $200B in supplemental war funding soon. Calling your senator's office is [the single most effective form of constituent contact](https://www.congressfoundation.org/citizen-engagement/how-to-engage) — staffers track every call and flag volume spikes directly to the senator.

Almost nobody calls. You have to find the right number, figure out what to say, and you hang up with zero indication it mattered. This is a collective action problem: the opposition exists but it's invisible and uncoordinated, so it's easy to ignore.

Counted is a routing tool. It identifies where calls will have the most impact and removes the friction to make one.

## How the scoring works

~220 lines of Python. Each senator gets an Expected Impact score:

```
Expected Impact = Persuadability × Leverage
```

**Persuadability** — will calls actually change their behavior?

| Factor | What it measures |
|---|---|
| Electoral proximity | Are they up for reelection in 2026? |
| Electorate alignment | Does their state's PVI suggest voters oppose the war? |
| Demonstrated ambivalence | Have they hedged, set conditions, or avoided commitment? |
| Historical independence | How often do they break with their party? |
| Electoral margin | How tight was their last race? |
| Primary direction | Are they threatened from the general or from a primary? |

**Leverage** — how much does their behavior matter?

| Factor | What it measures |
|---|---|
| Committee power | Do they sit on Appropriations, Armed Services, or Foreign Relations? |
| Leadership role | Can they set agenda or whip votes? |
| Signal value | Would their defection change the calculus for others? |

The top result is Susan Collins (R-ME) at 0.80 — she chairs the Appropriations Committee (the committee the $200B goes through), faces reelection in a state that went for Harris, and has publicly hedged on her support. The #2 is at 0.35. The top 20 includes 11 Republicans and 9 Democrats.

All weights and factors are in the code. You can disagree with them. That's intentional.

## The web app

Enter your zip code. See your senators and the top national targets. Get a call script. Tap to call. The whole thing takes a few minutes.

**No backend.** ZIP-to-state lookup uses a 12KB JSON map of ~950 USPS ZIP3 prefixes, processed client-side. No API calls, no analytics, no tracking.

**Static data at build time.** A Python script transforms the algorithm's output into three JSON files (senator data, call scripts, ZIP map) that get compiled into the bundle. Re-running the scorer invalidates only the data chunk.

**Personalized scripts.** The top 20 targets get call scripts that reference their specific committee role, stated position, and electoral situation. The other 80 get a generic template that still works.

**`tel:` links as the primary CTA.** On mobile, tapping "Call DC Office" opens the dialer. No app, no signup.

**localStorage for persistence.** "You already contacted this senator" survives a page reload. The record schema (`{senator_slug, action_type, timestamp, zip}`) mirrors a future API body so a backend can be added later without changing the UI code.

### Bundle size

~101KB gzipped. No web fonts.

| Chunk | Gzipped |
|---|---|
| React + React Router | 74KB |
| Senator data + scripts + ZIP map | 15KB |
| Application code | 7KB |
| CSS (Tailwind, purged) | 4KB |

## Running it

```bash
# Score all 100 senators
python -m counted

# Generate frontend data files from scores
python scripts/build_frontend_data.py

# Start the dev server
cd counted-web
npm install
npm run dev

# Production build → dist/
npm run build
```

Deploy `dist/` to any static host. The `public/_redirects` file handles SPA routing on Netlify.

## Project structure

```
├── counted/                     # Scoring algorithm (Python)
│   ├── scorer.py                # 10 factors → expected impact
│   ├── models.py                # Senator, Score, Contact
│   ├── data_loader.py           # JSON ingestion
│   └── output.py                # Terminal + file output
├── data/                        # Algorithm inputs (public sources)
│   ├── senators.json            # 119th Congress, 100 senators
│   ├── committees.json          # War-relevant assignments
│   ├── ambivalence.json         # Hand-scored hedging signals (~20 senators)
│   ├── contacts.json            # Phones, web forms, social handles
│   └── ...                      # PVI, margins, independence, signal value
├── output/                      # Algorithm output
│   └── ranked_senators.json     # Scored + ranked with full contact cards
├── scripts/
│   └── build_frontend_data.py   # Transforms output → frontend JSON
├── counted-web/                 # Static React app (Vite + Tailwind)
│   └── src/
│       ├── data/                # Generated: senators, scripts, ZIP map
│       ├── lib/                 # Data access, phone formatting, sharing
│       ├── hooks/               # ZIP lookup, localStorage actions
│       ├── components/          # UI: cards, scripts, contact lists
│       └── pages/               # Landing, results, senator detail, about, FAQ
└── tests/
```

## Methodology notes

Most inputs are derived from public data: FEC filings, committee rosters, Cook PVI, vote records, election results.

Two inputs involve judgment:

**Ambivalence scores** (M3) for ~20 key senators were hand-scored from public statements, floor speeches, and reported conditions on support. Jerry Moran (R-KS) gets a 0.70 for the most vocal skepticism; Tom Cotton (R-AR) gets a 0.05. This is the most subjective factor.

**Signal value** (M9) estimates "how much would it matter if this senator broke?" — a question about political dynamics that doesn't have a clean quantitative answer.

Everything else is mechanical.

## What this is not

Not partisan. The algorithm is indifferent to party. It targets Collins and Durbin for different structural reasons, but it targets both.

Not a data collection tool. No accounts, no cookies, no pixels. Your zip code is matched against a static file in your browser and discarded.

Not astroturf. The scripts are templates. You call from your own phone, to your own senator, in your own voice. The tool just tells you which number to dial and gives you something to say.

## Phase 3 (planned)

The missing piece is feedback. Right now you call and nothing visible happens. Phase 3 adds a public counter — verified constituent contacts per senator, updated in real time. The frontend already has the hooks wired in (placeholder components, localStorage schema matching the future API).

The theory is that "23,000 Maine constituents have called Senator Collins" changes the dynamic for both the next caller and the senator's office. Individual calls are easy to ignore. A visible, growing count is not.
