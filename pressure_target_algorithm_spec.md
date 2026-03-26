# Counted — Technical Specification v1.2
### Pressure Target Scoring Algorithm & Constituent Pressure Ledger

## Purpose & Theory of Change
**Counted** scores every sitting US Senator (and optionally House member) on **Expected Impact** — the likelihood that constituent pressure from antiwar callers will influence their behavior on the Iran war, weighted by how much their behavior matters.

**The core problem Counted solves:** 62% of Americans oppose the Iran war — making it the most unpopular war at inception in modern US history — yet there is almost no organized pressure on the politicians who could stop it. The gap is not that people lack opinions. It is that individual opposition is invisible, unquantified, and therefore politically ignorable. Counted converts diffuse opposition into visible, verified, per-senator constituent pressure that creates measurable electoral risk.

**Theory of change:**
```
Individual feels powerless
       → Tool shows them exactly WHO to pressure and HOW
       → They take action (call, tweet, visit)
       → Their action is COUNTED and VISIBLE to others
       → Growing public count creates social proof → more people act
       → Count becomes large enough to represent electoral threat
       → Senator's office can no longer claim "we've heard from a few people"
       → Media covers the count → amplification loop
       → Senator faces concrete choice: vote for $200B war funding
         with 50,000+ constituents publicly pledging to vote against you,
         or break with the administration
```

```
EXPECTED IMPACT = PERSUADABILITY × LEVERAGE
```

Both components are composite scores. The multiplicative structure ensures that a senator who is highly persuadable but has zero leverage (e.g., a vulnerable backbencher with no committee power) scores lower than someone who is moderately persuadable but chairs Appropriations.

---

## PERSUADABILITY COMPONENT

### M1: Electoral Proximity
**What it measures:** How soon the senator faces voters. Immediate electoral pressure changes behavior.

| Condition | Score (0–1) |
|---|---|
| Up for election Nov 2026 | 1.0 |
| Up for election Nov 2028 | 0.3 |
| Up for election Nov 2030 | 0.1 |

**Data source:** Fixed. The 35 seats up in 2026 are known.
- https://ballotpedia.org/United_States_Senate_elections,_2026
- https://en.wikipedia.org/wiki/2026_United_States_Senate_elections

**Update frequency:** Static (changes only if a senator resigns or is appointed mid-cycle).

**Weight: 0.20**

---

### M2: Electorate Alignment (State Opposition to War)
**What it measures:** How antiwar the senator's actual electorate is. A Republican in a blue state has more antiwar constituents calling.

**Scoring approach:** Composite of two sub-metrics:

**M2a: Cook PVI (Partisan Voter Index)**
Maps how blue/red the state leans relative to the national average. More blue = more likely the electorate opposes the war.

| State PVI | Score (0–1) |
|---|---|
| D+5 or more | 1.0 |
| D+1 to D+4 | 0.8 |
| EVEN | 0.6 |
| R+1 to R+4 | 0.4 |
| R+5 to R+9 | 0.2 |
| R+10 or more | 0.05 |

**Data source:**
- Cook Political Report PVI: https://www.cookpolitical.com/cook-pvi (requires subscription; Wikipedia mirrors the latest published values)
- https://en.wikipedia.org/wiki/Cook_Partisan_Voting_Index

**Update frequency:** Updated after each presidential election cycle. Current values reflect 2024 results. Stable until 2028.

**M2b: State-Level War Polling (if available)**
Direct polling on support/opposition to Iran strikes, broken down by state.

| % oppose in state | Score (0–1) |
|---|---|
| 60%+ oppose | 1.0 |
| 50–59% oppose | 0.7 |
| 40–49% oppose | 0.4 |
| <40% oppose | 0.15 |

**Data sources:**
- National polls: AP-NORC, Gallup, Pew, YouGov (search for latest)
- State-level: University polls (UNH for NH, Quinnipiac for swing states, etc.)
- Crosstabs by state are rare; use regional breakdowns or state-party-ID proxies when state-level data unavailable
- FiveThirtyEight polling aggregator: https://projects.fivethirtyeight.com/ (check for war-specific polls)

**Update frequency:** Changes weekly as war continues. Re-pull before each run.

**Composite M2 = 0.6 × M2a + 0.4 × M2b** (if M2b unavailable, use M2a alone)

**Weight: 0.20**

---

### M3: Demonstrated Ambivalence
**What it measures:** Has the senator used hedging language, set conditions, or expressed unease about the war — as opposed to full-throated support or opposition?

| Signal | Score (0–1) |
|---|---|
| Has publicly opposed the war or voted for war powers resolution | 0.95 (already moved — diminishing marginal return on calls, but reinforce) |
| Has set explicit conditions (e.g., "if boots on ground," "if it's not brief") | 0.85 |
| Has expressed unease or said information is "insufficient" | 0.70 |
| Voted against war powers but included cautionary statement | 0.55 |
| Voted against war powers with no caveats | 0.20 |
| Has actively championed the war | 0.05 |

**Data sources:**
- Senator press releases: Each senator's .senate.gov site
- Roll call votes on war powers resolutions (multiple votes now on record):
  - https://www.senate.gov/legislative/votes.htm
  - https://clerk.house.gov/Votes
