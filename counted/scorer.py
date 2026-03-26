"""Core scoring engine: compute M1-M10 and rank senators."""

from counted.models import MetricScores, ScoredSenator
from counted.data_loader import load_senators, load_metric_data, load_contacts
from counted.contacts import build_contact_card
from counted.output import print_terminal, write_json, write_csv

# Persuadability weights (Option B: M6 as multiplier, renormalized to 1.0)
W_M1 = 0.25
W_M2 = 0.25
W_M3 = 0.25
W_M4 = 0.12
W_M5 = 0.13

# Leverage weights
W_M7 = 0.40
W_M8 = 0.20
W_M9 = 0.40


def parse_pvi(pvi_str):
    """Convert PVI string ('D+5', 'R+12', 'EVEN') to float. Positive = Dem."""
    pvi_str = pvi_str.strip().upper()
    if pvi_str in ("EVEN", "0", ""):
        return 0.0
    parts = pvi_str.split("+")
    if len(parts) != 2:
        return 0.0
    direction, value = parts[0], float(parts[1])
    return value if direction == "D" else -value


def score_m1(senator):
    if senator.senate_class == 2:
        return 1.0
    if senator.senate_class == 3:
        return 0.3
    return 0.1


def score_m2(state, pvi_data):
    pvi = parse_pvi(pvi_data.get(state, "EVEN"))
    if pvi >= 5:
        return 1.0
    if pvi >= 1:
        return 0.8
    if pvi >= 0:
        return 0.6
    if pvi >= -4:
        return 0.4
    if pvi >= -9:
        return 0.2
    return 0.05


def score_m3(bioguide_id, ambivalence_data, party):
    if bioguide_id in ambivalence_data:
        return ambivalence_data[bioguide_id]
    return 0.20 if party == "R" else 0.05


def score_m4(bioguide_id, independence_data):
    pct = independence_data.get(bioguide_id, 5.0)
    if pct >= 20:
        return 1.0
    if pct >= 10:
        return 0.7
    if pct >= 5:
        return 0.4
    return 0.15


def score_m5(bioguide_id, margin_data):
    margin = margin_data.get(bioguide_id, 15.0)
    if margin < 3:
        return 1.0
    if margin <= 6:
        return 0.75
    if margin <= 10:
        return 0.5
    if margin <= 20:
        return 0.25
    return 0.05


def score_m6(bioguide_id, primary_data):
    return primary_data.get(bioguide_id, 1.0)


def score_m7(bioguide_id, committee_data):
    assignments = committee_data.get(bioguide_id, [])
    if not assignments:
        return 0.15

    best = 0.15
    key = {"Appropriations", "Armed Services", "Foreign Relations"}
    secondary = {"Intelligence", "Budget"}

    for a in assignments:
        committee = a.get("committee", "")
        role = a.get("role", "Member")
        if committee in key:
            if role == "Chair":
                best = max(best, 1.0)
            elif role == "Ranking Member":
                best = max(best, 0.85)
            else:
                best = max(best, 0.7)
        elif committee in secondary:
            best = max(best, 0.4)

    return best


def score_m8(bioguide_id, committee_data, leadership=None):
    if leadership is None:
        leadership = {}

    best = 0.2
    role = leadership.get(bioguide_id, "")

    if role in ("Majority Leader", "Minority Leader",
                "Majority Whip", "Minority Whip"):
        return 1.0
    if "Conference Chair" in role or "Caucus Chair" in role:
        best = max(best, 0.6)

    for a in committee_data.get(bioguide_id, []):
        r = a.get("role", "Member")
        if r in ("Chair", "Ranking Member"):
            best = max(best, 0.7)
        elif "Subcommittee Chair" in r:
            relevant = {"Appropriations", "Armed Services",
                        "Foreign Relations", "Intelligence", "Budget"}
            if a.get("committee", "") in relevant:
                best = max(best, 0.5)

    return best


def score_m9(bioguide_id, signal_data):
    return signal_data.get(bioguide_id, 0.2)


def score_all(senator, metric_data):
    m1 = score_m1(senator)
    m2 = score_m2(senator.state, metric_data["pvi"])
    m3 = score_m3(senator.bioguide_id, metric_data["ambivalence"], senator.party)
    m4 = score_m4(senator.bioguide_id, metric_data["independence"])
    m5 = score_m5(senator.bioguide_id, metric_data["margins"])
    m6 = score_m6(senator.bioguide_id, metric_data["primary_direction"])
    m7 = score_m7(senator.bioguide_id, metric_data["committees"])
    m8 = score_m8(senator.bioguide_id, metric_data["committees"],
                   metric_data.get("leadership", {}))
    m9 = score_m9(senator.bioguide_id, metric_data["signal_value"])
    m10 = 1.0

    persuadability = (W_M1*m1 + W_M2*m2 + W_M3*m3 + W_M4*m4 + W_M5*m5) * m6
    leverage = W_M7*m7 + W_M8*m8 + W_M9*m9
    expected_impact = persuadability * leverage * m10

    return MetricScores(
        m1=m1, m2=m2, m3=m3, m4=m4, m5=m5, m6=m6,
        m7=m7, m8=m8, m9=m9, m10=m10,
        persuadability=round(persuadability, 4),
        leverage=round(leverage, 4),
        expected_impact=round(expected_impact, 4),
    )


def determine_key_factor(scores):
    p_contributions = {
        "Electoral proximity (up 2026)": W_M1 * scores.m1,
        "Blue-state electorate": W_M2 * scores.m2,
        "Demonstrated ambivalence on war": W_M3 * scores.m3,
        "History of independence": W_M4 * scores.m4,
        "Tight election margin": W_M5 * scores.m5,
    }
    l_contributions = {
        "Committee power": W_M7 * scores.m7,
        "Leadership role": W_M8 * scores.m8,
        "Signal/narrative value if shifted": W_M9 * scores.m9,
    }

    all_c = {}
    for k, v in p_contributions.items():
        all_c[k] = v * scores.m6 * scores.leverage
    for k, v in l_contributions.items():
        all_c[k] = v * scores.persuadability

    if scores.m6 != 1.0 and scores.m6 != 0:
        effect = abs(scores.persuadability - scores.persuadability / scores.m6)
        label = ("General election threat boosts impact" if scores.m6 > 1.0
                 else "Right-wing primary dampens impact")
        all_c[label] = effect * scores.leverage

    return max(all_c, key=all_c.get) if all_c else "Rank-and-file"


def rank_senators(senators, metric_data, contacts_data):
    scored = []
    for senator in senators:
        ms = score_all(senator, metric_data)
        contact = build_contact_card(senator.bioguide_id, contacts_data)
        kf = determine_key_factor(ms)
        scored.append(ScoredSenator(
            senator=senator, scores=ms, contact=contact, key_factor=kf,
        ))

    scored.sort(key=lambda s: s.scores.expected_impact, reverse=True)
    for i, s in enumerate(scored, 1):
        s.rank = i
    return scored


def main():
    senators = load_senators()
    metric_data = load_metric_data()
    contacts_data = load_contacts()
    ranked = rank_senators(senators, metric_data, contacts_data)
    print_terminal(ranked)
    write_json(ranked)
    write_csv(ranked)
