"""
cnfa_algs.vlm_activity_prompt — Structured VLM prompt protocol for
activity-likelihood rating and cross-validation with attribute predictions.

This module generates prompts for Gemini/VLM to rate which activities
a photographed space supports, parses the structured response, and
detects disagreements between attribute-based predictions and VLM ratings.

The prompt protocol is designed per the approved Activity Prediction
Framework (docs/ACTIVITY_PREDICTION_FRAMEWORK.md).

Usage:
    from cnfa_algs.vlm_activity_prompt import (
        build_activity_prompt, parse_vlm_response,
        detect_disagreements, format_claim
    )
    prompt = build_activity_prompt()
    # Send prompt + image to Gemini → get response text
    vlm_result = parse_vlm_response(response_text)
    disagreements = detect_disagreements(attr_predictions, vlm_result)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json
import re

from .activity import (
    ACTIVITIES, Activity, ActivityPrediction,
    predict_activities, rating_label, ATTR_NAMES,
)


# ═══════════════════════════════════════════════════════════════════════
#  PROMPT CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════

RATING_SCALE = """Rate each activity using EXACTLY one of these labels:
  LIKELY         — you would expect to see this activity here
  POSSIBLE       — it could happen but isn't especially invited
  UNLIKELY       — the space seems wrong for this activity
  VERY_UNLIKELY  — the space actively discourages this activity"""

RESPONSE_FORMAT = """Respond in this EXACT format for each activity (one per line):
  CODE | RATING | REASON
where:
  CODE = the activity code (e.g. A01)
  RATING = one of LIKELY, POSSIBLE, UNLIKELY, VERY_UNLIKELY
  REASON = the ONE physical feature of the space that most influences your rating

Example:
  A04 | LIKELY | The enclosed alcove with soft lighting provides visual privacy for focused work
  A11 | UNLIKELY | The narrow corridor lacks stopping points for spontaneous encounters"""


def build_activity_prompt(activities: Optional[List[Activity]] = None,
                          context: str = "") -> str:
    """Build the structured prompt for Gemini activity-likelihood rating.

    Args:
        activities: list of activities to rate (default: all 24)
        context: optional additional context about the image

    Returns:
        Prompt string to send with the image to Gemini
    """
    acts = activities or ACTIVITIES

    activity_list = "\n".join(
        f"  {a.code}. {a.name} (group: {a.group_size[0]}-{a.group_size[1]}, "
        f"typical duration: {a.duration_min[0]}-{a.duration_min[1]} min)"
        for a in acts
    )

    prompt = f"""You are an expert in environmental psychology and architectural design,
trained in the work of Jan Gehl, William Whyte, Christopher Alexander,
and Edward Hall. You understand how physical spaces shape human behavior.

Look at this photograph of an architectural space and rate the likelihood
of each activity occurring here based on the physical features you observe.

{RATING_SCALE}

Activities to rate:
{activity_list}

{RESPONSE_FORMAT}

IMPORTANT GUIDELINES:
- Base your ratings ONLY on the physical features visible in the image
- Consider: lighting, enclosure, openness, seating arrangement, acoustics
  (inferred from materials), sightlines, and overall atmosphere
- Do NOT assume the presence of people — rate the space's POTENTIAL
- Rate ALL activities listed above
{f"Additional context: {context}" if context else ""}

