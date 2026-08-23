from backend.scoring import score_activity, score_role


def test_highly_automatable_activity_scores_high():
    attrs = {"name": "Invoice matching", "structured": True, "repetitive": True, "rule_based": True}
    s = score_activity(attrs)
    assert s.classification == "automated"
    assert s.automation_score >= 65


def test_interpersonal_activity_is_not_automated():
    attrs = {"name": "Client negotiation", "interpersonal": True, "requires_judgment": True}
    s = score_activity(attrs)
    assert s.classification != "automated"


def test_role_percentages_sum_to_100():
    activities = [
        {"activity": "A", "structured": True, "repetitive": True, "rule_based": True, "weight": 40},
        {"activity": "B", "interpersonal": True, "requires_judgment": True, "weight": 60},
    ]
    r = score_role(activities)
    total = r.automation_pct + r.augmentation_pct + r.unaffected_pct
    assert 99.0 <= total <= 100.5


def test_every_activity_gets_a_reason():
    activities = [{"activity": "A", "structured": True, "weight": 100}]
    r = score_role(activities)
    assert len(r.reason_codes) == 1
    assert "A" in r.reason_codes[0]
