"""Output generation: terminal table, JSON file, CSV file."""

import json
import csv
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def print_terminal(ranked):
    print()
    print("  COUNTED — Pressure Target Rankings")
    print("  " + "=" * 60)
    print()

    header = (f"  {'Rank':<5} {'Senator':<22} {'Pty':<4} {'St':<4} "
              f"{'Pers.':<7} {'Lev.':<7} {'SCORE':<8} Key Factor")
    print(header)
    print("  " + "-" * 95)

    for s in ranked[:20]:
        print(f"  {s.rank:<5} {s.senator.name:<22} {s.senator.party:<4} "
              f"{s.senator.state:<4} {s.scores.persuadability:<7.3f} "
              f"{s.scores.leverage:<7.3f} {s.scores.expected_impact:<8.4f} "
              f"{s.key_factor}")

    print("  " + "-" * 95)
    print()

    all_scores = [s.scores.expected_impact for s in ranked]
    r_scores = [s.scores.expected_impact for s in ranked if s.senator.party == "R"]
    d_scores = [s.scores.expected_impact for s in ranked
                if s.senator.party in ("D", "I")]

    print(f"  Senators scored: {len(ranked)}")
    if all_scores:
        print(f"  Score range: {min(all_scores):.4f} - {max(all_scores):.4f}")
    if r_scores:
        print(f"  Republican avg: {sum(r_scores)/len(r_scores):.4f}")
    if d_scores:
        print(f"  Democrat/Ind avg: {sum(d_scores)/len(d_scores):.4f}")

    top5_r_2026 = all(
        s.senator.party == "R" and s.senator.up_2026 for s in ranked[:5]
    )
    print(f"  Top 5 all R up in 2026: {'YES' if top5_r_2026 else 'NO'}")
    print()

    if ranked:
        top = ranked[0]
        print(f"  #1 TARGET: {top.senator.name} "
              f"({top.senator.party}-{top.senator.state})")
        print(f"  {'-' * 50}")
        _print_contact(top.contact)
        print()


def _print_contact(c):
    for label, value in [
        ("DC Phone", c.dc_phone), ("DC Fax", c.dc_fax),
        ("Web Contact", c.web_form_url), ("Twitter/X", c.twitter),
        ("Facebook", c.facebook), ("Instagram", c.instagram),
        ("Bluesky", c.bluesky), ("YouTube", c.youtube),
        ("Truth Social", c.truth_social), ("Campaign", c.campaign_site),
    ]:
        if value:
            print(f"  {label + ':':<16} {value}")
    for office in c.state_offices:
        city = office.get("city", "")
        phone = office.get("phone", "")
        if city or phone:
            print(f"  {'State Office:':<16} {city} {phone}")


def _senator_to_dict(s):
    return {
        "rank": s.rank,
        "bioguide_id": s.senator.bioguide_id,
        "name": s.senator.name,
        "party": s.senator.party,
        "state": s.senator.state,
        "senate_class": s.senator.senate_class,
        "up_2026": s.senator.up_2026,
        "scores": {
            "m1_electoral_proximity": s.scores.m1,
            "m2_electorate_alignment": s.scores.m2,
            "m3_ambivalence": s.scores.m3,
            "m4_independence": s.scores.m4,
            "m5_margin": s.scores.m5,
            "m6_primary_modifier": s.scores.m6,
            "m7_committee_power": s.scores.m7,
            "m8_leadership": s.scores.m8,
            "m9_signal_value": s.scores.m9,
            "m10_saturation": s.scores.m10,
            "persuadability": s.scores.persuadability,
            "leverage": s.scores.leverage,
            "expected_impact": s.scores.expected_impact,
        },
        "key_factor": s.key_factor,
        "contact": {
            "dc_phone": s.contact.dc_phone,
            "dc_fax": s.contact.dc_fax,
            "state_offices": s.contact.state_offices,
            "web_form_url": s.contact.web_form_url,
            "twitter": s.contact.twitter,
            "facebook": s.contact.facebook,
            "instagram": s.contact.instagram,
            "bluesky": s.contact.bluesky,
            "youtube": s.contact.youtube,
            "truth_social": s.contact.truth_social,
            "campaign_site": s.contact.campaign_site,
        },
    }


def write_json(ranked):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "ranked_senators.json"
    with open(path, "w") as f:
        json.dump([_senator_to_dict(s) for s in ranked], f, indent=2)
    print(f"  JSON: {path}")


def write_csv(ranked):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "ranked_senators.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Name", "Party", "State", "Score",
                         "Key Factor", "DC Phone", "Twitter"])
        for s in ranked:
            writer.writerow([
                s.rank, s.senator.name, s.senator.party, s.senator.state,
                f"{s.scores.expected_impact:.4f}", s.key_factor,
                s.contact.dc_phone, s.contact.twitter,
            ])
    print(f"  CSV:  {path}")