Begin your ratings:"""

    return prompt


def build_focused_prompt(activity_codes: List[str],
                         context: str = "") -> str:
    """Build a focused prompt for a subset of activities.

    Use when you want detailed reasoning for specific activities
    rather than a quick scan of all 24.
    """
    acts = [a for a in ACTIVITIES if a.code in activity_codes]
    if not acts:
        raise ValueError(f"No activities found for codes: {activity_codes}")
    return build_activity_prompt(acts, context)


# ═══════════════════════════════════════════════════════════════════════
#  RESPONSE PARSING
# ═══════════════════════════════════════════════════════════════════════

VALID_RATINGS = {"LIKELY", "POSSIBLE", "UNLIKELY", "VERY_UNLIKELY"}
RATING_SCORES = {
    "LIKELY": 0.85,
    "POSSIBLE": 0.60,
    "UNLIKELY": 0.30,
    "VERY_UNLIKELY": 0.10,
}


@dataclass
class VLMActivityRating:
    """A single activity rating from the VLM."""
    code: str
    rating: str              # LIKELY, POSSIBLE, UNLIKELY, VERY_UNLIKELY
    score: float             # numeric score (0-1)
    reason: str              # the physical feature cited
    raw_line: str = ""       # original response line


@dataclass
class VLMResponse:
    """Parsed VLM response for all activities."""
    ratings: Dict[str, VLMActivityRating]  # keyed by activity code
    unparsed_lines: List[str] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)


def parse_vlm_response(response_text: str) -> VLMResponse:
    """Parse the VLM's structured response into typed ratings.

    Tolerant parser: handles variations in formatting, extra whitespace,
    missing pipe separators, etc.
    """
    ratings = {}
    unparsed = []
    errors = []

    for line in response_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Begin"):
            continue

        # Try pipe-separated format first: A04 | LIKELY | reason
        parts = [p.strip() for p in line.split("|")]

        if len(parts) >= 3:
            code = parts[0].upper().strip()
            rating = parts[1].upper().strip()
            reason = parts[2].strip()
        elif len(parts) == 2:
            code = parts[0].upper().strip()
            rating = parts[1].upper().strip()
            reason = ""
        else:
            # Try regex: A04 LIKELY reason...
            m = re.match(r'(A\d{2})\s+(LIKELY|POSSIBLE|UNLIKELY|VERY_UNLIKELY)\s*(.*)',
                         line, re.IGNORECASE)
            if m:
                code, rating, reason = m.group(1).upper(), m.group(2).upper(), m.group(3).strip()
            else:
                unparsed.append(line)
                continue

        # Validate
        if not re.match(r'^A\d{2}$', code):
            errors.append(f"Invalid code: {code} in line: {line}")
            continue
        if rating not in VALID_RATINGS:
            errors.append(f"Invalid rating: {rating} in line: {line}")
            continue

        ratings[code] = VLMActivityRating(
            code=code,
            rating=rating,
            score=RATING_SCORES[rating],
            reason=reason,
            raw_line=line,
        )

    return VLMResponse(ratings=ratings, unparsed_lines=unparsed, parse_errors=errors)


# ═══════════════════════════════════════════════════════════════════════
#  DISAGREEMENT DETECTION
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Disagreement:
    """A case where attribute-based prediction and VLM rating diverge."""
    activity_code: str
    activity_name: str
    attr_score: float
    attr_label: str
    vlm_score: float
    vlm_label: str
    vlm_reason: str
    severity: str              # "minor", "major", "critical"
    interpretation: str        # what the disagreement might mean


def detect_disagreements(attr_predictions: List[ActivityPrediction],
                         vlm_response: VLMResponse,
                         threshold: float = 0.3,
                         ) -> List[Disagreement]:
    """Find cases where attribute predictions and VLM ratings disagree.

    A disagreement is significant when the attribute-based score and
    VLM score differ by more than `threshold`.

    Args:
        attr_predictions: predictions from predict_activities()
        vlm_response: parsed VLM response
        threshold: minimum score difference to flag

    Returns:
        List of Disagreement objects, sorted by severity
    """
    disagreements = []

    # Build lookup from attr predictions
    attr_by_code = {p.activity.code: p for p in attr_predictions}

    # Check all activities that appear in both sources
    all_codes = set(attr_by_code.keys()) | set(vlm_response.ratings.keys())

    for code in all_codes:
        attr_pred = attr_by_code.get(code)
        vlm_rating = vlm_response.ratings.get(code)

        if attr_pred is None or vlm_rating is None:
            continue

        diff = abs(attr_pred.adjusted_score - vlm_rating.score)
        if diff < threshold:
            continue

        # Classify severity
        if diff >= 0.5:
            severity = "critical"
        elif diff >= 0.35:
            severity = "major"
        else:
            severity = "minor"

        # Interpret the disagreement
        attr_high = attr_pred.adjusted_score > vlm_rating.score
        if attr_high:
            interp = (f"Attributes suggest this space supports {attr_pred.activity.name}, "
                      f"but VLM disagrees because: {vlm_rating.reason}. "
                      "Possible: attribute model overweights a condition, "
                      "or VLM sees something not captured by pixel attributes "
                      "(e.g., signage, furniture style, cultural context).")
        else:
            interp = (f"VLM sees this space as suitable for {attr_pred.activity.name}, "
                      f"but attributes disagree. VLM reason: {vlm_rating.reason}. "
                      "Possible: missing attribute (e.g., ceiling height, greenery), "
                      "or condition signature too restrictive.")

        disagreements.append(Disagreement(
            activity_code=code,
            activity_name=attr_pred.activity.name,
            attr_score=attr_pred.adjusted_score,
            attr_label=rating_label(attr_pred.adjusted_score),
            vlm_score=vlm_rating.score,
            vlm_label=vlm_rating.rating,
            vlm_reason=vlm_rating.reason,
            severity=severity,
            interpretation=interp,
        ))

    disagreements.sort(key=lambda d: {"critical": 0, "major": 1, "minor": 2}[d.severity])
    return disagreements


# ═══════════════════════════════════════════════════════════════════════
#  STRUCTURED CLAIM OUTPUT
# ═══════════════════════════════════════════════════════════════════════

def format_claim(pred: ActivityPrediction,
                 vlm_rating: Optional[VLMActivityRating] = None,
                 attribute_confidences: Optional[Dict[str, float]] = None,
                 ) -> str:
    """Format a full structured claim with evidence, moderation, and VLM corroboration.

    This is the publishable output format described in the framework.
    """
    act = pred.activity
    label = rating_label(pred.adjusted_score)

    lines = [
        f"CLAIM: Activity {act.code} ({act.name}) is {label} in this space.",
        "",
        "PHYSICAL EVIDENCE:",
    ]

    # Attribute values (from gaps, which only lists deviators)
    for name in ATTR_NAMES:
        gap_val = pred.attribute_gaps.get(name)
        if gap_val is not None:
            lines.append(f"  {name}: deviation {gap_val:+.2f} from ideal")

    lines.append(f"\nSIGNATURE MATCH: {pred.match_score:.2f}")

    if pred.personality != "neutral" or pred.hour is not None:
        lines.append("\nMODERATORS:")
        if pred.personality != "neutral":
            delta = pred.adjusted_score - pred.match_score
            lines.append(f"  Personality ({pred.personality}): {delta:+.3f}")
        if pred.hour is not None:
            lines.append(f"  Time of day: {pred.hour:02d}:00")

    if vlm_rating:
        lines.append(f"\nVLM CORROBORATION: Gemini rates {act.code} as {vlm_rating.rating}.")
        if vlm_rating.reason:
            lines.append(f"  Cited reason: \"{vlm_rating.reason}\"")

    if attribute_confidences:
        min_conf_name = min(attribute_confidences, key=attribute_confidences.get)
        min_conf = attribute_confidences[min_conf_name]
        lines.append(f"\nCONFIDENCE:")
        lines.append(f"  Weakest link: {min_conf_name} (conf={min_conf:.2f})")

    lines.append(f"\nCITATIONS: {', '.join(act.citations)}")
    lines.append("")

    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════
#  SECOND-PASS: Populated-space VLM query
# ═══════════════════════════════════════════════════════════════════════

POPULATED_RESPONSE_FORMAT = """Respond in this EXACT JSON format:
{
  "flow_matches_intuition": true|false,
  "flow_mismatch_reason": "string or null",
  "high_density_activities": ["activity1", "activity2", ...],
  "low_density_activities": ["activity1", "activity2", ...],
  "unexpected_patterns": "string describing anything the model finds surprising, or null"
}"""


def build_populated_prompt(
    occupancy_scalar: float = 0.0,
    n_free_cells: int = 0,
    clustering_scalar: float = 0.0,
    trace_entropy: float = 0.0,
    context: str = "",
) -> str:
    """Build the second-pass VLM prompt for occupancy-overlay evaluation.

    This prompt accompanies a composite image: the original space photo
    with the predicted occupancy heatmap overlaid. The VLM is asked
    whether the predicted flow matches its spatial intuition and what
    activities would occur at high vs. low density locations.

    The composite image must be sent alongside this text prompt.

    Citation: The two-pass protocol (attributes → simulation → VLM)
    is a project convention; no published source for this specific
    prompt design. The underlying occupancy model is grounded in
    Hillier 1996 and Turner 2001.

    Args:
        occupancy_scalar: mean predicted occupancy [0, 1]
        n_free_cells: number of walkable cells in the BEV grid
        clustering_scalar: fraction of agents in top-10% density cells
        trace_entropy: normalised Shannon entropy of movement paths
        context: optional additional context string

    Returns:
        Prompt text (the composite image is sent separately).
    """
    parts = [
        "SECOND-PASS EVALUATION: Predicted Human Occupancy",
        "",
        "This image shows a space with PREDICTED HUMAN OCCUPANCY overlaid as a heatmap.",
        "Brighter/warmer areas indicate where MORE people are predicted to walk or gather,",
        "based on a Visibility Graph Analysis of the spatial configuration (Turner et al. 2001)",
        "and an agent-based simulation using Hillier's natural movement model (1996).",
        "",
        "KEY STATISTICS from the simulation:",
        f"  • Mean occupancy density: {occupancy_scalar:.3f}",
        f"  • Walkable area: {n_free_cells} grid cells",
        f"  • Clustering index: {clustering_scalar:.3f} "
        "(fraction of flow concentrated in top 10% of cells)",
        f"  • Path diversity (entropy): {trace_entropy:.3f} "
        "(higher = more diverse movement patterns)",
        "",
        "QUESTIONS — answer based on what you see in the image:",
        "",
        "1. FLOW VALIDATION: Does the predicted occupancy pattern match your",
        "   spatial intuition about how people would move through and use this",
        "   space? If not, what does the model get wrong?",
        "",
        "2. HIGH-DENSITY LOCATIONS: What specific activities would you expect",
        "   at the hotspots (bright areas)? Name concrete activities, not",
        "   abstract descriptions.",
        "",
        "3. LOW-DENSITY LOCATIONS: What activities would you expect in the",
        "   quiet zones (dark areas)? These are predicted refuges — places",
        "   people tend NOT to pass through.",
        "",
        "4. UNEXPECTED PATTERNS: Is there anything about the predicted flow",
        "   that surprises you? A hotspot where you'd expect quiet, or a",
        "   dead zone where you'd expect activity?",
    ]

    if context:
        parts.append("")
        parts.append(f"ADDITIONAL CONTEXT: {context}")

    parts.append("")
    parts.append(POPULATED_RESPONSE_FORMAT)

    return "\n".join(parts)

