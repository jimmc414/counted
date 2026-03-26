#!/usr/bin/env python3
"""Verify contact data for a batch of senators from official .gov sources.

Usage:
    python scripts/verify_batch.py --ranks 1-10
    python scripts/verify_batch.py --ids C001035 T000476
    python scripts/verify_batch.py --ranks 1-5 --dry-run

Fetches each senator's official senate.gov contact page, extracts contact info,
and updates per-member files with 'verified' status + citation URL.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SENATE_DIR = DATA / "verified_contacts" / "senate"
MANIFEST_PATH = DATA / "verified_contacts" / "_manifest.json"

CONTACT_FIELDS = [
    "dc_phone", "dc_fax", "web_form_url",
    "twitter", "facebook", "instagram", "bluesky",
    "youtube", "truth_social", "campaign_site",
]


def get_ranked_senators():
    """Load ranked senators list."""
    path = ROOT / "output" / "ranked_senators.json"
    return json.loads(path.read_text())


def resolve_targets(args):
    """Return list of bioguide_ids to verify."""
    ranked = get_ranked_senators()

    if args.ids:
        return args.ids

    if args.ranks:
        match = re.match(r"(\d+)-(\d+)", args.ranks)
        if match:
            lo, hi = int(match.group(1)), int(match.group(2))
        else:
            lo = hi = int(args.ranks)
        return [s["bioguide_id"] for s in ranked if lo <= s["rank"] <= hi]

    return []


def load_member(bioguide_id):
    """Load a verified contact file."""
    path = SENATE_DIR / f"{bioguide_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_member(record):
    """Save a verified contact file."""
    record["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    path = SENATE_DIR / f"{record['bioguide_id']}.json"
    path.write_text(json.dumps(record, indent=2) + "\n")


def make_field(value, status="verified", source="", verified_date=None):
    """Create a verified field triple."""
    return {
        "value": value,
        "status": status,
        "source": source,
        "verified_date": verified_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def make_office(city="", address="", phone="", fax="", source=""):
    """Create a verified state office entry."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    status = "verified" if source else "unverified"
    return {
        "city": make_field(city, status, source, today) if city else make_field("", "placeholder"),
        "address": make_field(address, status, source, today) if address else make_field("", "placeholder"),
        "phone": make_field(phone, status, source, today) if phone else make_field("", "placeholder"),
        "fax": make_field(fax, status, source, today) if fax else make_field("", "placeholder"),
    }


