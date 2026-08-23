"""
Deterministic, explainable scoring engine.

Architectural decision (per the design brief): keep the AI-exposure prediction
itself as transparent, rule-based logic — NOT a black-box model — because
enterprise trust depends on every conclusion being traceable to a reason.
An optional LLM (see llm.py) is only used downstream for narrative text
generation, never for the automation/augmentation numbers themselves.

Each activity attribute contributes weighted points toward an
automation score and an augmentation score. Every point contributes a
human-readable reason code, which is how the system "explains how it
derived its conclusions" (a core requirement of the brief).
"""

from dataclasses import dataclass, field
from typing import List, Dict

# Weight each attribute contributes to automation vs augmentation (0-100 scale components)
AUTOMATION_WEIGHTS = {
    "structured": 25,
    "repetitive": 30,
    "rule_based": 30,
}
AUTOMATION_PENALTIES = {
    "requires_judgment": -20,
    "requires_creativity": -25,
    "interpersonal": -30,
}

AUGMENTATION_WEIGHTS = {
    "requires_judgment": 35,
    "structured": 15,
    "rule_based": 10,
}
AUGMENTATION_PENALTIES = {
    "interpersonal": -10,
}

REASON_TEXT = {
    "structured": "operates on structured, well-defined data",
    "repetitive": "is high-frequency and repetitive",
    "rule_based": "follows explicit, codifiable rules",
    "requires_judgment": "requires contextual human judgment",
    "requires_creativity": "requires original/creative thinking",
    "interpersonal": "depends on human relationships and trust",
}


@dataclass
class ActivityScore:
    name: str
    weight: float
    automation_score: float
    augmentation_score: float
    classification: str
    reason: str


@dataclass
class RoleScore:
    automation_pct: float
    augmentation_pct: float
    unaffected_pct: float
    confidence: str
    reason_codes: List[str] = field(default_factory=list)
    activity_scores: List[ActivityScore] = field(default_factory=list)


def score_activity(attrs: Dict) -> ActivityScore:
    auto_score = 10  # baseline
    aug_score = 10
    reasons_pos = []
    reasons_neg = []

    for key, pts in AUTOMATION_WEIGHTS.items():
        if attrs.get(key):
            auto_score += pts
            reasons_pos.append(REASON_TEXT[key])
    for key, pts in AUTOMATION_PENALTIES.items():
        if attrs.get(key):
            auto_score += pts  # negative
            reasons_neg.append(REASON_TEXT[key])

    for key, pts in AUGMENTATION_WEIGHTS.items():
        if attrs.get(key):
            aug_score += pts
    for key, pts in AUGMENTATION_PENALTIES.items():
        if attrs.get(key):
            aug_score += pts

    auto_score = max(0, min(100, auto_score))
    aug_score = max(0, min(100, aug_score))

    # Classification: whichever dimension dominates, with a human-led floor
    if auto_score >= 65:
        classification = "automated"
    elif aug_score >= 45 or attrs.get("requires_judgment"):
        classification = "augmented"
    else:
        classification = "human-led"

    reason_parts = []
    if reasons_pos:
        reason_parts.append(
            f"'{attrs['name']}' is {', and '.join(reasons_pos)} -> {auto_score}% automation potential."
        )
    else:
        reason_parts.append(f"'{attrs['name']}' has low automation potential ({auto_score}%).")
    if reasons_neg:
        reason_parts.append(
            f"However, it {', and '.join(reasons_neg)}, which caps full automation and favours augmentation instead."
        )

    return ActivityScore(
        name=attrs["name"],
        weight=attrs.get("weight", 0),
        automation_score=auto_score,
        augmentation_score=aug_score,
        classification=classification,
        reason=" ".join(reason_parts),
    )


def score_role(activities: List[Dict]) -> RoleScore:
    total_weight = sum(a.get("weight", 0) for a in activities) or 100
    weighted_auto = 0.0
    weighted_aug = 0.0
    activity_scores = []
    reason_codes = []

    for a in activities:
        a_with_name = {**a, "name": a.get("activity", a.get("name", "Activity"))}
        s = score_activity(a_with_name)
        activity_scores.append(s)
        w = a.get("weight", 0) / total_weight
        weighted_auto += s.automation_score * w
        weighted_aug += s.augmentation_score * w
        reason_codes.append(s.reason)

    # Normalise: augmentation only counts for the portion NOT already automated
    weighted_auto = round(weighted_auto, 1)
    weighted_aug = round(min(weighted_aug, 100 - weighted_auto), 1)
    unaffected = round(max(0.0, 100 - weighted_auto - weighted_aug), 1)

    # Confidence heuristic: more activities + clearer split (less "50/50 ambiguous") = higher confidence
    spread = abs(weighted_auto - weighted_aug)
    if len(activities) >= 4 and spread >= 20:
        confidence = "high"
    elif len(activities) >= 3 and spread >= 8:
        confidence = "medium"
    else:
        confidence = "low"

    return RoleScore(
        automation_pct=weighted_auto,
        augmentation_pct=weighted_aug,
        unaffected_pct=unaffected,
        confidence=confidence,
        reason_codes=reason_codes,
        activity_scores=activity_scores,
    )


def build_future_role_profile(role_title: str, role_score: RoleScore,
                               new_responsibilities: List[str], future_skills: List[str]) -> str:
    """Deterministic, template-based narrative (no LLM required)."""
    top_automated = sorted(
        [a for a in role_score.activity_scores if a.classification == "automated"],
        key=lambda a: a.weight, reverse=True
    )
    top_augmented = sorted(
        [a for a in role_score.activity_scores if a.classification == "augmented"],
        key=lambda a: a.weight, reverse=True
    )

    parts = [f"The {role_title} role is projected to shift from execution-heavy work toward "
             f"oversight and judgment-driven work."]

    if top_automated:
        names = ", ".join(a.name for a in top_automated[:2])
        parts.append(f"~{role_score.automation_pct}% of time (led by {names}) is likely to be automated.")
    if top_augmented:
        names = ", ".join(a.name for a in top_augmented[:2])
        parts.append(f"~{role_score.augmentation_pct}% of time (e.g. {names}) will be AI-augmented rather than replaced.")
    if new_responsibilities:
        parts.append(f"New responsibilities are expected to include: {', '.join(new_responsibilities)}.")
    if future_skills:
        parts.append(f"Future-critical skills: {', '.join(future_skills)}.")

    return " ".join(parts)
