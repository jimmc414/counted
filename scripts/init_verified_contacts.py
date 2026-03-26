#!/usr/bin/env python3
"""Seed verified contact files from existing senators.json + contacts.json.

Creates one JSON file per senator in data/verified_contacts/senate/,
with every data point wrapped in a {value, status, source, verified_date} triple.
All fields start as 'unverified' (carrying existing data) or 'placeholder' (no data).
Also writes data/verified_contacts/_manifest.json to track progress.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SENATE_DIR = DATA / "verified_contacts" / "senate"
MANIFEST_PATH = DATA / "verified_contacts" / "_manifest.json"

# All contact channels tracked per member
CONTACT_FIELDS = [
    "dc_phone", "dc_fax", "web_form_url",
    "twitter", "facebook", "instagram", "bluesky",
    "youtube", "truth_social", "campaign_site",
]


def make_field(value, status=None):
    """Wrap a value in a verified-contact triple."""
    if status is None:
        status = "unverified" if value else "placeholder"
    return {
        "value": value,
        "status": status,
        "source": "",
        "verified_date": "",
    }


def make_office(office_dict):
    """Wrap a state office entry — each sub-field gets its own triple."""
    return {
        "city": make_field(office_dict.get("city", "")),
        "address": make_field(""),  # not in existing data
        "phone": make_field(office_dict.get("phone", "")),
        "fax": make_field(""),      # not in existing data
    }


def build_verified_contact(senator, contact):
    """Build a full verified contact record for one senator."""
    record = {
        "bioguide_id": senator["bioguide_id"],
        "name": senator["name"],
        "party": senator["party"],
        "state": senator["state"],
        "senate_class": senator["senate_class"],
        "up_2026": senator["up_2026"],
        "chamber": "senate",
        "contacts": {},
        "state_offices": [],
        "metadata": {
            "created": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "verification_notes": "",
        },
    }

    # Wrap each scalar contact field
    for field_name in CONTACT_FIELDS:
        value = contact.get(field_name, "")
        # If field key existed in source data (even empty), mark unverified not placeholder
        key_present = field_name in contact
        if key_present:
            record["contacts"][field_name] = make_field(value, "unverified")
        else:
            record["contacts"][field_name] = make_field(value)

    # Wrap state offices
    for office in contact.get("state_offices", []):
        record["state_offices"].append(make_office(office))

    # If no state offices exist, add one placeholder
    if not record["state_offices"]:
        record["state_offices"].append(make_office({}))

    return record


def main():
    senators = json.loads((DATA / "senators.json").read_text())
    contacts_list = json.loads((DATA / "contacts.json").read_text())
    contacts_by_id = {c["bioguide_id"]: c for c in contacts_list}

    SENATE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "chambers": {
            "senate": {"total": 0, "verified_count": 0, "members": {}},
            "house": {"total": 0, "verified_count": 0, "members": {}},
        },
    }

    for senator in senators:
        bid = senator["bioguide_id"]
        contact = contacts_by_id.get(bid, {})
        record = build_verified_contact(senator, contact)

        out_path = SENATE_DIR / f"{bid}.json"
        out_path.write_text(json.dumps(record, indent=2) + "\n")

        # Count how many fields have actual data (unverified vs placeholder)
        fields_with_data = sum(
            1 for f in CONTACT_FIELDS
            if record["contacts"][f]["status"] == "unverified"
        )

        manifest["chambers"]["senate"]["members"][bid] = {
            "name": senator["name"],
            "file": f"senate/{bid}.json",
            "fields_with_data": fields_with_data,
            "fields_verified": 0,
            "status": "seeded",
        }

    manifest["chambers"]["senate"]["total"] = len(senators)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Created {len(senators)} senate files in {SENATE_DIR}")
    print(f"Manifest written to {MANIFEST_PATH}")

    # Quick stats
    total_fields = len(senators) * len(CONTACT_FIELDS)
    filled = sum(
        m["fields_with_data"]
        for m in manifest["chambers"]["senate"]["members"].values()
    )
    print(f"Field coverage: {filled}/{total_fields} "
          f"({filled/total_fields*100:.1f}%) have data (all unverified)")


if __name__ == "__main__":
    main()
