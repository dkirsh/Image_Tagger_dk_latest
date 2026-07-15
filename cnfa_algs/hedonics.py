"""
cnfa_algs.hedonics — the RESPONSE-SHAPE contract for fluency/hedonic attributes.

The fluency-family attributes (symmetry, edge/figure-ground clarity, processing-load,
palette-entropy, fractal dimension, warmth, glare) are the ones that implicitly bet on
perceptual fluency -> affect. The science (see FLUENCY_AND_HEDONICS.md) says the fluency
-> immediate-liking DIRECTION is sound, but the value->preference FUNCTION is often
NON-MONOTONIC (complexity/variety/fractal have an inverted-U, Berlyne / Graf & Landwehr),
sometimes context-dependent (hue), and never a calibrated scalar.

This module makes that a machine-enforceable contract: every fluency-family attribute
declares its correct RESPONSE SHAPE, and any code that maps a raw attribute value to a
hedonic/preference score MUST go through `hedonic_response`, which applies the declared
shape — so a complexity measure can never be silently scored monotone. Attributes whose
hedonic sign is context-dependent ABSTAIN (return a null tag, licensed=False).

Self-test (analytic L0):
    python -m cnfa_algs.hedonics
"""
from __future__ import annotations
from typing import Dict, Optional
import numpy as np

# shape ::= monotone_pos | monotone_neg | inverted_u | context(abstain)
# evidence grade carries the honesty tag; 'promising-import' = strong-in-lab, untested-in-building.
HEDONIC_SHAPE: Dict[str, Dict] = {
    "cnfa.fluency.symmetry_score_horizontal":
        {"shape": "monotone_pos", "evidence": "STRONG-lab/promising-import", "peak": None,
         "note": "symmetry is a fluency driver & is preferred; domain limits (faces > abstract art)"},
    "cnfa.fluency.edge_clarity_mean":
        {"shape": "monotone_pos", "evidence": "STRONG", "peak": None,
         "note": "figure-ground contrast/clarity raises fluency"},
    "cnfa.fluency.processing_load_proxy":
        {"shape": "inverted_u", "evidence": "CONTESTED", "peak": 0.40,
         "note": "complexity: Berlyne collative inverted-U; disfluency drives INTEREST — NOT monotone"},
    "cnfa.fluency.color_palette_entropy":
        {"shape": "inverted_u", "evidence": "CONTESTED", "peak": 0.50,
         "note": "colour variety: moderate preferred, too much = overload (inverted-U)"},
    "cnfa.fractal_dimension":
        {"shape": "inverted_u", "evidence": "PROMISING", "peak": 1.40, "scale": (1.0, 2.0),
         "note": "D~1.3-1.5 preferred & arousal-reducing (Taylor, Hagerhall) — inverted-U"},
    "cnfa.light.warm_vs_cool_ratio":
        {"shape": "context", "evidence": "CONTESTED-weak", "peak": None,
         "note": "hue-affect largely fails to replicate; abstain from a hedonic tag (Elliot & Maier)"},
    "glare-risk":
        {"shape": "monotone_neg", "evidence": "STRONG", "peak": None,
         "note": "discomfort glare is a detractor"},
}
FLUENCY_FAMILY = set(HEDONIC_SHAPE)


def _inverted_u(v: float, peak: float, scale=(0.0, 1.0)) -> float:
    """Triangular inverted-U peaking at `peak`, 1.0 at the peak, falling to 0 at the ends
    of `scale`. v is first normalized into [0,1] over scale."""
    lo, hi = scale
    x = (float(v) - lo) / (hi - lo + 1e-9)
    pk = (peak - lo) / (hi - lo + 1e-9)
    x = min(max(x, 0.0), 1.0)
    reach = max(pk, 1.0 - pk)                     # distance from peak to the farther end
    return float(np.clip(1.0 - abs(x - pk) / (reach + 1e-9), 0.0, 1.0))