- News coverage of post-vote statements:
  - The Hill, Politico, CNN, NPR congressional coverage
  - Search: "[Senator name] Iran war statement 2026"
- Congressional Record (verbatim floor statements): https://www.congress.gov/congressional-record

**Update frequency:** Changes with each new vote, briefing, or public statement. Re-assess before each run by searching for recent quotes. This is the most labor-intensive metric to maintain — consider setting up Google Alerts for each target senator + "Iran."

**Weight: 0.25** (highest weight — this is the strongest signal of movability)

---

### M4: Historical Independence Score
**What it measures:** How often has this senator broken with their party on prior votes? Consistent mavericks are more likely to break again.

**Scoring:** Use the senator's "Trump Score" or party-unity score.

| % votes against party/Trump | Score (0–1) |
|---|---|
| 20%+ against | 1.0 |
| 10–19% against | 0.7 |
| 5–9% against | 0.4 |
| <5% against | 0.15 |

**Data sources:**
- FiveThirtyEight "Tracking Congress" (tracks agreement with party): https://projects.fivethirtyeight.com/congress-tracker/
- ProPublica Congress API (free, includes vote records): https://projects.propublica.org/api-docs/congress-api/
- VoteView (academic, DW-NOMINATE ideology scores): https://voteview.com/

**Update frequency:** Changes with each vote but the overall pattern is slow-moving. Pull once per month.

**Weight: 0.10**

---

### M5: Electoral Margin (Inverse)
**What it measures:** How close was their last election? Tighter margins = more fear of losing = more responsive to pressure.

| Last margin of victory | Score (0–1) |
|---|---|
| <3 points | 1.0 |
| 3–6 points | 0.75 |
| 6–10 points | 0.5 |
| 10–20 points | 0.25 |
| 20+ points | 0.05 |

**Data source:**
- Ballotpedia election results: https://ballotpedia.org/United_States_Senate_elections
- Wikipedia election result pages for each senator
- MIT Election Lab data: https://electionlab.mit.edu/data

**Update frequency:** Static (changes only when new election occurs).

**Note:** For open seats where the incumbent is retiring, use the most recent statewide competitive race margin as a proxy.

**Weight: 0.10**

---

### M6: Primary Direction Modifier
**What it measures:** Is their primary threat from the LEFT (making antiwar pressure electorally helpful) or from the RIGHT (making antiwar pressure electorally harmful)?

This is a **modifier**, not a standalone score. It adjusts the persuadability composite up or down.

| Situation | Modifier |
|---|---|
| General election threat from the left/center (e.g., Collins in ME) | × 1.2 |
| No significant primary or general challenge | × 1.0 |
| Primary threat from the right (e.g., Cassidy in LA, Cornyn in TX) | × 0.7 |
| Both primary from right AND general from left | × 0.9 (mixed incentives) |

**Data sources:**
- FEC filings for declared challengers: https://www.fec.gov/data/
- Ballotpedia candidate lists: https://ballotpedia.org/United_States_Senate_elections,_2026
- Cook Political Report race ratings: https://www.cookpolitical.com/ratings/senate-race-ratings
- Sabato's Crystal Ball: https://centerforpolitics.org/crystalball/

**Update frequency:** Changes as candidates file, endorse, or withdraw. Check monthly.

**Weight: Applied as multiplier to PERSUADABILITY subtotal**

---

## LEVERAGE COMPONENT

### M7: Committee Power
**What it measures:** Does the senator sit on a committee with direct procedural control over war-related legislation or funding?

| Committee Position | Score (0–1) |
|---|---|
| Chair of Appropriations, Armed Services, or Foreign Relations | 1.0 |
| Ranking member of same | 0.85 |
| Member of Appropriations, Armed Services, or Foreign Relations | 0.7 |
| Member of Intelligence or Budget (secondary relevance) | 0.4 |
| No relevant committee | 0.15 |

**Data source:**
- Senate committee rosters: https://www.senate.gov/committees/
- House committee rosters: https://www.house.gov/committees
- Note: Susan Collins chairs Appropriations. Roger Wicker chairs Armed Services. Jim Risch chairs Foreign Relations.

**Update frequency:** Changes only with new Congress (Jan of odd years) or rare mid-session reshuffles. Static for 2026.

**Weight: 0.40**

---

### M8: Leadership / Institutional Role
**What it measures:** Does the senator hold a leadership position that gives them disproportionate influence over other members or the legislative agenda?

| Role | Score (0–1) |
|---|---|
| Majority/Minority Leader or Whip | 1.0 |
| Committee Chair (any committee) | 0.7 |
| Caucus/Conference Chair | 0.6 |
| Subcommittee chair on relevant committee | 0.5 |
| Rank-and-file | 0.2 |

**Data source:**
- Senate leadership: https://www.senate.gov/senators/leadership.htm
- Congressional Leadership Fund / caucus sites

**Update frequency:** Static within a Congress.

**Weight: 0.20**

---

### M9: Signal / Narrative Value
**What it measures:** Would this senator's public shift create disproportionate media coverage and/or catalyze other defections? The *first* Republican to break on war funding is worth far more than the fifth.

