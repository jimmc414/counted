#!/usr/bin/env python3
"""Build House roster and create 435 placeholder verified contact files.

Fetches the current House membership from the official clerk.house.gov XML
or falls back to a structured web source (house.gov/representatives).
Creates data/house_members.json and placeholder files in
data/verified_contacts/house/.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
HOUSE_DIR = DATA / "verified_contacts" / "house"
MANIFEST_PATH = DATA / "verified_contacts" / "_manifest.json"
HOUSE_MEMBERS_PATH = DATA / "house_members.json"

CONTACT_FIELDS = [
    "dc_phone", "dc_fax", "web_form_url",
    "twitter", "facebook", "instagram", "bluesky",
    "youtube", "truth_social", "campaign_site",
]


def make_field(value="", status="placeholder"):
    """Create a placeholder field triple."""
    return {
        "value": value,
        "status": status,
        "source": "",
        "verified_date": "",
    }


def make_office():
    """Create a placeholder state office entry."""
    return {
        "city": make_field(),
        "address": make_field(),
        "phone": make_field(),
        "fax": make_field(),
    }


def build_placeholder_contact(member):
    """Build a placeholder verified contact record for a House member."""
    return {
        "bioguide_id": member["bioguide_id"],
        "name": member["name"],
        "party": member["party"],
        "state": member["state"],
        "district": member.get("district", ""),
        "chamber": "house",
        "contacts": {f: make_field() for f in CONTACT_FIELDS},
        "state_offices": [make_office()],
        "metadata": {
            "created": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "verification_notes": "",
        },
    }


def parse_clerk_xml(xml_text):
    """Parse clerk.house.gov memberData XML format."""
    members = []
    root = ET.fromstring(xml_text)

    for member_el in root.iter("member"):
        info = member_el.find("member-info")
        if info is None:
            continue

        bioguide = info.findtext("bioguideID", "").strip()
        if not bioguide:
            continue

        first = info.findtext("firstname", "").strip()
        last = info.findtext("lastname", "").strip()
        middle = info.findtext("middlename", "").strip()
        suffix = info.findtext("suffix", "").strip()
        party = info.findtext("party", "").strip()
        state = info.findtext("state", "").strip()

        # State postal code from statedistrict
        state_district = member_el.findtext("statedistrict", "").strip()
        district = ""
        if state_district and len(state_district) >= 4:
            state = state_district[:2]
            district = state_district[2:]

        name_parts = [first]
        if middle:
            name_parts.append(middle)
        name_parts.append(last)
        if suffix:
            name_parts.append(suffix)
        name = " ".join(name_parts)

        # Normalize party
        party_map = {"R": "R", "D": "D", "I": "I", "Republican": "R",
                     "Democrat": "D", "Independent": "I"}
        party = party_map.get(party, party)

        phone = info.findtext("phone", "").strip()

        members.append({
            "bioguide_id": bioguide,
            "name": name,
            "party": party,
            "state": state,
            "district": district.lstrip("0") or "At-Large",
            "dc_phone": phone,
        })

    return members


def parse_html_roster(html):
    """Fallback: parse house.gov/representatives HTML table."""
    members = []

    # Look for table rows with member data
    rows = re.findall(
        r'<tr[^>]*>.*?</tr>', html, re.S
    )

    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        if len(cells) < 3:
            continue

        # Try to extract name and link
        name_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', cells[0], re.S)
        if not name_match:
            continue

        name = re.sub(r'<[^>]+>', '', name_match.group(2)).strip()
        link = name_match.group(1)

        # Extract bioguide from link if possible
        bio_match = re.search(r'/([A-Z]\d{6})/', link)
        bioguide = bio_match.group(1) if bio_match else ""

        # District and party from other cells
        district = re.sub(r'<[^>]+>', '', cells[1]).strip() if len(cells) > 1 else ""
        party_raw = re.sub(r'<[^>]+>', '', cells[2]).strip() if len(cells) > 2 else ""

        party_map = {"Republican": "R", "Democrat": "D", "Independent": "I",
                     "R": "R", "D": "D", "I": "I"}
        party = party_map.get(party_raw, party_raw[:1] if party_raw else "")

        if name and bioguide:
            members.append({
                "bioguide_id": bioguide,
                "name": name,
                "party": party,
                "state": "",
                "district": district,
                "dc_phone": "",
            })

    return members


def fetch_roster():
    """Attempt to fetch House roster from official sources.

    Returns list of member dicts. Falls back gracefully.
    """
    # Try clerk.house.gov XML first
    try:
        import urllib.request
        url = "https://clerk.house.gov/xml/lists/MemberData.xml"
        print(f"Fetching {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_text = resp.read().decode("utf-8")
        members = parse_clerk_xml(xml_text)
        if members:
            print(f"  Parsed {len(members)} members from clerk.house.gov XML")
            return members, url
    except Exception as e:
        print(f"  clerk.house.gov XML failed: {e}")

    # Fallback: try house.gov representatives page
    try:
        url = "https://www.house.gov/representatives"
        print(f"Fetching {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
        members = parse_html_roster(html)
        if members:
            print(f"  Parsed {len(members)} members from house.gov HTML")
            return members, url
    except Exception as e:
        print(f"  house.gov HTML failed: {e}")

    return [], ""


def main():
    members, source_url = fetch_roster()

    if not members:
        print("ERROR: Could not fetch House roster from any source.")
        print("You can manually provide a roster file and re-run.")
        sys.exit(1)

    # Filter to only House members (some XML sources include delegates)
    # Keep all for now — delegates from territories are relevant for contact purposes

    # Save roster
    HOUSE_MEMBERS_PATH.write_text(
        json.dumps(members, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Wrote {len(members)} members to {HOUSE_MEMBERS_PATH}")

    # Create placeholder files
    HOUSE_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    for member in members:
        bid = member["bioguide_id"]
        if not bid:
            continue
        record = build_placeholder_contact(member)
        # Carry over DC phone if we got it from the roster
        if member.get("dc_phone"):
            record["contacts"]["dc_phone"] = make_field(member["dc_phone"], "unverified")
        out_path = HOUSE_DIR / f"{bid}.json"
        out_path.write_text(json.dumps(record, indent=2) + "\n")
        created += 1

    print(f"Created {created} placeholder files in {HOUSE_DIR}")

    # Update manifest
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
    else:
        manifest = {
            "created": datetime.now(timezone.utc).isoformat(),
            "chambers": {},
        }

    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    manifest["chambers"]["house"] = {
        "total": created,
        "verified_count": 0,
        "source": source_url,
        "members": {},
    }

    for member in members:
        bid = member["bioguide_id"]
        if not bid:
            continue
        manifest["chambers"]["house"]["members"][bid] = {
            "name": member["name"],
            "file": f"house/{bid}.json",
            "fields_with_data": 1 if member.get("dc_phone") else 0,
            "fields_verified": 0,
            "status": "placeholder",
        }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Manifest updated with {created} house members")

    # Stats
    parties = {}
    for m in members:
        p = m.get("party", "?")
        parties[p] = parties.get(p, 0) + 1
    print(f"Party breakdown: {dict(sorted(parties.items()))}")


if __name__ == "__main__":
    main()
