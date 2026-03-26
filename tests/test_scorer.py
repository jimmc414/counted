"""Calibration tests for the Counted scoring algorithm."""

import pytest
from counted.scorer import rank_senators
from counted.data_loader import load_senators, load_metric_data, load_contacts


@pytest.fixture(scope="module")
def ranked():
    senators = load_senators()
    metric_data = load_metric_data()
    contacts_data = load_contacts()
    return rank_senators(senators, metric_data, contacts_data)


def find(ranked, name):
    for s in ranked:
        if name.lower() in s.senator.name.lower():
            return s
    raise ValueError(f"{name} not found in ranked list")


def test_collins_top_3(ranked):
    """Collins (R-ME) must be in top 3: Approps Chair, blue state, up 2026."""
    collins = find(ranked, "Collins")
    assert collins.rank <= 3, (
        f"Collins ranked #{collins.rank} (score={collins.scores.expected_impact:.4f}), "
        f"expected top 3"
    )


def test_cotton_deprioritized(ranked):
    """Cotton (R-AR) deprioritized: immovable hawk despite committee power."""
    cotton = find(ranked, "Cotton")
    collins = find(ranked, "Collins")
    assert cotton.rank > 20, (
        f"Cotton ranked #{cotton.rank}, expected outside top 20"
    )
    assert cotton.scores.expected_impact < collins.scores.expected_impact * 0.25, (
        f"Cotton ({cotton.scores.expected_impact:.4f}) should be <25% of "
        f"Collins ({collins.scores.expected_impact:.4f})"
    )


def test_paul_moderate(ranked):
    """Paul (R-KY) scores moderate: already moved, limited marginal value."""
    paul = find(ranked, "Paul")
    total = len(ranked)
    assert paul.rank > 5, (
        f"Paul ranked #{paul.rank}, expected not in top 5"
    )
    assert paul.rank < total - 30, (
        f"Paul ranked #{paul.rank}/{total}, expected not in bottom 30"
    )


def test_no_safe_d_outscores_vulnerable_r(ranked):
    """No safe-seat Democrat should outscore any genuinely vulnerable Republican.

    Excludes Rs with right-wing primary threats (M6 < 0.9) since those are
    intentionally deprioritized — antiwar pressure is counterproductive for them.
    """
    from counted.data_loader import load_metric_data
    from counted.scorer import parse_pvi
    pvi = load_metric_data()["pvi"]

    safe_d_scores = []
    for s in ranked:
        if s.senator.party not in ("D", "I"):
            continue
        if s.senator.up_2026:
            continue
        state_pvi = parse_pvi(pvi.get(s.senator.state, "EVEN"))
        if state_pvi >= 5:
            safe_d_scores.append(s.scores.expected_impact)

    vulnerable_r_scores = []
    for s in ranked:
        if s.senator.party != "R" or not s.senator.up_2026:
            continue
        if s.scores.m5 >= 0.5 and s.scores.m6 >= 0.9:
            vulnerable_r_scores.append(s.scores.expected_impact)

    if safe_d_scores and vulnerable_r_scores:
        max_safe_d = max(safe_d_scores)
        min_vuln_r = min(vulnerable_r_scores)
        assert max_safe_d < min_vuln_r, (
            f"Safe D max score ({max_safe_d:.4f}) >= "
            f"vulnerable R min score ({min_vuln_r:.4f})"
        )


def test_primary_direction_penalizes(ranked):
    """Right-wing primary threats should reduce score vs general threats."""
    collins = find(ranked, "Collins")
    dampened = [s for s in ranked
                if s.scores.m6 < 1.0
                and s.senator.up_2026
                and s.senator.party == "R"]
    if dampened:
        best_dampened = min(s.rank for s in dampened)
        assert collins.rank < best_dampened, (
            f"Collins (M6={collins.scores.m6}, rank={collins.rank}) "
            f"should rank above best primary-dampened R "
            f"(rank={best_dampened})"
        )


def test_top_5_all_r_2026(ranked):
    """Top 5 should all be Republicans facing 2026 elections."""
    for s in ranked[:5]:
        assert s.senator.party == "R", (
            f"#{s.rank} {s.senator.name} is {s.senator.party}, expected R"
        )
        assert s.senator.up_2026, (
            f"#{s.rank} {s.senator.name} not up in 2026"
        )