| Condition | Score (0–1) |
|---|---|
| Would be the FIRST Republican to publicly oppose continued war funding | 1.0 |
| Is a well-known "bellwether" moderate whose stance is widely watched (e.g., Collins, Murkowski) | 0.85 |
| Is a notable hawk whose shift would be surprising and newsworthy | 0.9 |
| Represents a symbolically important state (large military presence, etc.) | 0.6 |
| Rank-and-file, shift would get little coverage | 0.2 |

**Data sources:** This is a qualitative judgment call. Base it on:
- Media mentions: search Google News for frequency of "[Senator name] Iran" articles
- Social media following / platform size of the senator
- Whether the senator is frequently quoted as a swing vote on other issues

**Update frequency:** Changes as the narrative evolves. Re-assess weekly.

**Weight: 0.40**

---

## COMPOSITE FORMULA

```python
# PERSUADABILITY (sum of weighted metrics, then apply primary modifier)
persuadability_raw = (
    0.20 * M1_electoral_proximity +
    0.20 * M2_electorate_alignment +
    0.25 * M3_ambivalence +
    0.10 * M4_independence_history +
    0.10 * M5_margin_inverse +
    0.15 * M6_primary_modifier  # or apply as multiplier — see note
)

# Option A: M6 as weighted additive component (simpler)
persuadability = persuadability_raw

# Option B: M6 as multiplier on the rest (more theoretically correct)
persuadability = (
    0.25 * M1 + 0.25 * M2 + 0.25 * M3 + 0.12 * M4 + 0.13 * M5
) * M6_modifier

# LEVERAGE (sum of weighted metrics)
leverage = (
    0.40 * M7_committee_power +
    0.20 * M8_leadership_role +
    0.40 * M9_signal_value
)

# BASE SCORE
base_score = persuadability * leverage

# PRESSURE SATURATION ADJUSTMENT (Phase 3 — active once Ledger is live)
# M10 adjusts the final score to redirect effort toward undersaturated targets
# This metric is 1.0 when no contacts have been logged, and decays toward 0.2
# as the senator approaches the electoral threat threshold
#
# electoral_threat_threshold = state_midterm_electorate * 0.03 (3%)
# saturation_ratio = current_unique_contacts / electoral_threat_threshold
#
# M10 = max(0.2, 1.0 - (0.8 * saturation_ratio))  # floor at 0.2
#
# Before the Ledger is live, M10 = 1.0 for all senators (no adjustment)

# FINAL SCORE
expected_impact = base_score * M10_pressure_saturation
```

**Note on M10:** This metric is dormant in Phase 1 (set to 1.0 for everyone). It activates in Phase 3 once the Pressure Ledger is collecting data. Its purpose is to make the system self-correcting: as pressure builds on top-ranked targets, the algorithm automatically redirects new participants toward targets that need more volume. This prevents the failure mode where all callers pile onto Collins while Moran receives nothing.

---

## DATA SOURCE SUMMARY TABLE

| Metric | Primary Source | Backup Source | Format | Update Cadence |
|---|---|---|---|---|
| M1: Electoral proximity | Ballotpedia | Wikipedia | Static list | Once (start of cycle) |
| M2a: State PVI | Cook Political Report | Wikipedia PVI table | Number (D+X / R+X) | Every 4 years |
| M2b: War polling | AP-NORC, Gallup, YouGov | State university polls | % support/oppose | Weekly |
| M3: Ambivalence | Senator websites, roll call votes | The Hill, Politico, NPR | Qualitative → coded | After each vote/statement |
| M4: Independence | FiveThirtyEight Congress Tracker | ProPublica Congress API | % party-line votes | Monthly |
| M5: Margin | Ballotpedia / MIT Election Lab | Wikipedia election pages | % margin | Static |
| M6: Primary direction | FEC filings, Cook ratings | Ballotpedia candidates | Qualitative → coded | Monthly |
| M7: Committee | senate.gov committees page | — | Lookup table | Static within Congress |
| M8: Leadership | senate.gov leadership page | — | Lookup table | Static within Congress |
| M9: Signal value | Google News search frequency | Qualitative judgment | Judgment → coded | Weekly |
| M10: Pressure saturation | Pressure Ledger DB (Phase 3) | Internal counter API | Ratio (0–1) | Real-time (when live) |

---

## IMPLEMENTATION NOTES

### Automation Potential
- **Fully automatable:** M1, M2a, M4, M5, M7, M8 (static data, pull once)
- **Semi-automatable:** M2b (requires finding and parsing new polls), M6 (requires checking FEC/Ballotpedia for new candidates)
- **Manual / judgment-heavy:** M3 (requires reading statements), M9 (narrative assessment)
- **Auto-updates from Pressure Ledger:** M10 (fully automatic once Phase 3 is live — pulls from internal counter DB)

### Suggested Re-Run Schedule
- **Daily (during active war):** M3 only — scan for new votes and statements
- **Weekly:** M2b (new polling), M9 (narrative shifts)
- **Monthly:** M4 (voting record updates), M6 (candidate field changes)
- **Once:** M1, M2a, M5, M7, M8

### API Sources for Programmatic Access
- **ProPublica Congress API** (free, key required): Members, votes, bills, statements
  - https://projects.propublica.org/api-docs/congress-api/
- **congress.gov API** (free): Bills, amendments, roll call votes
  - https://api.congress.gov/
- **FEC API** (free): Campaign finance, candidate filings
  - https://api.open.fec.gov/
