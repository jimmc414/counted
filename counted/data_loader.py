"""Load all JSON data from the data/ directory."""

import json
from pathlib import Path
from counted.models import Senator, ContactCard

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename, default=None):
    if default is None:
        default = {}
    path = DATA_DIR / filename
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def load_senators():
    raw = _load_json("senators.json", default=[])
    return [
        Senator(
            bioguide_id=s["bioguide_id"],
            name=s["name"],
            party=s["party"],
            state=s["state"],
            senate_class=s["senate_class"],
            up_2026=s.get("up_2026", s["senate_class"] == 2),
        )
        for s in raw
    ]


def load_metric_data():
    committees_raw = _load_json("committees.json")

    leadership = {}
    committees = {}
    for bid, assignments in committees_raw.items():
        regular = []
        for a in assignments:
            if a.get("committee") == "Senate Leadership":
                leadership[bid] = a.get("role", "")
            else:
                regular.append(a)
        committees[bid] = regular

    return {
        "pvi": _load_json("pvi.json"),
        "margins": _load_json("margins.json"),
        "independence": _load_json("independence.json"),
        "ambivalence": _load_json("ambivalence.json"),
        "signal_value": _load_json("signal_value.json"),
        "primary_direction": _load_json("primary_direction.json"),
        "committees": committees,
        "leadership": leadership,
        "electorate": _load_json("electorate.json"),
    }


def load_contacts():
    raw = _load_json("contacts.json", default=[])
    contacts = {}
    for entry in raw:
        bid = entry.get("bioguide_id", "")
        if not bid:
            continue
        contacts[bid] = ContactCard(
            dc_phone=entry.get("dc_phone", ""),
            dc_fax=entry.get("dc_fax", ""),
            state_offices=entry.get("state_offices", []),
            web_form_url=entry.get("web_form_url", ""),
            twitter=entry.get("twitter", ""),
            facebook=entry.get("facebook", ""),
            instagram=entry.get("instagram", ""),
            bluesky=entry.get("bluesky", ""),
            youtube=entry.get("youtube", ""),
            truth_social=entry.get("truth_social", ""),
            campaign_site=entry.get("campaign_site", ""),
        )
    return contacts