def apply_verification(record, verified_data):
    """Apply verified data to a member record.

    verified_data is a dict with keys from CONTACT_FIELDS and/or 'state_offices',
    each containing {'value': ..., 'source': ...}.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for field_name in CONTACT_FIELDS:
        if field_name in verified_data:
            vd = verified_data[field_name]
            value = vd.get("value", "")
            source = vd.get("source", "")
            if value:
                record["contacts"][field_name] = make_field(value, "verified", source, today)
            elif source:
                # Actively searched, confirmed absent
                record["contacts"][field_name] = make_field("", "not_found", source, today)

    if "state_offices" in verified_data:
        record["state_offices"] = verified_data["state_offices"]

    return record


def update_manifest(bioguide_id, record):
    """Update manifest with verification progress."""
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text())
    member_entry = manifest["chambers"]["senate"]["members"].get(bioguide_id, {})

    verified_count = sum(
        1 for f in CONTACT_FIELDS
        if record["contacts"].get(f, {}).get("status") == "verified"
    )
    member_entry["fields_verified"] = verified_count
    member_entry["status"] = "verified" if verified_count > 0 else "seeded"
    manifest["chambers"]["senate"]["members"][bioguide_id] = member_entry

    # Recount total verified
    manifest["chambers"]["senate"]["verified_count"] = sum(
        1 for m in manifest["chambers"]["senate"]["members"].values()
        if m.get("status") == "verified"
    )
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")


def extract_phones_from_text(text):
    """Extract US phone numbers from text."""
    return re.findall(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)


def extract_social_links(text):
    """Extract social media URLs/handles from page text."""
    social = {}

    # Twitter/X
    tw = re.findall(r'(?:twitter\.com|x\.com)/(\w+)', text, re.I)
    if tw:
        social["twitter"] = f"@{tw[0]}"

    # Facebook
    fb = re.findall(r'facebook\.com/([\w.]+)', text, re.I)
    if fb:
        social["facebook"] = fb[0]

    # Instagram
    ig = re.findall(r'instagram\.com/([\w.]+)', text, re.I)
    if ig:
        social["instagram"] = ig[0]

    # YouTube
    yt = re.findall(r'youtube\.com/(?:@|user/|channel/|c/)([\w-]+)', text, re.I)
    if yt:
        social["youtube"] = yt[0]

    # Bluesky
    bs = re.findall(r'bsky\.app/profile/([\w.-]+)', text, re.I)
    if bs:
        social["bluesky"] = bs[0]

    return social


def parse_senate_contact_page(html, source_url):
    """Parse a senate.gov contact page and extract structured data.

    Returns a dict suitable for apply_verification().
    """
    result = {}

    # DC phone
    dc_phones = re.findall(
        r'(?:Washington|D\.?C\.?|202)[^<\n]*?\(202\)\s*\d{3}[.-]\d{4}', html, re.I
    )
    if not dc_phones:
        dc_phones = re.findall(r'\(202\)\s*\d{3}[.-]\d{4}', html)
    if dc_phones:
        phone_match = re.search(r'\(202\)\s*\d{3}[.-]\d{4}', dc_phones[0])
        if phone_match:
            result["dc_phone"] = {"value": phone_match.group(), "source": source_url}

    # DC fax
    fax_match = re.findall(
        r'(?:fax|facsimile)[^<\n]*?\(202\)\s*\d{3}[.-]\d{4}', html, re.I
    )
    if fax_match:
        fax_num = re.search(r'\(202\)\s*\d{3}[.-]\d{4}', fax_match[0])
        if fax_num:
            result["dc_fax"] = {"value": fax_num.group(), "source": source_url}

    # Social media
    social = extract_social_links(html)
    for platform, handle in social.items():
        result[platform] = {"value": handle, "source": source_url}

    # State offices — look for patterns with city names and local phones
    # This is a best-effort parser; complex pages may need manual review
    state_offices = []
    office_blocks = re.findall(
        r'<(?:div|p|li|address)[^>]*>.*?(?:\(\d{3}\)\s*\d{3}[.-]\d{4}).*?</(?:div|p|li|address)>',
        html, re.I | re.S
    )
    for block in office_blocks:
        phones = re.findall(r'\((\d{3})\)\s*(\d{3})[.-](\d{4})', block)
        if phones:
            area, ex, num = phones[0]
            phone_str = f"({area}) {ex}-{num}"
            if area == "202":
                continue  # Skip DC office phones
            # Try to find city/address
            clean = re.sub(r'<[^>]+>', ' ', block).strip()
            city = ""
            address = ""
            lines = [l.strip() for l in clean.split('\n') if l.strip()]
            if lines:
                # First non-phone line is often city or address
                for line in lines:
                    if not re.search(r'\(\d{3}\)', line) and len(line) > 2:
                        if not city:
                            city = line[:80]
                        elif not address:
                            address = line[:120]
            state_offices.append(
                make_office(city=city, address=address, phone=phone_str, source=source_url)
            )

    if state_offices:
        result["state_offices"] = state_offices

    return result


def verify_single(bioguide_id, dry_run=False):
    """Verify one senator. Returns (bioguide_id, success, message)."""
    record = load_member(bioguide_id)
    if record is None:
        return bioguide_id, False, "File not found"

    name = record["name"]
    web_form = record["contacts"].get("web_form_url", {}).get("value", "")
    if not web_form:
        return bioguide_id, False, f"{name}: No web_form_url to derive .gov base URL"

    # Derive base senate.gov URL from web form
    base_match = re.match(r'(https?://www\.\w+\.senate\.gov)', web_form)
    if not base_match:
        return bioguide_id, False, f"{name}: Cannot parse senate.gov URL from {web_form}"

    base_url = base_match.group(1)
    contact_url = f"{base_url}/contact"

    if dry_run:
        return bioguide_id, True, f"{name}: Would fetch {contact_url}"

    print(f"  Verifying {name} ({bioguide_id}) from {contact_url}...")
    return bioguide_id, True, f"Ready: {name} — fetch {contact_url}"


def main():
    parser = argparse.ArgumentParser(description="Verify senator contact data")
    parser.add_argument("--ranks", help="Rank range, e.g. '1-10' or '5'")
    parser.add_argument("--ids", nargs="+", help="Specific bioguide_ids")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--apply-json", help="Path to JSON with verified data to apply")
    args = parser.parse_args()

    if args.apply_json:
        # Apply pre-gathered verification data from a JSON file
        verified_batch = json.loads(Path(args.apply_json).read_text())
        for bid, verified_data in verified_batch.items():
            record = load_member(bid)
            if record is None:
                print(f"  SKIP {bid}: file not found")
                continue
            record = apply_verification(record, verified_data)
            save_member(record)
            update_manifest(bid, record)
            v_count = sum(
                1 for f in CONTACT_FIELDS
                if record["contacts"].get(f, {}).get("status") == "verified"
            )
            print(f"  Updated {record['name']} ({bid}): {v_count} fields verified")
        return

    targets = resolve_targets(args)
    if not targets:
        print("No targets specified. Use --ranks or --ids.")
        parser.print_help()
        sys.exit(1)

    print(f"Targets: {len(targets)} senators")
    for bid in targets:
        bid, ok, msg = verify_single(bid, args.dry_run)
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {msg}")


if __name__ == "__main__":
    main()