- **Google Civic Information API** (free with key): Representative lookup by address
  - https://developers.google.com/civic-information
- **OpenSecrets API** (free, key required): Donor data, lobbying
  - https://www.opensecrets.org/open-data/api

### Output Format
The script should produce a ranked list with a full **Contact Card** for each target:

```
Rank | Senator | Party | State | Persuadability | Leverage | SCORE | Key Factor
1    | Collins | R     | ME    | 0.82           | 0.88     | 0.72  | Approps Chair, blue state

CONTACT CARD:
  DC Phone:      (202) 224-2523
  State Offices: Portland (207) 780-3575 | Bangor (207) 945-0417 | ...
  Web Contact:   https://www.collins.senate.gov/contact
  Twitter/X:     @SenatorCollins
  Truth Social:  (if applicable)
  Facebook:      facebook.com/susancollins
  Instagram:     @senatorcollins
  Bluesky:       (if applicable)
  YouTube:       (if applicable)
  Fax:           (202) 224-2693
  Town Halls:    [next scheduled date if known]
```

Include the **Key Factor** column — the single most important reason this person is ranked where they are — so a volunteer can reference it in their call.

---

## CONTACT CHANNELS — Data Sources & Effectiveness

### Channel Inventory
Every target should have the following fields populated (where the channel exists):

| Channel | Data Source | Programmatic Access | Notes |
|---|---|---|---|
| **DC Office Phone** | senate.gov/senators/senators-contact.htm | Static scrape or congress.gov API | Most impactful direct channel — staffers tally calls |
| **State/District Office Phones** | Same page, or individual senator sites | Scrape from senator .gov sites | Often less busy than DC; calls here still get logged |
| **Web Contact Form** | Individual senator .gov websites | URLs are stable, but forms require manual submission | Lower impact than calls; useful for volume |
| **Official Email** | Most senators don't publish direct email; use contact forms | — | Some publish constituent service emails |
| **Twitter / X** | @handle from senator website or Twitter search | X API (paid) | Public pressure; most effective when coordinated |
| **Truth Social** | truthsocial.com/@handle | No public API currently | Relevant for R senators active there; signals base alignment |
| **Facebook** | facebook.com/[page] from senator website | Facebook Graph API (limited) | Largest reach for older demographics |
| **Instagram** | @handle from senator website | Instagram API (limited) | Lower political engagement but visible |
| **Bluesky** | bsky.app/profile/[handle] | AT Protocol API (free, open) | Growing political audience; easier to go viral |
| **Threads** | threads.net/@handle | No public API | Some senators active |
| **YouTube** | youtube.com/@handle or /c/[channel] | YouTube Data API (free w/ key) | Comment sections on war-related videos |
| **Official Website** | [name].senate.gov | — | Check for town hall schedules, press releases |
| **Town Halls / Events** | TownHallProject.com | Manual check / scrape | In-person constituent pressure is extremely high impact |
| **District Offices (in person)** | senator website | Scrape | Showing up in person gets logged differently than a call |
| **Campaign Website** | Usually [name]forsenate.com | FEC links | Campaign sites sometimes have different contact paths |
| **Fax** | senate.gov contact page | — | Congressional offices still receive and tally faxes. FaxZero sends free faxes |

### Channel Effectiveness Weighting
Based on what congressional staffers have publicly described about what gets tracked and influences behavior:

| Channel | Impact Weight | Why |
|---|---|---|
| **In-person visit** (DC or district office) | 1.0 | Staffers report these directly. Hardest to ignore. |
| **Town hall attendance** | 0.90 | Creates public accountability moments. Video clips go viral. |
| **Phone call** (DC office) | 0.85 | Offices tally calls by issue and position. High volume gets flagged. |
| **Phone call** (state/district office) | 0.80 | Same tally system, sometimes more accessible. |
| **Personalized physical letter** | 0.75 | Slow but signals seriousness. |
| **Coordinated Twitter/X campaign** | 0.60 | Public pressure, especially if it trends or gets media pickup. |
| **Fax** | 0.50 | Gets logged. Useful as supplementary channel. |
| **Web contact form** (personalized) | 0.45 | Gets tallied but lower priority than calls. |
| **Truth Social post/reply** | 0.40 | Only for R senators active on the platform; signals base discontent. |
| **Email** (if available) | 0.35 | Often filtered; less impact than calls. |
| **Bluesky** | 0.30 | Growing but smaller audience; useful for narrative-building. |
| **Facebook comment** | 0.25 | Volume matters; individual comments rarely noticed. |
| **Web contact form** (form letter) | 0.20 | Offices discount obvious form letters. |
| **Instagram comment** | 0.15 | Low political signal. |

**Key design principle:** The ranked output should present channels in descending order of effectiveness, so a volunteer with 5 minutes does the highest-impact action first (call), and someone with 30 minutes works down the list.

### Data Sources for Contact Info

**Bulk / Programmatic (best sources):**
- **@unitedstates project (GitHub):** https://github.com/unitedstates/congress-legislators — YAML/JSON with social media handles, office addresses, phone numbers. Community-maintained. **This is the single best bulk data source.**
- **theunitedstates.io:** https://theunitedstates.io/ — clean API wrapper around the above
- **congress.gov API:** https://api.congress.gov/ — member bios, official URLs
- **ProPublica Congress API:** https://projects.propublica.org/api-docs/congress-api/ — includes Twitter handles, contact URLs, office addresses
- **Google Civic Information API:** https://developers.google.com/civic-information — lookup by address, returns representative contact info including social channels

