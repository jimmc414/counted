"""Assemble contact cards from loaded data."""

from counted.models import ContactCard


def build_contact_card(bioguide_id, contacts_data):
    """Build a ContactCard for a senator. Returns empty card if not found."""
    return contacts_data.get(bioguide_id, ContactCard())
