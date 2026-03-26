"""Domain models for the Counted scoring system."""

from dataclasses import dataclass, field


@dataclass
class Senator:
    bioguide_id: str
    name: str
    party: str
    state: str
    senate_class: int
    up_2026: bool


@dataclass
class MetricScores:
    m1: float = 0.0
    m2: float = 0.0
    m3: float = 0.0
    m4: float = 0.0
    m5: float = 0.0
    m6: float = 1.0
    m7: float = 0.0
    m8: float = 0.0
    m9: float = 0.0
    m10: float = 1.0
    persuadability: float = 0.0
    leverage: float = 0.0
    expected_impact: float = 0.0


@dataclass
class ContactCard:
    dc_phone: str = ""
    dc_fax: str = ""
    state_offices: list = field(default_factory=list)
    web_form_url: str = ""
    twitter: str = ""
    facebook: str = ""
    instagram: str = ""
    bluesky: str = ""
    youtube: str = ""
    truth_social: str = ""
    campaign_site: str = ""


@dataclass
class ScoredSenator:
    senator: Senator
    scores: MetricScores
    contact: ContactCard
    rank: int = 0
    key_factor: str = ""
