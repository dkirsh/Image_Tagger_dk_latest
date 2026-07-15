"""
annotation_socket.derivation — the VISION trust chokepoint (I7 for predicates).

The extraction controller's rule (trusted_derivation.py): a privilege-granting signal exists
only if MECHANICALLY DERIVED from an authoritative source; absence fails closed to UNKNOWN.
This module is the same rule for annotation: **a predicate SCORE exists only if it was
mechanically derived from image evidence and ships that evidence.** A defaulted, constant,
or evidence-free value is not a low score — it is UNKNOWN, and UNKNOWN routes RED.

Three states (amendment #1, tri-state):
  SCORED     value + evidence chain (region/global/plan-chain) + producing signal + confidence
  ABSTAINED  the predicate's declared `requires` are not in the unit — reason NAMES the
             missing input, so verify() can audit that the abstention is real (you cannot
             launder a failure as an abstention)
  UNKNOWN    should have been derivable but was not (compute failed / no evidence /
             fabricated). Never a number. -> RED.

Evidence is a CHAIN, not one region (amendment #3): a plan metric's honest provenance is
image -> geometry(vp, plane-conf) -> PlanGrid(grid_hash, cell_m) -> value.
"""
from __future__ import annotations
import hashlib
import sys
from typing import Any, Dict, FrozenSet, Optional

sys.path.insert(0, "/home/claude/_control_deps/supervisor")
try:
    from trusted_derivation import UNKNOWN          # the shared sentinel — one trust vocabulary
except Exception:                                   # repo fallback (Mac path)
    sys.path.insert(0, "/Users/davidusa/REPOS/_control/supervisor")
    try:
        from trusted_derivation import UNKNOWN
    except Exception:
        UNKNOWN = "UNKNOWN"

SCORED, ABSTAINED = "SCORED", "ABSTAINED"


def grid_hash(grid) -> str:
    import numpy as np
    return hashlib.sha256(np.ascontiguousarray(grid).tobytes()).hexdigest()[:16]


def evidence_image(kind: str, locator: Any, signal: str, confidence: float,
                   upstream: Optional[list] = None) -> Dict:
    """kind: image_region | global_image | plan_chain. locator: bbox/cells/desc.
    signal: the producing method string. upstream: the derivation chain."""
    return {"kind": kind, "locator": locator, "signal": signal,
            "confidence": round(float(confidence), 3), "upstream": upstream or []}


def _valid_evidence(ev: Any, img_shape=None) -> bool:
    if not isinstance(ev, dict):
        return False
    if ev.get("kind") not in ("image_region", "global_image", "plan_chain"):
        return False
    if not isinstance(ev.get("signal"), str) or not ev["signal"].strip():
        return False
    if ev.get("kind") == "image_region" and img_shape is not None:
        loc = ev.get("locator")
        if not (isinstance(loc, (list, tuple)) and len(loc) == 4):
            return False
        x0, y0, x1, y1 = loc
        H, W = img_shape[:2]
        if not (0 <= x0 <= x1 <= W and 0 <= y0 <= y1 <= H):
            return False           # a cited region that does not exist in the image
    return True


def scored(pred_id: str, value: float, ev: Dict, tier_hint: str,
           img_shape=None) -> Dict:
    """The ONLY constructor for a believed number. No evidence -> UNKNOWN, by construction.
    A None/NaN value -> UNKNOWN. This is where the score_layout fabrication becomes
    structurally impossible: you cannot build a SCORED record without derivation evidence."""
    import math
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return unknown(pred_id, "value_not_finite")
    if not _valid_evidence(ev, img_shape):
        return unknown(pred_id, "evidence_missing_or_invalid")
    return {"predicate": pred_id, "status": SCORED, "value": round(float(value), 4),
            "tier_hint": tier_hint, "evidence": ev}


def abstain(pred_id: str, missing: FrozenSet[str] | set) -> Dict:
    """Mechanically-derived abstention: names the exact missing inputs so verify() can
    confirm they are genuinely absent from the unit (the anti-laundering check)."""
    return {"predicate": pred_id, "status": ABSTAINED,
            "missing_inputs": sorted(missing), "value": None, "evidence": None}


def unknown(pred_id: str, reason: str) -> Dict:
    """Fail-closed: should have been derivable, was not. Never a number; routes RED."""
    return {"predicate": pred_id, "status": UNKNOWN, "reason": reason,
            "value": None, "evidence": None}
