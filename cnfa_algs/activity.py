"""
cnfa_algs.activity — Activity prediction from physical attribute constellations.

Maps computed spatial/visual attributes to predicted human activities using
condition signatures from environmental psychology literature.

Scientific basis:
    Gehl 2011 "Life Between Buildings" — activity taxonomy
    Mehrabian & Russell 1974 — PAD arousal model
    Whyte 1980 "Social Life of Small Urban Spaces" — edge effect
    Appleton 1975 — prospect-refuge theory
    Hall 1966 — proxemic distance zones
    Alexander 1977 — pattern language intimacy gradient
    Kuttruff 2009 — acoustic absorption/speech privacy
    Kaplan 1995 — attention restoration theory
    Cajochen et al. 2005, 2011 — circadian lighting effects
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


# ═══════════════════════════════════════════════════════════════════════
#  ACTIVITY DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

# Condition signal values:  HIGH=0.8, MID=0.5, LOW=0.2, REJECT=0.0
HIGH, MID, LOW, REJECT = 0.8, 0.5, 0.2, 0.0
# Relevance: 1.0 = matters, 0.0 = doesn't matter for this activity
REL, SKIP = 1.0, 0.0

# Attribute order for profile vectors (must match pipeline output):
ATTR_NAMES = [
    "enclosure",          # cnfa.spatial.enclosure_index
    "prospect",           # cnfa.spatial.prospect
    "brightness",         # cnfa.light.brightness_variance
    "glare",              # cnfa.light.glare_risk
    "warmth",             # cnfa.light.warm_vs_cool_ratio
    "acoustics",          # cnfa.acoustics.absorption_proxy
    "saliency",           # cnfa.cognitive.landmark_salience
    "sociopetal",         # cnfa.social.sociopetal_seating
    "edge_clarity",       # cnfa.fluency.edge_clarity_mean (proxy for edge proximity)
]

N_ATTRS = len(ATTR_NAMES)


@dataclass
class Activity:
    """An activity with its environmental condition signature."""
    code: str                    # e.g. "A04"
    name: str                    # e.g. "Solitary focused work"
    tier: int                    # 0=passage, 1=solitary, 2=dyadic, 3=group, 4=special
    gehl_class: str              # "necessary", "optional", "social"
    profile: np.ndarray          # ideal attribute values (N_ATTRS,)
    relevance: np.ndarray        # which attributes matter (N_ATTRS,)
    group_size: Tuple[int, int]  # (min, max)
    duration_min: Tuple[int, int]  # typical (min, max) minutes
    citations: List[str] = field(default_factory=list)


def _act(code, name, tier, gehl, profile, relevance,
         group=(1, 1), dur=(1, 5), cites=None):
    return Activity(
        code=code, name=name, tier=tier, gehl_class=gehl,
        profile=np.array(profile, dtype=np.float64),
        relevance=np.array(relevance, dtype=np.float64),
        group_size=group, duration_min=dur,
        citations=cites or [])


#                                            enc   pros  brt   glr   wrm   aco   sal   soc   edge
#                                            rel   rel   rel   rel   rel   rel   rel   rel   rel

ACTIVITIES: List[Activity] = [
    # --- Tier 0: Passage ---
    _act("A01", "Walking through",           0, "necessary",
         [MID,  HIGH, MID,  REJECT, MID,  MID,  MID,  MID,  MID],
         [SKIP, REL,  SKIP, REL,    SKIP, SKIP, SKIP, SKIP, SKIP],
         group=(1,1), dur=(0,1), cites=["Gehl 2011"]),

    _act("A02", "Wayfinding / orienting",    0, "necessary",
         [MID,  HIGH, HIGH, REJECT, MID,  MID,  HIGH, MID,  MID],
         [SKIP, REL,  REL,  REL,    SKIP, SKIP, REL,  SKIP, SKIP],
         group=(1,1), dur=(0,1), cites=["Gehl 2011", "Kaplan 1995 legibility"]),

    _act("A03", "Waiting (standing)",        0, "necessary",
         [MID,  MID,  MID,  REJECT, MID,  MID,  MID,  MID,  HIGH],
         [SKIP, SKIP, SKIP, REL,    SKIP, SKIP, SKIP, SKIP, REL],
         group=(1,2), dur=(1,5), cites=["Whyte 1980 edge effect"]),

    # --- Tier 1: Solitary dwelling ---
    _act("A04", "Solitary focused work",     1, "optional",
         [HIGH, LOW,  HIGH, REJECT, MID,  HIGH, LOW,  MID,  HIGH],
         [REL,  REL,  REL,  REL,    SKIP, REL,  REL,  SKIP, REL],
         group=(1,1), dur=(15,120), cites=["Mehrabian-Russell 1974", "Kaplan 1995"]),

    _act("A05", "Solitary contemplation",    1, "optional",
         [HIGH, MID,  MID,  REJECT, HIGH, HIGH, LOW,  MID,  HIGH],
         [REL,  SKIP, SKIP, REL,    REL,  REL,  REL,  SKIP, REL],
         group=(1,1), dur=(5,30), cites=["Kaplan 1995 ART"]),

    _act("A06", "People-watching",           1, "optional",
         [MID,  HIGH, MID,  MID,  MID,  MID,  HIGH, MID,  HIGH],
         [SKIP, REL,  SKIP, SKIP,  SKIP, SKIP, REL,  SKIP, REL],
         group=(1,1), dur=(5,60), cites=["Whyte 1980", "Gehl 2011"]),

    _act("A07", "Phone call (private)",      1, "optional",
         [HIGH, LOW,  MID,  MID,  MID,  HIGH, LOW,  MID,  MID],
         [REL,  REL,  SKIP, SKIP, SKIP, REL,  REL,  SKIP, SKIP],
         group=(1,1), dur=(2,15), cites=["Hall 1966 personal distance"]),

    _act("A08", "Eating alone",              1, "optional",
         [MID,  MID,  MID,  REJECT, HIGH, MID,  MID,  MID,  HIGH],
         [SKIP, SKIP, SKIP, REL,    REL,  SKIP, SKIP, SKIP, REL],
         group=(1,1), dur=(10,30), cites=["Whyte 1980"]),

    # --- Tier 2: Dyadic social ---
    _act("A09", "Intimate conversation",     2, "social",
         [HIGH, LOW,  LOW,  REJECT, HIGH, HIGH, LOW,  HIGH, HIGH],
         [REL,  REL,  REL,  REL,    REL,  REL,  REL,  REL,  REL],
         group=(2,2), dur=(10,60), cites=["Hall 1966 intimate/personal", "Mehrabian-Russell 1974"]),

    _act("A10", "Professional meeting (1:1)", 2, "social",
         [HIGH, LOW,  HIGH, REJECT, MID,  HIGH, LOW,  HIGH, MID],
         [REL,  REL,  REL,  REL,    SKIP, REL,  REL,  REL,  SKIP],
         group=(2,2), dur=(15,60), cites=["Hall 1966 social distance"]),

    _act("A11", "Chance encounter",          2, "social",
         [LOW,  HIGH, MID,  MID,  MID,  MID,  MID,  MID,  MID],
         [REL,  REL,  SKIP, SKIP, SKIP, SKIP, SKIP, SKIP, SKIP],
         group=(2,2), dur=(0,3), cites=["Whyte 1980 triangulation", "Gehl 2011"]),

    _act("A12", "Collaborative desk work",   2, "social",
         [MID,  LOW,  HIGH, REJECT, MID,  MID,  LOW,  HIGH, MID],
         [SKIP, REL,  REL,  REL,    SKIP, SKIP, REL,  REL,  SKIP],
         group=(2,2), dur=(30,120), cites=["Alexander 1977 Pattern 152"]),

    # --- Tier 3: Small-group social ---
    _act("A13", "Small group conversation",  3, "social",
         [MID,  MID,  MID,  REJECT, HIGH, HIGH, LOW,  HIGH, MID],
         [SKIP, SKIP, SKIP, REL,    REL,  REL,  REL,  REL,  SKIP],
         group=(3,5), dur=(10,45), cites=["Hall 1966", "Osmond 1957 sociopetal"]),

    _act("A14", "Informal stand-up",         3, "social",
         [LOW,  HIGH, HIGH, REJECT, MID,  MID,  MID,  MID,  MID],
         [REL,  REL,  REL,  REL,    SKIP, SKIP, SKIP, SKIP, SKIP],
         group=(3,6), dur=(5,15), cites=["Gehl 2011"]),

    _act("A15", "Collaborative workshop",    3, "social",
         [MID,  LOW,  HIGH, REJECT, MID,  HIGH, LOW,  HIGH, MID],
         [SKIP, REL,  REL,  REL,    SKIP, REL,  REL,  REL,  SKIP],
         group=(4,8), dur=(30,120), cites=["Alexander 1977 Pattern 142"]),

    _act("A16", "Shared meal",               3, "social",
         [MID,  MID,  MID,  REJECT, HIGH, MID,  MID,  HIGH, MID],
         [SKIP, SKIP, SKIP, REL,    REL,  SKIP, SKIP, REL,  SKIP],
         group=(3,8), dur=(20,60), cites=["Gehl 2011"]),

    _act("A17", "Presentation (small)",      3, "social",
         [HIGH, LOW,  HIGH, REJECT, MID,  HIGH, LOW,  LOW,  MID],
         [REL,  REL,  REL,  REL,    SKIP, REL,  REL,  REL,  SKIP],
         group=(5,20), dur=(15,60), cites=["Alexander 1977 Pattern 151"]),

    # --- Tier 4: Special modes ---
    _act("A18", "Restorative pause",         4, "optional",
         [MID,  HIGH, MID,  REJECT, HIGH, HIGH, LOW,  MID,  HIGH],
         [SKIP, REL,  SKIP, REL,    REL,  REL,  REL,  SKIP, REL],
         group=(1,1), dur=(5,20), cites=["Kaplan 1995 ART"]),

    _act("A19", "Creative brainstorm",       4, "social",
         [MID,  MID,  HIGH, REJECT, HIGH, MID,  MID,  HIGH, MID],
         [SKIP, SKIP, REL,  REL,    REL,  SKIP, SKIP, REL,  SKIP],
         group=(2,6), dur=(15,60), cites=["Mehrabian-Russell 1974 moderate arousal"]),

    _act("A20", "Difficult conversation",    4, "social",
         [HIGH, LOW,  LOW,  REJECT, MID,  HIGH, LOW,  HIGH, HIGH],
         [REL,  REL,  REL,  REL,    SKIP, REL,  REL,  REL,  REL],
         group=(2,3), dur=(10,30), cites=["Hall 1966", "Alexander 1977 Pattern 127"]),

    _act("A21", "Play",                      4, "social",
         [LOW,  HIGH, HIGH, MID,  MID,  LOW,  HIGH, MID,  MID],
         [REL,  REL,  REL,  SKIP, SKIP, REL,  REL,  SKIP, SKIP],
         group=(2,10), dur=(5,60), cites=["Gehl 2011", "Gibson 1979 affordances"]),

    _act("A22", "Meditation / mindfulness",  4, "optional",
         [HIGH, MID,  LOW,  REJECT, HIGH, HIGH, LOW,  MID,  HIGH],
         [REL,  SKIP, REL,  REL,    REL,  REL,  REL,  SKIP, REL],
         group=(1,1), dur=(5,30), cites=["Kaplan 1995 soft fascination"]),

    _act("A23", "Napping / resting",         4, "optional",
         [HIGH, LOW,  LOW,  REJECT, HIGH, HIGH, LOW,  MID,  HIGH],
         [REL,  REL,  REL,  REL,    REL,  REL,  REL,  SKIP, REL],
         group=(1,1), dur=(15,60), cites=["Mehrabian-Russell 1974 low arousal"]),

    _act("A24", "Performance / exhibition",  4, "social",
         [LOW,  HIGH, HIGH, REJECT, MID,  MID,  HIGH, MID,  HIGH],
         [REL,  REL,  REL,  REL,    SKIP, SKIP, REL,  SKIP, REL],
         group=(1,100), dur=(5,60), cites=["Whyte 1980 triangulation"]),
]

ACTIVITY_BY_CODE = {a.code: a for a in ACTIVITIES}


# ═══════════════════════════════════════════════════════════════════════
#  PERSONALITY MODERATORS
# ═══════════════════════════════════════════════════════════════════════

# Per Mehrabian & Russell 1974, Zuckerman 1979 optimal stimulation level:
#   Introverts have lower arousal threshold → prefer more enclosure,
#   less prospect, less saliency, more acoustic absorption.
#   Weights modulate the condition-signature match.
#
# Order matches ATTR_NAMES:
#   [enclosure, prospect, brightness, glare, warmth, acoustics, saliency, sociopetal, edge]

PERSONALITY_WEIGHTS = {
    "introvert":  np.array([1.15, 0.90, 0.95, 1.0, 1.05, 1.10, 1.20, 0.95, 1.05]),
    "extrovert":  np.array([0.85, 1.10, 1.05, 1.0, 0.95, 0.90, 0.80, 1.05, 0.95]),
    "neutral":    np.ones(N_ATTRS),
}


# ═══════════════════════════════════════════════════════════════════════
#  TIME-OF-DAY MODERATORS
# ═══════════════════════════════════════════════════════════════════════

# Per Cajochen et al. 2005, 2011:
#   Morning: bright cool light → alertness; focused work favored
#   Afternoon: post-lunch dip → restorative activities
#   Evening: warm dim light → social activities favored

def _time_weight(hour: int) -> np.ndarray:
    """Return attribute-level weights for time of day.
    Citation: Cajochen et al. 2005, 2011 circadian lighting."""
    # Order: [enclosure, prospect, brightness, glare, warmth, acoustics, saliency, sociopetal, edge]
    if 6 <= hour < 10:    # morning
        return np.array([1.0, 1.0, 1.15, 1.0, 0.90, 1.0, 1.0, 1.0, 1.0])
    elif 14 <= hour < 17:  # afternoon dip
        return np.array([1.0, 1.10, 0.95, 1.0, 1.05, 1.05, 0.90, 1.0, 1.0])
    elif 17 <= hour < 21:  # evening
        return np.array([1.0, 1.0, 0.85, 1.0, 1.15, 1.0, 1.0, 1.05, 1.0])
    else:                  # baseline
        return np.ones(N_ATTRS)


# ═══════════════════════════════════════════════════════════════════════
#  SIGNATURE MATCHING
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ActivityPrediction:
    """Prediction of how well a space supports a given activity."""
    activity: Activity
    match_score: float           # [0,1] raw signature match
    adjusted_score: float        # [0,1] after personality + time modulation
    personality: str             # "introvert", "extrovert", "neutral"
    hour: Optional[int]          # time of day (0-23) or None
    attribute_gaps: Dict[str, float]  # which attributes deviate most


def match_activity(x: np.ndarray, activity: Activity,
                   personality: str = "neutral",
                   hour: Optional[int] = None) -> ActivityPrediction:
    """Score how well attribute vector x matches activity's condition signature.

    Args:
        x: attribute vector of shape (N_ATTRS,), values in [0,1]
        activity: Activity to match against
        personality: "introvert", "extrovert", or "neutral"
        hour: time of day (0-23) or None for no time modulation

    Returns:
        ActivityPrediction with match scores and gap analysis
    """
    assert x.shape == (N_ATTRS,), f"Expected ({N_ATTRS},), got {x.shape}"

    p = activity.profile
    m = activity.relevance

    # Raw match: weighted mean absolute deviation from ideal
    diffs = np.abs(x - p)
    weighted_sum = float((m * diffs).sum())
    weight_total = float(m.sum()) + 1e-9
    raw_match = 1.0 - weighted_sum / weight_total

    # Personality modulation
    pw = PERSONALITY_WEIGHTS.get(personality, np.ones(N_ATTRS))

    # Time modulation
    tw = _time_weight(hour) if hour is not None else np.ones(N_ATTRS)

    # Combined modulation: adjust profile, re-score
    p_adj = np.clip(p * pw * tw, 0, 1)
    diffs_adj = np.abs(x - p_adj)
    adj_match = 1.0 - float((m * diffs_adj).sum()) / weight_total

    # Gap analysis: which attributes deviate most?
    gaps = {}
    for i, name in enumerate(ATTR_NAMES):
        if m[i] > 0 and diffs[i] > 0.25:
            gaps[name] = round(float(x[i] - p[i]), 3)

    return ActivityPrediction(
        activity=activity,
        match_score=round(max(0.0, min(1.0, raw_match)), 4),
        adjusted_score=round(max(0.0, min(1.0, adj_match)), 4),
        personality=personality,
        hour=hour,
        attribute_gaps=gaps,
    )


def predict_activities(x: np.ndarray,
                       personality: str = "neutral",
                       hour: Optional[int] = None,
                       top_k: int = 5,
                       threshold: float = 0.5,
                       ) -> List[ActivityPrediction]:
    """Predict which activities a space supports, ranked by match score.

    Args:
        x: attribute vector, shape (N_ATTRS,), values in [0,1]
        personality: "introvert", "extrovert", or "neutral"
        hour: time of day (0-23) or None
        top_k: max number of predictions to return
        threshold: minimum match score to include

    Returns:
        List of ActivityPrediction, sorted by adjusted_score descending
    """
    predictions = []
    for act in ACTIVITIES:
        pred = match_activity(x, act, personality, hour)
        if pred.adjusted_score >= threshold:
            predictions.append(pred)

    predictions.sort(key=lambda p: p.adjusted_score, reverse=True)
    return predictions[:top_k]


def attribute_vector_from_results(results: Dict[str, float]) -> np.ndarray:
    """Build an attribute vector from a dict of {canonical_key: scalar}.

    Maps canonical pipeline keys to the ATTR_NAMES order.
    Missing attributes default to 0.5 (agnostic).
    """
    KEY_MAP = {
        "cnfa.spatial.enclosure_index":       "enclosure",
        "cnfa.spatial.prospect":              "prospect",
        "cnfa.light.brightness_variance":     "brightness",
        "cnfa.light.glare_risk":              "glare",
        "cnfa.light.warm_vs_cool_ratio":      "warmth",
        "cnfa.acoustics.absorption_proxy":    "acoustics",
        "cnfa.cognitive.landmark_salience":   "saliency",
        "cnfa.social.sociopetal_seating":      "sociopetal",
        "cnfa.fluency.edge_clarity_mean":     "edge_clarity",
    }
    mapped = {}
    for k, v in results.items():
        if k in KEY_MAP:
            mapped[KEY_MAP[k]] = v

    vec = np.full(N_ATTRS, 0.5)
    for i, name in enumerate(ATTR_NAMES):
        if name in mapped:
            vec[i] = mapped[name]
    return vec


# ═══════════════════════════════════════════════════════════════════════
#  CONVENIENCE: HUMAN-READABLE OUTPUT
# ═══════════════════════════════════════════════════════════════════════

RATING_LABELS = {
    (0.75, 1.01): "LIKELY",
    (0.55, 0.75): "POSSIBLE",
    (0.35, 0.55): "UNLIKELY",
    (0.00, 0.35): "VERY_UNLIKELY",
}


def rating_label(score: float) -> str:
    for (lo, hi), label in RATING_LABELS.items():
        if lo <= score < hi:
            return label
    return "UNKNOWN"


def format_prediction(pred: ActivityPrediction) -> str:
    """Format a single prediction as a human-readable string."""
    act = pred.activity
    label = rating_label(pred.adjusted_score)
    gaps = ", ".join(f"{k}={v:+.2f}" for k, v in pred.attribute_gaps.items())
    mods = []
    if pred.personality != "neutral":
        mods.append(f"personality={pred.personality}")
    if pred.hour is not None:
        mods.append(f"hour={pred.hour:02d}")
    mod_str = f" [{', '.join(mods)}]" if mods else ""
    return (f"  {act.code} {act.name}: {label} "
            f"(match={pred.adjusted_score:.2f}){mod_str}"
            f"{f'  gaps: {gaps}' if gaps else ''}")
