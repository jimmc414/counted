#!/usr/bin/env python3
"""Build frontend data files from Phase 1 output.

Reads:  output/ranked_senators.json, data/committees.json, data/ambivalence.json
Writes: counted-web/src/data/{scored_senators,call_scripts,zip_to_state}.json
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "counted-web" / "src" / "data"

KEY_FACTOR_MAP = {
    "Committee power": {
        "short": "Holds war funding power",
        "long": "Sits on a committee that controls war funding. Your call reaches someone who can directly block the $200B.",
    },
    "Signal/narrative value if shifted": {
        "short": "Could break the dam",
        "long": "If this senator breaks, it changes the political calculus. One defection gives cover to others.",
    },
    "Electoral proximity (up 2026)": {
        "short": "Faces voters in November",
        "long": "Up for reelection in 2026. Every call is a reminder this vote follows them to the ballot box.",
    },
    "Blue-state electorate": {
        "short": "Represents antiwar voters",
        "long": "Represents a state where the majority oppose this war. Ignoring constituents is an electoral risk.",
    },
    "Demonstrated ambivalence on war": {
        "short": "Already wavering",
        "long": "Has publicly hedged or set conditions on support. Pressure now could tip the balance.",
    },
    "Leadership role": {
        "short": "Party leadership",
        "long": "Holds a leadership position that sets the party agenda. Pressure here ripples across the caucus.",
    },
}

PERSONALIZED_SCRIPTS = {
    "C001035": (
        "Hi, I'm [NAME] from [CITY], Maine. As Chair of the Senate Appropriations "
        "Committee, Senator Collins, you have direct control over whether the $200 billion "
        "Iran war supplemental moves forward. You've indicated you have concerns about this "
        "spending \u2014 I'm calling to ask you to act on those concerns and require a full "
        "congressional authorization vote before releasing any war funding. This will be my "
        "top issue when I vote in November. Thank you."
    ),
    "T000476": (
        "Hi, I'm [NAME] from [CITY], North Carolina. Senator Tillis, as a member of the "
        "Armed Services Committee, you oversee military operations that affect North "
        "Carolina's military families directly. You've raised questions about the scope of "
        "this conflict \u2014 please follow through by voting against the $200 billion "
        "supplemental until Congress holds a proper authorization vote. I'll be watching "
        "this vote closely in November. Thank you."
    ),
    "S001198": (
        "Hi, I'm [NAME] from [CITY], Alaska. Senator Sullivan, as a Marine veteran and "
        "Armed Services Committee member, your voice on military matters carries enormous "
        "weight. A vote against unauthorized war spending from you would send a powerful "
        "signal that both parties believe in congressional oversight. Please vote against "
        "the $200 billion supplemental until a proper authorization vote is held. Thank you."
    ),
    "C001047": (
        "Hi, I'm [NAME] from [CITY], West Virginia. Senator Capito, you sit on the "
        "Appropriations Committee that controls this $200 billion war spending package. "
        "You've expressed real doubts about where this money is going \u2014 West Virginia "
        "could use those resources right here at home. Please vote to require a full "
        "authorization debate before any more war funding is approved. Thank you."
    ),
    "E000295": (
        "Hi, I'm [NAME] from [CITY], Iowa. Senator Ernst, you sit on both the Armed "
        "Services and Appropriations committees \u2014 you have unique power over both the "
        "military mission and the money. You've publicly questioned aspects of this "
        "conflict. I'm asking you to use your position to require Congress to vote on "
        "authorization before approving $200 billion in war funding. Iowa voters are "
        "watching. Thank you."
    ),
    "D000563": (
        "Hi, I'm [NAME] from [CITY], Illinois. Senator Durbin, as Minority Whip and a "
        "senior Appropriations Committee member, you set the direction for the Democratic "
        "caucus on this vote. I'm calling to ask you to whip votes against the $200 "
        "billion Iran war supplemental until Congress holds a full authorization vote. "
        "Your leadership position exists for moments exactly like this. Thank you."
    ),
    "R000122": (
        "Hi, I'm [NAME] from [CITY], Rhode Island. Senator Reed, as Ranking Member of "
        "the Armed Services Committee, you are the top Democrat overseeing military "
        "operations. I'm calling to urge you to use that authority to demand a full "
        "authorization vote before any additional war funding moves forward. Congress "
        "must not hand over $200 billion without debate. Thank you."
    ),
    "S001181": (
        "Hi, I'm [NAME] from [CITY], New Hampshire. Senator Shaheen, you serve as "
        "Ranking Member on Foreign Relations and sit on Armed Services \u2014 few senators "
        "have more direct oversight of this conflict. I'm calling to ask you to lead the "
        "push for a full congressional authorization vote before the $200 billion war "
        "supplemental advances. This is exactly the oversight role you were elected to "
        "fill. Thank you."
    ),
    "M001153": (
        "Hi, I'm [NAME] from [CITY], Alaska. Senator Murkowski, you've built a reputation "
        "for independent judgment that Alaskans respect. As an Appropriations Committee "
        "member, you have a direct vote on whether this $200 billion goes to war or stays "
        "available for priorities at home. Please vote to require proper congressional "
        "authorization before any more war funding. Thank you."
    ),
    "R000605": (
        "Hi, I'm [NAME] from [CITY], South Dakota. Senator Rounds, you sit on both the "
        "Armed Services and Foreign Relations committees \u2014 you see this conflict from "
        "every angle. I'm calling to ask you to require a full congressional authorization "
        "vote before approving $200 billion in war spending. South Dakotans deserve to "
        "know their senator demanded accountability. Thank you."
    ),
    "M001111": (
        "Hi, I'm [NAME] from [CITY], Washington. Senator Murray, as Ranking Member of "
        "the Appropriations Committee, you are the top Democrat on spending decisions. "
        "I'm calling to ask you to use every tool available to block the $200 billion "
        "Iran war supplemental until Congress holds a full authorization vote. Washington "
        "state overwhelmingly opposes this war. Thank you."
    ),
    "P000595": (
        "Hi, I'm [NAME] from [CITY], Michigan. Senator Peters, as a member of the Armed "
        "Services Committee, you have direct oversight of the military operations this "
        "funding would support. Michigan has a large veteran and military family population "
        "who deserve a proper debate. Please vote against the $200 billion supplemental "
        "until Congress holds an authorization vote. Thank you."
    ),
    "R000584": (
        "Hi, I'm [NAME] from [CITY], Idaho. Senator Risch, as Chair of the Foreign "
        "Relations Committee, you are the single most important voice on whether this war "
        "has proper congressional authorization. I'm calling to ask you to hold hearings "
        "and require a full authorization vote before the $200 billion supplemental "
        "advances. Your committee exists for exactly this purpose. Thank you."
    ),
    "W000805": (
        "Hi, I'm [NAME] from [CITY], Virginia. Senator Warner, as Ranking Member of the "
        "Intelligence Committee, you have access to information most senators don't. I'm "
        "calling to ask you to use your knowledge and your platform to demand a full "
        "authorization vote before Congress approves $200 billion in war spending. "
        "Virginia's military families trust you to provide oversight. Thank you."
    ),
    "C001056": (
        "Hi, I'm [NAME] from [CITY], Texas. Senator Cornyn, as Chair of the Finance "
        "Committee and a member of the Intelligence Committee, you understand both the "
        "fiscal impact and the intelligence realities of this conflict. I'm asking you to "
        "demand a full congressional authorization vote before approving $200 billion in "
        "war funding. Texas taxpayers deserve that accountability. Thank you."
    ),
    "C001075": (
        "Hi, I'm [NAME] from [CITY], Louisiana. Senator Cassidy, you sit on both the "
        "Appropriations and Foreign Relations committees \u2014 you see both the cost and "
        "the diplomacy. You've expressed concerns about the direction of this conflict. "
        "Please act on those concerns and vote to require a full authorization vote before "
        "any more war funding is approved. Thank you."
    ),
    "M000934": (
        "Hi, I'm [NAME] from [CITY], Kansas. Senator Moran, you've been more vocal than "
        "most in questioning this war \u2014 and as an Appropriations Committee member, you "
        "have the power to act on those doubts. I'm calling to ask you to vote against "
        "the $200 billion war supplemental until Congress holds a proper authorization "
        "debate. Kansas voters support your independence on this. Thank you."
    ),
    "B001277": (
        "Hi, I'm [NAME] from [CITY], Connecticut. Senator Blumenthal, as a member of the "
        "Armed Services Committee, you have direct oversight of these military operations. "
        "Connecticut has a strong tradition of demanding that wars be properly authorized. "
        "I'm calling to ask you to vote against the $200 billion supplemental until "
        "Congress holds a full authorization vote. Thank you."
    ),
    "S001194": (
        "Hi, I'm [NAME] from [CITY], Hawaii. Senator Schatz, as a member of the "
        "Appropriations Committee, you have a direct vote on whether $200 billion goes to "
        "war. Hawaii knows the cost of military conflict firsthand. I'm calling to ask you "
        "to vote against the war supplemental until Congress holds a proper authorization "
        "vote. Thank you."
    ),
    "D000622": (
        "Hi, I'm [NAME] from [CITY], Illinois. Senator Duckworth, as a combat veteran who "
        "knows the true cost of war and a member of the Armed Services Committee, your "
        "voice carries unique moral authority. I'm calling to ask you to demand a full "
        "congressional authorization vote before approving $200 billion in war funding. "
        "Sending Americans into harm's way without a vote is wrong. Thank you."
    ),
}

GENERIC_SCRIPT = (
    "Hi, I'm [NAME] from [CITY], [STATE]. I'm calling to urge Senator [SENATOR] to vote "
    "against the $200 billion Iran war supplemental funding unless Congress holds a full "
    "authorization vote. This war was started without congressional approval. I will be "
    "making this my top voting issue in November. Thank you."
)

# USPS ZIP3 prefix → state code. Gaps = unassigned prefixes.
ZIP3_RANGES = [
    (1, 5, "NY"),
    (6, 9, "PR"),
    (10, 27, "MA"),
    (28, 29, "RI"),
    (30, 38, "NH"),
    (39, 49, "ME"),
    (50, 59, "VT"),
    (60, 69, "CT"),
    (70, 89, "NJ"),
    (100, 149, "NY"),
    (150, 196, "PA"),
    (197, 199, "DE"),
    (200, 200, "DC"),
    (201, 201, "VA"),
    (202, 205, "DC"),
    (206, 219, "MD"),
    (220, 246, "VA"),
    (247, 268, "WV"),
    (270, 289, "NC"),
    (290, 299, "SC"),
    (300, 319, "GA"),
    (320, 349, "FL"),
    (350, 369, "AL"),
    (370, 385, "TN"),
    (386, 397, "MS"),
    (398, 399, "GA"),
    (400, 427, "KY"),
    (430, 458, "OH"),
    (460, 479, "IN"),
    (480, 499, "MI"),
    (500, 528, "IA"),
    (530, 549, "WI"),
    (550, 567, "MN"),
    (570, 577, "SD"),
    (580, 588, "ND"),
    (590, 599, "MT"),
    (600, 629, "IL"),
    (630, 658, "MO"),
    (660, 679, "KS"),
    (680, 693, "NE"),
    (700, 714, "LA"),
    (716, 729, "AR"),
    (730, 749, "OK"),
    (750, 799, "TX"),
    (800, 816, "CO"),
    (820, 831, "WY"),
    (832, 838, "ID"),
    (840, 847, "UT"),
    (850, 865, "AZ"),
    (870, 884, "NM"),
    (885, 885, "TX"),
    (889, 898, "NV"),
    (900, 961, "CA"),
    (963, 966, "HI"),
    (968, 968, "AS"),
    (969, 969, "GU"),
    (970, 979, "OR"),
    (980, 994, "WA"),
    (995, 999, "AK"),
]


def slugify(name, state):
    slug = name.lower()
    slug = re.sub(r"[^a-z\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return f"{slug}-{state.lower()}"


def build_zip_to_state():
    mapping = {}
    for start, end, state in ZIP3_RANGES:
        for i in range(start, end + 1):
            mapping[f"{i:03d}"] = state
    return mapping


def transform_senator(senator):
    slug = slugify(senator["name"], senator["state"])
    kf = senator.get("key_factor", "")
    kf_mapped = KEY_FACTOR_MAP.get(kf, {"short": kf, "long": kf})

    contact = senator.get("contact", {})
    social_fields = [
        "twitter", "facebook", "instagram", "bluesky", "youtube", "truth_social",
    ]
    social = {f: contact[f] for f in social_fields if contact.get(f)}

    return {
        "rank": senator["rank"],
        "slug": slug,
        "bioguide_id": senator["bioguide_id"],
        "name": senator["name"],
        "party": senator["party"],
        "state": senator["state"],
        "senate_class": senator.get("senate_class"),
        "up_2026": senator.get("up_2026", False),
        "expected_impact": round(senator["scores"]["expected_impact"], 4),
        "key_factor": kf,
        "key_factor_short": kf_mapped["short"],
        "key_factor_long": kf_mapped["long"],
        "scores": senator["scores"],
        "contact": {
            "dc_phone": contact.get("dc_phone"),
            "dc_fax": contact.get("dc_fax"),
            "state_offices": contact.get("state_offices", []),
            "web_form_url": contact.get("web_form_url"),
            "social": social,
        },
        "call_script": slug,
        "counted": None,
    }


def build_call_scripts(senators):
    scripts = {"generic": GENERIC_SCRIPT}
    bio_to_slug = {s["bioguide_id"]: s["slug"] for s in senators}
    for bio_id, script in PERSONALIZED_SCRIPTS.items():
        slug = bio_to_slug.get(bio_id)
        if slug:
            scripts[slug] = script
    return scripts


def main():
    phase1 = json.loads((ROOT / "output" / "ranked_senators.json").read_text())
    senators = [transform_senator(s) for s in phase1]

    slugs = [s["slug"] for s in senators]
    dupes = [s for s in slugs if slugs.count(s) > 1]
    assert not dupes, f"Duplicate slugs: {set(dupes)}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scored = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "senators": senators,
    }
    out = OUTPUT_DIR / "scored_senators.json"
    out.write_text(json.dumps(scored, indent=2))
    print(f"  scored_senators.json: {len(senators)} senators, {out.stat().st_size:,} bytes")

    scripts = build_call_scripts(senators)
    out = OUTPUT_DIR / "call_scripts.json"
    out.write_text(json.dumps(scripts, indent=2))
    print(f"  call_scripts.json: {len(scripts) - 1} personalized + generic, {out.stat().st_size:,} bytes")

    zip_map = build_zip_to_state()
    out = OUTPUT_DIR / "zip_to_state.json"
    out.write_text(json.dumps(zip_map, sort_keys=True))
    print(f"  zip_to_state.json: {len(zip_map)} ZIP3 prefixes, {out.stat().st_size:,} bytes")

    # Verification
    dc_phones = sum(1 for s in senators if s["contact"]["dc_phone"])
    personalized = sum(1 for s in senators if s["slug"] in scripts)
    print(f"\n  DC phones: {dc_phones}/100")
    print(f"  Personalized scripts: {personalized}/20")
    assert dc_phones == 100, f"Missing DC phones: {100 - dc_phones}"
    assert personalized == 20, f"Expected 20 personalized scripts, got {personalized}"


if __name__ == "__main__":
    main()
