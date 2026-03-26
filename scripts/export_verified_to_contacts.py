#!/usr/bin/env python3
"""Export verified per-member files back to flat data/contacts.json format.

This ensures backward compatibility with the existing pipeline:
  python -m counted -> build_frontend_data.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SENATE_DIR = DATA / "verified_contacts" / "senate"
CONTACTS_PATH = DATA / "contacts.json"

CONTACT_FIELDS = [
    "dc_phone", "dc_fax", "web_form_url",
    "twitter", "facebook", "instagram",
    "youtube", "campaign_site",
]

# Fields that exist in ranked_senators.json contact block but not in contacts.json
EXTRA_FIELDS = ["bluesky", "truth_social"]


def extract_value(triple):
    """Get the plain value from a verified triple."""
    if isinstance(triple, dict) and "value" in triple:
        return triple["value"]
    return triple


def export_member(record):
    """Convert a verified contact record back to flat contacts.json format."""
    flat = {"bioguide_id": record["bioguide_id"]}

    for field_name in CONTACT_FIELDS:
        triple = record.get("contacts", {}).get(field_name, {})
        value = extract_value(triple)
        status = triple.get("status", "placeholder") if isinstance(triple, dict) else "placeholder"
        # Include field if it has data OR was carried from original (unverified/verified)
        if value or status in ("unverified", "verified", "not_found"):
            flat[field_name] = value

    # State offices — flatten back to [{city, phone}]
    offices = []
    for office in record.get("state_offices", []):
        city = extract_value(office.get("city", {}))
        phone = extract_value(office.get("phone", {}))
        if city or phone:
            entry = {}
            if city:
                entry["city"] = city
            if phone:
                entry["phone"] = phone
            # Include address if present (new field, enriches existing format)
            address = extract_value(office.get("address", {}))
            if address:
                entry["address"] = address
            offices.append(entry)

    if offices:
        flat["state_offices"] = offices

    return flat


def main():
    # Read all senate files
    files = sorted(SENATE_DIR.glob("*.json"))
    if not files:
        print("No senate files found. Run init_verified_contacts.py first.")
        return

    # Also load existing contacts.json to preserve ordering
    existing = json.loads(CONTACTS_PATH.read_text())
    existing_order = [c["bioguide_id"] for c in existing]
    existing_ids = set(existing_order)

    exported = []
    by_id = {}

    for f in files:
        record = json.loads(f.read_text())
        flat = export_member(record)
        by_id[flat["bioguide_id"]] = flat

    # Maintain original ordering, append any new members at end
    for bid in existing_order:
        if bid in by_id:
            exported.append(by_id.pop(bid))
    # Append remaining (shouldn't happen for senate, but future-proof)
    for bid in sorted(by_id.keys()):
        exported.append(by_id[bid])

    # Write output
    output = json.dumps(exported, indent=2, ensure_ascii=False) + "\n"
    CONTACTS_PATH.write_text(output)
    print(f"Exported {len(exported)} contacts to {CONTACTS_PATH}")

    # Diff check: compare field counts
    for old, new in zip(existing, exported):
        if old["bioguide_id"] != new["bioguide_id"]:
            continue
        old_fields = set(old.keys()) - {"bioguide_id"}
        new_fields = set(new.keys()) - {"bioguide_id"}
        lost = old_fields - new_fields
        if lost:
            print(f"  WARNING: {old['bioguide_id']} lost fields: {lost}")


if __name__ == "__main__":
    main()
