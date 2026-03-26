#!/usr/bin/env python3
"""Print verification coverage stats across all per-member contact files."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
VERIFIED_DIR = DATA / "verified_contacts"

CONTACT_FIELDS = [
    "dc_phone", "dc_fax", "web_form_url",
    "twitter", "facebook", "instagram", "bluesky",
    "youtube", "truth_social", "campaign_site",
]


def analyze_member(path):
    """Return per-field status counts for one member file."""
    record = json.loads(path.read_text())
    stats = {"name": record["name"], "bioguide_id": record["bioguide_id"]}
    field_statuses = {}

    for field_name in CONTACT_FIELDS:
        triple = record.get("contacts", {}).get(field_name, {})
        field_statuses[field_name] = triple.get("status", "placeholder")

    stats["field_statuses"] = field_statuses
    stats["office_count"] = len(record.get("state_offices", []))

    # Count offices with verified phones
    stats["offices_with_address"] = sum(
        1 for o in record.get("state_offices", [])
        if o.get("address", {}).get("value", "")
    )
    stats["offices_verified"] = sum(
        1 for o in record.get("state_offices", [])
        if o.get("phone", {}).get("status") == "verified"
    )

    return stats


def print_report(chamber, members_dir):
    """Print a coverage report for one chamber."""
    files = sorted(members_dir.glob("*.json"))
    if not files:
        print(f"  No files found in {members_dir}")
        return

    all_stats = [analyze_member(f) for f in files]
    total = len(all_stats)

    print(f"\n{'='*60}")
    print(f"  {chamber.upper()} — {total} members")
    print(f"{'='*60}")

    # Per-field summary
    status_labels = ["verified", "unverified", "placeholder", "not_found"]
    print(f"\n  {'Field':<16} {'verified':>9} {'unverified':>11} {'placeholder':>12} {'not_found':>10}")
    print(f"  {'-'*16} {'-'*9} {'-'*11} {'-'*12} {'-'*10}")

    for field_name in CONTACT_FIELDS:
        counts = {s: 0 for s in status_labels}
        for m in all_stats:
            status = m["field_statuses"].get(field_name, "placeholder")
            counts[status] = counts.get(status, 0) + 1
        print(f"  {field_name:<16} {counts['verified']:>9} {counts['unverified']:>11} "
              f"{counts['placeholder']:>12} {counts['not_found']:>10}")

    # Office stats
    total_offices = sum(m["office_count"] for m in all_stats)
    with_address = sum(m["offices_with_address"] for m in all_stats)
    offices_verified = sum(m["offices_verified"] for m in all_stats)
    print(f"\n  State/District Offices: {total_offices} total, "
          f"{with_address} with addresses, {offices_verified} verified")

    # Overall verification progress
    total_fields = total * len(CONTACT_FIELDS)
    verified = sum(
        1 for m in all_stats
        for f in CONTACT_FIELDS
        if m["field_statuses"].get(f) == "verified"
    )
    unverified = sum(
        1 for m in all_stats
        for f in CONTACT_FIELDS
        if m["field_statuses"].get(f) == "unverified"
    )
    print(f"\n  Overall: {verified}/{total_fields} verified, "
          f"{unverified}/{total_fields} unverified (have data, need checking), "
          f"{total_fields - verified - unverified}/{total_fields} placeholder/not_found")

    # Members with most verified fields
    member_verified = []
    for m in all_stats:
        v = sum(1 for f in CONTACT_FIELDS if m["field_statuses"].get(f) == "verified")
        if v > 0:
            member_verified.append((m["name"], m["bioguide_id"], v))
    if member_verified:
        member_verified.sort(key=lambda x: -x[2])
        print(f"\n  Top verified members:")
        for name, bid, v in member_verified[:10]:
            print(f"    {name} ({bid}): {v}/{len(CONTACT_FIELDS)} fields verified")


def main():
    senate_dir = VERIFIED_DIR / "senate"
    house_dir = VERIFIED_DIR / "house"

    if senate_dir.exists():
        print_report("senate", senate_dir)
    if house_dir.exists() and any(house_dir.glob("*.json")):
        print_report("house", house_dir)

    # Manifest summary
    manifest_path = VERIFIED_DIR / "_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        print(f"\n{'='*60}")
        print(f"  MANIFEST")
        print(f"{'='*60}")
        print(f"  Created: {manifest.get('created', 'unknown')}")
        print(f"  Last updated: {manifest.get('last_updated', 'unknown')}")
        for chamber, info in manifest.get("chambers", {}).items():
            print(f"  {chamber}: {info['total']} members, "
                  f"{info['verified_count']} fully verified")


if __name__ == "__main__":
    main()
