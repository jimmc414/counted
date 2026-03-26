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

### Persuadability

Weighted sum of five factors, multiplied by a sixth:

```
Persuadability = (0.25·M1 + 0.25·M2 + 0.25·M3 + 0.12·M4 + 0.13·M5) × M6
```

M1, M2, and M3 are weighted equally at 0.25 because the model treats electoral exposure, electorate alignment, and personal ambivalence as roughly equally strong signals that a senator might respond to pressure. M4 and M5 are weaker signals — a senator can have a narrow margin and still vote in lockstep.

| Factor | Weight | Input | Scoring tiers |
|---|---|---|---|
| M1: Electoral proximity | 0.25 | Senate class | Class II (up 2026) → 1.0, Class III (2028) → 0.3, Class I (2030) → 0.1 |
| M2: Electorate alignment | 0.25 | Cook PVI | D+5 → 1.0, D+1 → 0.8, EVEN → 0.6, R+4 → 0.4, R+9 → 0.2, R+10+ → 0.05 |
| M3: Ambivalence | 0.25 | Hand-scored | Explicit scores for ~20 senators (0.05–0.95). Default: R → 0.20, D → 0.05 |
| M4: Independence | 0.12 | Party-line deviation % | ≥20% → 1.0, ≥10% → 0.7, ≥5% → 0.4, <5% → 0.15 |
| M5: Electoral margin | 0.13 | Last election margin | <3pt → 1.0, ≤6 → 0.75, ≤10 → 0.5, ≤20 → 0.25, >20 → 0.05 |

**M6: Primary direction modifier.** M6 is not a weighted addend — it multiplies the entire persuadability sum. Values above 1.0 boost the score (the senator faces a general-election threat, so opposing the war helps them); values below 1.0 dampen it (the senator faces a right-wing primary, so opposing the war hurts them). Most senators get 1.0 (no adjustment). Collins gets 1.2; senators like Cotton and Cornyn get 0.7.

This factor exists because the same constituent call has opposite effects depending on which election the senator is worried about. A call saying "I'll vote against you if you fund this war" helps Collins in a general election and hurts Cotton in a primary. Treating M6 as a multiplier scales the entire persuadability signal rather than penalizing just one component.

### Leverage

```
Leverage = 0.40·M7 + 0.20·M8 + 0.40·M9
```

Committee power and signal value are weighted equally at 0.40. The model considers "can they directly block the funding" and "would their defection shift the political landscape" as equally important forms of leverage. Leadership gets a lower weight because most leaders are ideologically committed — the whip is unlikely to break, but if they did, it would matter.

| Factor | Weight | Scoring |
|---|---|---|
| M7: Committee power | 0.40 | Chair of Approps/Armed Svcs/Foreign Rels → 1.0, Ranking Member → 0.85, Member → 0.7, Intel/Budget → 0.4, none → 0.15 |
| M8: Leadership | 0.20 | Majority/Minority Leader/Whip → 1.0, Committee Chair/Ranking → 0.7, Conference/Caucus Chair → 0.6, none → 0.2 |
| M9: Signal value | 0.40 | Hand-scored, 0.2–0.9. Collins → 0.9, Murkowski → 0.8, Moran → 0.65. Default → 0.2 |

### Debatable assumptions

**R vs. D ambivalence defaults.** Senators without explicit M3 scores default to 0.20 (R) or 0.05 (D). The reasoning: most Republicans haven't publicly opposed the war but belong to a party with some isolationist tradition; most Democrats have actively opposed it and are scored explicitly if they've wavered. You could argue the R default should be lower or the D default higher.

**M10 is dormant.** Set to 1.0 for all senators. Designed for Phase 3, where it would model diminishing returns — the 50,000th call to Collins matters less than the 500th. Currently a no-op because there's no contact data to drive it.

**Key factor labels.** Each senator's "why they matter" tag (e.g., "Holds war funding power") is derived by computing the marginal contribution of each factor to the final score and picking the largest. It's not hand-assigned — it falls out of the math.

### Worked example: Susan Collins (R-ME)

```
M1 (electoral proximity):  1.0   — Class II, up in 2026
M2 (electorate alignment): 0.8   — Maine is D+3
M3 (ambivalence):          0.55  — hand-scored from public hedging
M4 (independence):         0.7   — 17% party-line deviation
M5 (margin):               0.5   — won by 8.6 points
M6 (primary direction):    1.2   — general election threat boosts

Persuadability = (0.25×1.0 + 0.25×0.8 + 0.25×0.55 + 0.12×0.7 + 0.13×0.5) × 1.2
               = 0.7365 × 1.2
               = 0.8838

M7 (committee power):      1.0   — chairs Appropriations
M8 (leadership):           0.7   — committee chair
M9 (signal value):         0.9   — highest in dataset

Leverage = 0.40×1.0 + 0.20×0.7 + 0.40×0.9
         = 0.90

Expected Impact = 0.8838 × 0.90 = 0.7954
```

The #2 senator (Tillis, R-NC) scores 0.35. That gap isn't an error — Collins is an unusually high-leverage target because she sits at the intersection of committee power, electoral vulnerability, and demonstrated ambivalence simultaneously. The top 20 includes 11 Republicans and 9 Democrats.

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

## Data sources

Most scoring inputs are derived from public records: Cook PVI, FEC election results, committee rosters from senate.gov, and vote tallies from ProPublica/VoteView.

Two inputs are hand-scored and subjective:

**Ambivalence (M3):** ~20 senators scored 0.05–0.95 from public statements, floor speeches, and reported conditions on support. Moran (R-KS) gets 0.70 for the most vocal skepticism; Paul (R-KY) gets 0.95 as a consistent non-interventionist; Cotton (R-AR) gets 0.05. The remaining ~80 senators use defaults (R: 0.20, D: 0.05).

**Signal value (M9):** ~20 senators scored 0.2–0.9. This estimates "how much would it matter if this senator broke?" — inherently a judgment about political dynamics. Collins at 0.9 reflects that the Appropriations chair opposing the funding would be front-page news. A backbench freshman at 0.2 would not.

## What this is not

Not partisan. The algorithm is indifferent to party. It targets Collins and Durbin for different structural reasons, but it targets both.

Not a data collection tool. No accounts, no cookies, no pixels. Your zip code is matched against a static file in your browser and discarded.

Not astroturf. The scripts are templates. You call from your own phone, to your own senator, in your own voice. The tool just tells you which number to dial and gives you something to say.

## Phase 3 (planned)

The missing piece is feedback. Right now you call and nothing visible happens. Phase 3 adds a public counter — verified constituent contacts per senator, updated in real time. The frontend already has the hooks wired in (placeholder components, localStorage schema matching the future API).

The theory is that "23,000 Maine constituents have called Senator Collins" changes the dynamic for both the next caller and the senator's office. Individual calls are easy to ignore. A visible, growing count is not.