**Manual / Supplementary:**
- **Senate contact directory:** https://www.senate.gov/senators/senators-contact.htm
- **Senate switchboard:** (202) 224-3121 (ask for any senator's office)
- **House directory:** https://www.house.gov/representatives
- **Truth Social:** No bulk source. Manually check truthsocial.com/@[likely_handle] for each target
- **Town hall schedules:** https://townhallproject.com/ — tracks upcoming town halls, telephone town halls, and public events by member
- **Campaign websites:** Found via FEC filings or searching "[name] 2026 campaign"

### Contact Data Schema

```json
{
  "bioguide_id": "C001035",
  "name": "Susan Collins",
  "party": "R",
  "state": "ME",
  "class": 2,
  "up_2026": true,
  "contacts": {
    "dc_phone": "(202) 224-2523",
    "dc_fax": "(202) 224-2693",
    "dc_address": "413 Dirksen Senate Office Building, Washington, DC 20510",
    "state_offices": [
      {"city": "Portland", "phone": "(207) 780-3575", "address": "..."},
      {"city": "Bangor", "phone": "(207) 945-0417", "address": "..."},
      {"city": "Lewiston", "phone": "(207) 784-6969", "address": "..."}
    ],
    "web_form_url": "https://www.collins.senate.gov/contact",
    "social": {
      "twitter": "@SenatorCollins",
      "truth_social": null,
      "facebook": "susancollins",
      "instagram": "senatorcollins",
      "bluesky": null,
      "threads": null,
      "youtube": "SenatorSusanCollins"
    },
    "campaign_site": "https://www.collinsforsenator.com",
    "next_town_hall": null,
    "district_office_hours": "M-F 9am-5pm ET"
  },
  "score": {
    "persuadability": 0.82,
    "leverage": 0.88,
    "expected_impact": 0.72,
    "key_factor": "Chairs Appropriations; $200B war funding flows through her; blue state general election threat"
  }
}
```

---

## PHASE 2: COMMUNICATION FACILITATION (Future Scope)

Phase 1 produces the ranked list with contact info. Phase 2 helps users **act on it**.

### 2A: Call Script Generator
- Input: senator name + user's top concern (cost, troops, constitutional authority, humanitarian)
- Output: 60-second call script personalized to that senator's stated positions and vulnerabilities
- Example: "Senator Collins, I'm calling from [city]. You said on March 13 that this operation should be brief. It's now day 26 with no endgame. I'm asking you to use your position as Appropriations Chair to block the $200B supplemental until Congress votes on authorization."
- Implementation: template engine with per-senator variable slots pulled from M3 data

### 2B: One-Click Contact Dispatch
- Web app or CLI that takes a user's zip code, auto-identifies their senators/rep, pulls ranked targets, and presents:
  - "Call this number" button (tel: link on mobile)
  - Pre-filled web contact form (where senator forms accept URL params)
  - Pre-drafted tweet with senator's handle (Twitter intent URL: `https://twitter.com/intent/tweet?text=...`)
  - Direct links to Truth Social / Facebook / Bluesky profiles
- Google Civic Information API handles zip-to-representative lookup

### 2C: Coordinated Action Scheduler
- "Call Collins Day" — schedule concentrated call volume on specific days
- Staffers have said 100 calls in one day on one issue gets more attention than 100 calls spread over a month
- Calendar integration or push notification reminders
- Coordinate around upcoming votes (especially the $200B supplemental)

### 2D: Impact Tracker
- Callers report: got through? Voicemail or live staffer? What was the staffer's response?
- Aggregate to estimate which offices are overwhelmed (good — volume is working) vs. which need more pressure
- Simple Google Form initially; lightweight web app later
- Tracks total contacts per senator per channel over time

### 2E: Social Media Pressure Coordinator
- Generate shareable content (images, thread templates) tailored to each target senator
- Track hashtag volume and engagement
- Coordinate timing: "Everyone tweet at @SenatorCollins at 2pm ET Thursday with #BlockWarFunding"
- Bluesky's open AT Protocol makes engagement tracking easier than X's paid API

### 2F: Town Hall Alert System
- Scrape TownHallProject.com for upcoming events by target senators
- Push notifications to subscribers in those states
- Provide suggested questions tailored to the senator's stated positions on Iran

### Phase 2 Technical Architecture (sketch)
```
[User enters zip code on getcounted.us]
       |
       v
[Google Civic API → identify representatives]
       |
       v
[Score them against Counted algorithm → ranked list]
       |
       v
[Pull contact card from data store]
       |
       v
[Present: call script + one-click links + social drafts]
       |
       v
[After action: user Gets Counted → Ledger DB → counter increments]
```

- Data stores: static JSON (from @unitedstates GitHub) for contact info, scored JSON for algorithm output, SQLite or Postgres for impact tracking
- Frontend: could be a React app, a static site, or even a CLI tool
- Hosting: Vercel/Netlify for static frontend; any VPS for the tracker API

### Legal / Ethical Notes for Phase 2
- All contact info is from public sources (official .gov sites, public social media)
- Facilitating constituent contact with elected representatives is protected First Amendment activity
- Auto-dialing or robocalling congressional offices is illegal under TCPA; the tool must facilitate human-initiated calls only
- Form letter submissions should be disclosed as such; personalized messages are more effective anyway
- Tool should encourage users to contact their own representatives (zip code validation enforces this)
- No impersonation of constituents

---

## PHASE 3: THE COUNTED LEDGER (Public Constituent Pressure Ledger)

This is the central innovation that transforms the project from a tool into movement infrastructure. Everything in Phases 1 and 2 feeds into and is amplified by this system.

### The Problem It Solves

The collective action problem is the single biggest barrier to antiwar pressure. Specifically:

1. **Invisibility of action:** You call your senator, hang up, and have no idea if you're the 5th caller or the 50,000th. The act feels futile. This suppresses participation.
2. **Invisibility of opposition:** Politicians know that diffuse, unquantified opposition is politically safe to ignore. "People are unhappy" is not a threat. "48,000 of your constituents have logged formal opposition" is.
3. **No social proof:** Humans are far more likely to act when they can see others acting. Without visible momentum, each person assumes they're alone — even when 62% of the country agrees with them.
4. **No feedback loop:** Current activism is open-loop. You take an action and never learn whether it mattered. Closed-loop systems (act → see impact → act again) sustain engagement.

### Core Concept

A **real-time, public, per-senator counter** of verified constituent contacts, visible to everyone: other constituents, media, organizers, and the senator's office itself.

**What the user sees:**

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   COUNTED.                                               │
│                                                          │
│   SENATOR SUSAN COLLINS (R-ME)                           │
│   Appropriations Chair · Up for reelection Nov 2026     │
│                                                          │
│   ████████████████████████████████████░░░░  43,712       │
│   verified Maine constituents have been Counted          │
│                                                          │
│   🔴 +2,847 in the last 24 hours                        │
│   📊 This represents ~5.5% of Maine's 2020 electorate   │
│   📈 Trend: accelerating                                │
│                                                          │
│   [ I contacted Sen. Collins → Get Counted ]             │
│   [ I haven't yet → Contact her now ]                   │
│                                                          │
│   "I will make the war funding vote my primary           │
│    consideration in November 2026."                      │
│   [ Add my pledge ]  ← 31,205 have pledged              │
│                                                          │
│   Have you been Counted? → Share                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Per-senator, not aggregate.**
"500,000 Americans oppose the war" is ignorable. "43,712 of YOUR constituents in YOUR state have formally registered opposition" is not. The counter must be broken down by senator so that the pressure is personal and the electoral math is visible.

**2. Percentage-of-electorate display.**
Raw numbers alone are easy to dismiss ("that's a small fraction of the state"). Converting the count to a percentage of the state's midterm electorate makes the electoral threat concrete. If Collins sees that 6% of Maine's typical midterm electorate has logged opposition, that's larger than her margin of victory in some scenarios. The tool should calculate and display this automatically.

Electorate denominators (approximate, from most recent midterm turnout):
- Pull from: https://www.electproject.org/election-data/voter-turnout-data (Michael McDonald's US Elections Project)
- Or: Secretary of State websites for each state
- Use most recent midterm (2022) turnout as the denominator, since 2026 is a midterm year

**3. Verified constituent, not just anyone.**
The count is only credible if it represents actual constituents. Verification approach:

| Level | Method | Confidence | Friction |
|---|---|---|---|
| **Basic** | Zip code matches senator's state | Medium | Very low |
| **Standard** | Zip + name + email (deduplicated) | Medium-high | Low |
| **Enhanced** | Zip + name + email + phone confirmation via SMS code | High | Moderate |
| **Voter-linked** | Cross-reference against public voter file | Very high | Higher (privacy concerns) |

**Recommendation:** Start with **Standard** (zip + name + email with deduplication). It's the right tradeoff between credibility and participation friction. Enhanced (SMS) can be added later if credibility is challenged. Voter-file linking is powerful but introduces privacy issues that could suppress participation.

Deduplication is critical: one person = one count, regardless of how many times they contact the senator. The counter measures unique constituents, not total contacts.

**4. The Electoral Pledge.**
Beyond "I contacted my senator," the tool should offer a specific pledge:

> "I will make the war funding vote my primary consideration when I vote in November 2026."

This converts vague opposition into a specific, credible electoral threat. The pledge count is displayed separately and prominently. This is the number that should keep a senator up at night — it's not just people who are unhappy, it's people who are telling you in advance they will vote on this issue.

**5. Action logging, not just signing.**
The counter should distinguish between:

| Action Type | Weight in Display | Why |
|---|---|---|
| Pledged to vote on this issue | Shown prominently | Direct electoral threat |
| Called DC office | Logged | High-impact action taken |
| Called state office | Logged | High-impact action taken |
| Sent web form message | Logged | Action taken |
| Attended town hall | Logged + featured | Highest-impact action |
| Visited district office | Logged + featured | Highest-impact action |
| Posted on social media | Logged | Lower impact but visible |
| Just registered opposition (no action yet) | Counted separately | Converts later |

The tool should track BOTH the headline count (unique constituents who have engaged) AND the breakdown of what actions they took. This serves two purposes: it gives the senator's office a picture of the intensity of opposition (not just volume), and it encourages users who only signed to come back and escalate to a call.

**6. Embeddable widget.**
The per-senator counter should be available as an embeddable widget (iframe or JS snippet) that local news sites, blogs, organizers, and social media can drop onto their pages. This is how the counter spreads virally without requiring centralized marketing.

```html
<!-- Embed the Collins counter on your site -->
<iframe src="https://getcounted.us/embed/collins-me"
        width="400" height="200" frameborder="0"></iframe>
```

The widget auto-updates in real time. Every site that embeds it becomes a recruitment channel.

**7. Trending / velocity display.**
The counter should show not just the total but the **rate of change**: "+2,847 in the last 24 hours" and whether the trend is accelerating or decelerating. Acceleration is the most powerful signal — it tells both the senator and potential participants that momentum is building.

### The Feedback Loop Into the Algorithm

The Pressure Ledger feeds back into the scoring algorithm in two ways:

**Feedback 1: Pressure Saturation Rebalancing**
If Collins has received 43,000 constituent contacts and Moran has received 800, the algorithm should shift targeting priority toward Moran. The marginal value of the 43,001st call to Collins is lower than the 801st call to Moran. Add a new metric:

**M10: Pressure Saturation (inverse)**

```python
# Saturation score: higher when the senator has received FEWER contacts
# relative to what's needed to create electoral threat
saturation_ratio = current_contacts / electoral_threat_threshold
# electoral_threat_threshold = e.g., 3% of state midterm electorate

if saturation_ratio >= 1.0:
    M10 = 0.2  # Still worth calling, but deprioritize
elif saturation_ratio >= 0.5:
    M10 = 0.6  # Getting there, keep pushing
else:
    M10 = 1.0  # Undersaturated, high marginal value per call
```

This makes the system self-correcting. As pressure builds on top targets, the algorithm redirects new participants toward targets that need more volume.

**Feedback 2: Ambivalence Re-scoring**
If a senator's office changes its public language in response to pressure (e.g., Collins moves from "the president has inherent authority" to "we need to see a timeline"), M3 (Demonstrated Ambivalence) should be updated. The Pressure Ledger's impact tracker (did staffers say anything notable?) provides the signal for this update.

### Data Architecture

```
┌─────────────────────────────────────────────────────┐
│                  PRESSURE LEDGER DB                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  constituents table:                                │
│    id (UUID)                                        │
│    name                                             │
│    email (hashed for dedup, not stored in plain)    │
│    zip_code                                         │
│    state (derived from zip)                         │
│    senator_bioguide_ids[] (derived from zip/state)  │
│    created_at                                       │
│    pledged_to_vote_on_issue (boolean)               │
│    pledge_date                                      │
│                                                     │
│  actions table:                                     │
│    id (UUID)                                        │
│    constituent_id (FK)                              │
│    senator_bioguide_id                              │
│    action_type (enum: call_dc, call_state,          │
│      web_form, town_hall, office_visit,             │
│      social_media, fax, letter)                     │
│    channel_detail (e.g., which state office)        │
│    staffer_response (free text, optional)           │
│    action_date                                      │
│                                                     │
│  counters table (materialized / cached):            │
│    senator_bioguide_id                              │
│    total_unique_constituents                        │
│    total_pledges                                    │
│    contacts_last_24h                                │
│    contacts_last_7d                                 │
│    pct_of_electorate                                │
│    trend (accelerating / steady / decelerating)     │
│    last_updated                                     │
│                                                     │
│  state_electorate_ref table:                        │
│    state                                            │
│    midterm_2022_turnout                             │
│    registered_voters                                │
│    voting_age_population                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Privacy considerations:**
- Emails are hashed (SHA-256 + salt) for deduplication; plaintext email is never stored
- Names are stored for credibility but could be displayed as "J. Smith from Portland, ME" (initial + last name + city) to protect privacy while showing geographic distribution
- No SSN, DOB, or other PII beyond what's needed
- Users can delete their record at any time (GDPR-style right to deletion even though this isn't legally required in the US — it builds trust)
- The public-facing counter shows aggregate numbers only, never individual names (unless the user explicitly opts in to a public list)

### Trust & Anti-Gaming

The counter is only powerful if it's credible. Risks and mitigations:

| Risk | Mitigation |
|---|---|
| Bot signups inflating counts | Email verification + rate limiting per IP + CAPTCHA |
| Out-of-state people signing | Zip code validation against USPS database; state derivation is automatic |
| Same person signing multiple times | Email hash deduplication; one count per unique email per senator |
| Astroturfing / coordinated fake signups | Anomaly detection on signup velocity; flag suspicious patterns for manual review |
| Political opponents discrediting the count | Transparency: publish methodology, deduplication rates, and allow third-party audits |
| Senator's office disputing the numbers | Offer to share anonymized, aggregated data with the office upon request; transparency builds credibility |

### Embeddable Widget Technical Spec

```javascript
// Counted widget embed code (provided to organizers, media, bloggers)
<script src="https://getcounted.us/widget.js"
        data-senator="collins-me"
        data-style="compact|full|counter-only"
        data-theme="light|dark">
</script>

// Widget hits a public API endpoint:
// GET /api/v1/counter/{senator_id}
// Returns:
{
  "senator": "Susan Collins",
  "state": "ME",
  "party": "R",
  "unique_constituents": 43712,
  "pledges": 31205,
  "last_24h": 2847,
  "last_7d": 14203,
  "pct_electorate": 5.5,
  "trend": "accelerating",
  "trend_pct_change_7d": 12.3,
  "updated_at": "2026-03-26T14:30:00Z"
}
```

The widget should be lightweight (<20KB), accessible (WCAG 2.1 AA), mobile-responsive, and load asynchronously so it doesn't slow down host pages.

### Media & Amplification Strategy

The Counted Ledger is most powerful when the numbers are reported by media. Design for this:

- **Press page:** Auto-generated press-friendly summaries: "As of March 26, 43,712 verified Maine residents have been Counted in opposition to Iran war funding — representing 5.5% of the state's 2022 midterm electorate. Source: getcounted.us"
- **Milestone alerts:** Auto-notify press list when a senator's count crosses significant thresholds (10K, 25K, 50K, 100K, or key percentages of electorate like 1%, 3%, 5%)
- **Comparative rankings:** "Senator Collins has more constituents Counted on Iran than any other Republican senator" — creates competitive dynamics and news hooks
- **State-level media targeting:** Local media (Portland Press Herald, Bangor Daily News for Collins; Austin American-Statesman for Cornyn) is more likely to cover state-specific constituent numbers than national outlets. Build a per-state press contact list.
- **Data download:** Offer journalists downloadable CSVs of aggregate (non-PII) data: counts by state, by day, by action type. Make it easy to build charts and graphics.

### How the Counted Ledger Changes the Full System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     COUNTED — FULL SYSTEM FLOW                   │
│                                                                  │
│  ┌─────────────┐     ┌──────────────────┐    ┌───────────────┐  │
│  │  PHASE 1    │     │   PHASE 2        │    │   PHASE 3     │  │
│  │  Scoring    │────▶│   Contact        │───▶│   Counted     │  │
│  │  Algorithm  │     │   Facilitation   │    │   Ledger      │  │
│  └──────┬──────┘     └──────────────────┘    └───────┬───────┘  │
│         │                                            │          │
│         │            ┌──────────────────┐             │          │
│         └────────────│   FEEDBACK LOOP  │◀────────────┘          │
│                      │   M10 Saturation │                        │
│                      │   M3 Re-scoring  │                        │
│                      └──────────────────┘                        │
│                                                                  │
│  User flow:                                                      │
│  1. Enter zip code                                               │
│  2. See ranked targets with scores + WHY they matter             │
│  3. See current Counted tally for each target                    │
│  4. Choose action: call / tweet / visit / web form               │
│  5. Get personalized script + one-click contact                  │
│  6. Log action → Get Counted → counter increments in real time   │
│  7. Optionally pledge to vote on this issue                      │
│  8. See updated counter → feel part of something growing         │
│  9. Share: "Have you been Counted?" → invite others              │
│  10. Come back when algorithm re-ranks and suggests new targets  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### MVP Scope for Counted Ledger

To ship fast, the minimum viable version needs only:

1. **Landing page** per senator with counter, pledge button, and contact links
2. **Signup form:** name + email + zip (email verification link)
3. **Action logger:** "I called / I emailed / I tweeted" (self-reported)
4. **Counter API:** returns current counts for widget embed
5. **Basic widget:** embeddable counter showing total + trend

Everything else (anomaly detection, press page automation, algorithm feedback loop, SMS verification) can be added iteratively.

**Tech stack for MVP:**
- Frontend: Next.js or plain React (deploys to Vercel free tier)
- Backend API: Python FastAPI or Node Express
- Database: PostgreSQL (Supabase free tier or Railway)
- Email verification: Resend or SendGrid free tier
- Zip-to-state lookup: USPS API or static zip code database (free, many available on GitHub)
- Hosting: Vercel (frontend) + Railway or Fly.io (backend)
- Cost: $0–$20/month at MVP scale

---

## CALIBRATION / SANITY CHECKS

Before trusting the output, verify that:
1. Collins (R-ME) scores in the top 3 — if she doesn't, weights are wrong
2. Tom Cotton (R-AR) scores near the bottom — if he doesn't, persuadability is broken
3. Rand Paul (R-KY) scores moderate (already moved, so leverage of calling him is limited despite agreement)
4. No Democrat in a safe blue state scores above any vulnerable Republican — calling Schumer about Iran is preaching to the choir
5. The primary-direction modifier correctly penalizes senators whose rightward primary threat makes antiwar positioning dangerous for them

---

## VERSION HISTORY

- **v1.0** — March 26, 2026. Initial spec. Scoring algorithm with 9 metrics.
- **v1.1** — March 26, 2026. Added contact channel inventory, effectiveness weights, data sources, contact data schema, and Phase 2 communication facilitation roadmap.
- **v1.2** — March 26, 2026. Added Phase 3: Counted Ledger. Added M10 (Pressure Saturation) to scoring formula. Updated purpose statement with theory of change. Added feedback loop architecture, embeddable widget spec, data schema, anti-gaming measures, media strategy, and MVP scope. Named the project **Counted**.
