"""
cnfa_algs.contracts — enforceable I/O CONTRACTS for every metric process and the pipeline.

Every criterion function in this package returns a "metric result" dict, and `score_layout`
returns a "layout score" dict. This module defines what those dicts MUST satisfy and gives
validators that enforce it. The contracts are the machine-checkable success conditions;
`validate_pipeline.py` runs them (unit + last-mile) and tries to break them.

Two contracts:
  MetricResult  — the shape every criterion function returns.
  LayoutScore   — the shape score_layout() returns.

A validator returns a list of contract VIOLATIONS (empty list == conforms). It never raises
on a merely non-conforming input — that IS the finding.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# ---- MetricResult contract -------------------------------------------------
REQUIRED_METRIC_KEYS = ("key", "confidence", "method", "failure_modes")
# criteria whose `scalar` is a DOMAIN value (not a [0,1] score) — exempt from the range rule
SCALAR_NOT_UNIT = {"C8"}          # C8 scalar = r_D in metres (converted to a score in score_layout)


def validate_metric_result(res: Any, grid_shape: Optional[Tuple[int, int]] = None,
                           name: str = "") -> List[str]:
    """Check a criterion function's output against the MetricResult contract.
    Returns a list of violation strings (empty == conforms)."""
    p: List[str] = []
    tag = name or (res.get("key", "?") if isinstance(res, dict) else "?")
    if not isinstance(res, dict):
        return [f"{tag}: result is {type(res).__name__}, not dict"]
    if "_error" in res:
        return [f"{tag}: function errored: {res['_error']}"]
    for k in REQUIRED_METRIC_KEYS:
        if k not in res:
            p.append(f"{tag}: missing required key '{k}'")
    # confidence
    c = res.get("confidence")
    if not isinstance(c, (int, float)) or not (0.0 <= float(c) <= 1.0):
        p.append(f"{tag}: confidence {c!r} not a float in [0,1]")
    # method must be a non-empty string
    if not isinstance(res.get("method"), str) or not res.get("method", "").strip():
        p.append(f"{tag}: method missing/empty (a process must state how it computes)")
    # failure_modes must be a non-empty list (RULE 0: disclose the boundary)
    fm = res.get("failure_modes")
    if not isinstance(fm, list) or len(fm) == 0:
        p.append(f"{tag}: failure_modes must be a non-empty list (disclose limits)")
    # scalar: None allowed (degenerate input), else numeric; [0,1] unless exempt
    crit = res.get("criterion", "")
    s = res.get("scalar", None)
    if s is not None:
        if not isinstance(s, (int, float)) or not np.isfinite(s):
            p.append(f"{tag}: scalar {s!r} not a finite number")
        elif crit not in SCALAR_NOT_UNIT and not (0.0 <= float(s) <= 1.0):
            p.append(f"{tag}: scalar {s} out of [0,1] (criterion {crit or 'unnamed'})")
    # field: if present must be ndarray matching the grid
    f = res.get("field")
    if f is not None:
        if not isinstance(f, np.ndarray):
            p.append(f"{tag}: field is {type(f).__name__}, not ndarray")
        elif grid_shape is not None and f.shape != grid_shape:
            p.append(f"{tag}: field shape {f.shape} != grid {grid_shape}")
    # rows: if present must be a list of dicts
    r = res.get("rows")
    if r is not None and (not isinstance(r, list) or any(not isinstance(x, dict) for x in r)):
        p.append(f"{tag}: rows must be a list of dicts")
    return p


# ---- LayoutScore contract --------------------------------------------------
def validate_layout_score(out: Any, expect_criteria: Optional[set] = None) -> List[str]:
    """Check score_layout() output against the LayoutScore contract."""
    p: List[str] = []
    if not isinstance(out, dict):
        return [f"layout score is {type(out).__name__}, not dict"]
    for k in ("objective_scores", "criteria_scored", "provenance", "headline"):
        if k not in out:
            p.append(f"layout score missing top-level key '{k}'")
    obj = out.get("objective_scores", {})
    for which in ("cognitive", "wellbeing"):
        o = obj.get(which, {})
        sc = o.get("score")
        if sc is not None and not (0.0 <= float(sc) <= 1.0):
            p.append(f"objective {which} score {sc} out of [0,1]")
    cs = out.get("criteria_scored", {})
    if not isinstance(cs, dict):
        p.append("criteria_scored must be a dict")
    else:
        for cid, v in cs.items():
            if not (0.0 <= float(v) <= 1.0):
                p.append(f"criteria_scored[{cid}] = {v} out of [0,1]")
        if expect_criteria is not None:
            missing = expect_criteria - set(cs)
            if missing:
                p.append(f"criteria_scored missing {sorted(missing)}")
    # provenance must carry the non-additivity honesty caveat (RULE 0)
    cav = out.get("provenance", {}).get("caveat", "")
    if "INTERACTIONS UN-MODELLED" not in cav.upper():
        p.append("provenance.caveat must disclose the non-additivity (interactions un-modelled)")
    # a fit matrix + worst-served segment are the headline deliverable (when settings exist)
    if out.get("fit_matrix") is None:
        p.append("fit_matrix is None (the §5 headline deliverable)")
    if out.get("worst_served_segment") is None:
        p.append("worst_served_segment is None (min-not-mean binding constraint)")
    return p


# ---- AttributeResult contract (the Tier-A image attributes in attributes.py) --------------
def validate_attribute_result(res: Any, grid_shape: Optional[Tuple[int, int]] = None,
                              name: str = "", require_failure_modes: bool = False) -> List[str]:
    """Check an image attribute's AttributeResult (dataclass with .to_json()) against the
    contract. `require_failure_modes=False` for the pre-existing attributes (disclosure is
    a newer norm); True for new code."""
    p: List[str] = []
    tag = name or getattr(res, "key", "?")
    key = getattr(res, "key", None)
    if not isinstance(key, str) or not key:
        p.append(f"{tag}: missing/empty key")
    c = getattr(res, "confidence", None)
    if not isinstance(c, (int, float)) or not (0.0 <= float(c) <= 1.0):
        p.append(f"{tag}: confidence {c!r} not in [0,1]")
    m = getattr(res, "method", None)
    if not isinstance(m, str) or not m.strip():
        p.append(f"{tag}: method missing/empty")
    s = getattr(res, "scalar", None)
    if s is not None and (not isinstance(s, (int, float)) or not np.isfinite(s)):
        p.append(f"{tag}: scalar {s!r} not finite")
    f = getattr(res, "field", None)
    if f is not None:
        # a localized attribute field may be FULL-res (==image) or TILED (an integer
        # downscale, e.g. per-tile fractal/processing-load). Both are legal; a field
        # LARGER than the image, or non-2D, is not.
        if not isinstance(f, np.ndarray) or f.ndim < 2:
            p.append(f"{tag}: field is not a 2D+ ndarray")
        elif grid_shape is not None and (f.shape[0] > grid_shape[0] or f.shape[1] > grid_shape[1]):
            p.append(f"{tag}: field {f.shape[:2]} larger than image {grid_shape} (not a valid tiling)")
    fm = getattr(res, "failure_modes", None)
    if not isinstance(fm, list):
        p.append(f"{tag}: failure_modes not a list")
    elif require_failure_modes and len(fm) == 0:
        p.append(f"{tag}: failure_modes empty (new code must disclose limits)")
    # at least one of scalar/field/regions must carry a result
    if s is None and f is None and not getattr(res, "regions", None):
        p.append(f"{tag}: no scalar, field, or regions (empty result)")
    return p


# ---- geometry/plan output contracts --------------------------------------------------------
def validate_plangrid(pg, name: str = "PlanGrid") -> List[str]:
    p: List[str] = []
    grid = getattr(pg, "grid", None)
    if not isinstance(grid, np.ndarray):
        return [f"{name}: grid is not an ndarray"]
    bad = set(np.unique(grid)) - {0, 1, 2}
    if bad:
        p.append(f"{name}: grid has illegal cell values {bad} (allowed 0/1/2)")
    if not (isinstance(getattr(pg, "cell_m", None), (int, float)) and pg.cell_m > 0):
        p.append(f"{name}: cell_m {getattr(pg,'cell_m',None)!r} not positive")
    if (grid == 1).sum() == 0:
        p.append(f"{name}: no FREE cells")
    return p


# ---- the full scored-criteria set (C1-C24 minus C6 opportunity) ------------
FULL_SCORED_CRITERIA = {f"C{i}" for i in range(1, 25)} - {"C6"}