def hedonic_response(attr_key: str, raw_value: Optional[float]) -> Dict:
    """Map a raw attribute value to a hedonic/preference score via the DECLARED shape.
    Returns {value, licensed, shape, evidence, note}. `value` is None (and licensed=False)
    for context-dependent attributes — the contract's way of REFUSING an unlicensed tag.
    Every licensed value is a *promising-import* prediction of immediate hedonic DIRECTION,
    never a calibrated scalar — validate at L2/L3 before trusting."""
    spec = HEDONIC_SHAPE.get(attr_key)
    if spec is None:
        return {"value": None, "licensed": False, "shape": "unregistered",
                "evidence": None, "note": f"{attr_key} not a registered fluency attribute"}
    shape = spec["shape"]
    if raw_value is None:
        val = None
    elif shape == "monotone_pos":
        val = float(np.clip(raw_value, 0, 1))
    elif shape == "monotone_neg":
        val = float(np.clip(1 - raw_value, 0, 1))
    elif shape == "inverted_u":
        val = _inverted_u(raw_value, spec["peak"], spec.get("scale", (0.0, 1.0)))
    else:  # context -> abstain
        return {"value": None, "licensed": False, "shape": shape,
                "evidence": spec["evidence"], "note": "hedonic sign context-dependent — abstaining"}
    return {"value": val, "licensed": val is not None, "shape": shape,
            "evidence": spec["evidence"], "note": spec["note"], "grade": "promising-import"}


def validate_hedonic_registry() -> list:
    """Contract check: every registered attribute has a known shape; every inverted-U has a
    peak; NO complexity/variety/fractal attribute is registered monotone (the core rule)."""
    problems = []
    complexity = {"cnfa.fluency.processing_load_proxy", "cnfa.fluency.color_palette_entropy",
                  "cnfa.fractal_dimension"}
    for k, spec in HEDONIC_SHAPE.items():
        if spec["shape"] not in ("monotone_pos", "monotone_neg", "inverted_u", "context"):
            problems.append(f"{k}: unknown shape {spec['shape']}")
        if spec["shape"] == "inverted_u" and spec.get("peak") is None:
            problems.append(f"{k}: inverted_u without a peak")
        if k in complexity and spec["shape"] != "inverted_u":
            problems.append(f"{k}: complexity attribute MUST be inverted_u, not {spec['shape']}")
    return problems


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.hedonics self-test (analytic L0)\n" + "-" * 42)

    # registry contract
    probs = validate_hedonic_registry()
    print("registry problems:", probs)
    assert not probs, f"registry violations: {probs}"

    # inverted-U: peak scores highest; both extremes lower (NON-monotone)
    lo = hedonic_response("cnfa.fluency.processing_load_proxy", 0.05)["value"]
    mid = hedonic_response("cnfa.fluency.processing_load_proxy", 0.40)["value"]
    hi = hedonic_response("cnfa.fluency.processing_load_proxy", 0.95)["value"]
    print(f"processing_load inverted-U: low={lo:.2f} peak={mid:.2f} high={hi:.2f}")
    assert mid > lo and mid > hi, "complexity must peak at the optimum, not at an extreme"

    # fractal peak at D~1.4 over scale (1,2)
    fpk = hedonic_response("cnfa.fractal_dimension", 1.40)["value"]
    fend = hedonic_response("cnfa.fractal_dimension", 1.95)["value"]
    print(f"fractal: D=1.40 -> {fpk:.2f}, D=1.95 -> {fend:.2f}")
    assert fpk > fend, "fractal preference peaks mid-range, not at high D"

    # monotone_pos rises; monotone_neg falls
    assert hedonic_response("cnfa.fluency.edge_clarity_mean", 0.9)["value"] > \
           hedonic_response("cnfa.fluency.edge_clarity_mean", 0.1)["value"], "clarity monotone up"
    assert hedonic_response("glare-risk", 0.9)["value"] < \
           hedonic_response("glare-risk", 0.1)["value"], "glare monotone down"

    # context attribute ABSTAINS (refuses an unlicensed tag)
    warm = hedonic_response("cnfa.light.warm_vs_cool_ratio", 0.8)
    print("warmth tag:", warm["value"], "licensed:", warm["licensed"])
    assert warm["value"] is None and warm["licensed"] is False, "hue must abstain from a hedonic tag"

    print("-" * 42 + "\nhedonics self-test: PASS")
