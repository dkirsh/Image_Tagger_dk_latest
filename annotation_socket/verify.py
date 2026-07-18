"""
annotation_socket.verify — the INDEPENDENT GATE (socket properties 5,6; CPP GATE verbs).

Mechanical-primary, LLM-advisory (SPEC-2). This module is the MECHANICAL layer and it IS
the decision; the ≠-mind inference judge ("does the score follow from the region?") is a
separate, advisory stage run by a different mind on AMBER units — never by the author.

Mechanical checks, in order (each producing evidence in the verdict):
  M1 REPLAY        re-derive every SCORED value from the image bytes and demand a match
                   (exact for audit_class=replayable, |d|<=0.02 for replayable_tol). A
                   fabricated/defaulted number cannot survive replay — this is the
                   author-neutral core: it checks the WORLD, not the author's assertions.
  M2 EVIDENCE      every SCORED ships valid evidence (cited image region exists in-bounds;
                   plan_chain carries grid_hash + upstream geometry).
  M3 DEPENDENCY    a SCORED value whose registry `requires` are NOT in the unit's inputs is
                   a FABRICATION (the score_layout regression, structurally: C14 scored
                   without C7 evidence, C8 scored without acoustic_params -> RED).
  M4 ABSTENTION    every ABSTAINED names missing inputs that are (a) genuinely required by
                   the registry and (b) genuinely absent from the unit — you cannot launder
                   a failure as an abstention.
  M5 COVERAGE      every registry predicate appears exactly once; every applicable one is
                   SCORED (UNKNOWN or missing -> RED); coverage is over the APPLICABLE set.

Tiering (declared as data, CPP property 8):
  RED    any fabrication / invalid evidence / replay mismatch / UNKNOWN / coverage gap
  AMBER  all mechanical checks pass but evidence quality is capped (tier_hint AMBER —
         heuristic Tier-B geometry) or confidence < 0.6  -> awaits the ≠-mind judge
  GREEN  all mechanical checks pass, tier_hint GREEN, confidence >= 0.6
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, "/home/claude/_control_deps")
sys.path.insert(0, "/Users/davidusa/REPOS/_control")
from cpp import stage

from . import registry as R
from . import derivation as D

CHECKER_ID = "verify-mechanical"        # != cnfa-annotator (I1 by topology)
TOL = 0.02


def _replay(record: Dict) -> Dict[str, float]:
    """Independent re-derivation: recompute the annotation from the image bytes with the
    pinned model version. Deterministic (S2 seeding), so a genuine score matches."""
    from .annotator import annotate_image
    fresh = annotate_image(record["image_path"], frozenset(record.get("unit_inputs", [])))
    return {s["predicate"]: s["value"] for s in fresh["scores"] if s["status"] == D.SCORED}


def verify_record(record: Dict, *, replay: bool = True) -> Tuple[str, Dict]:
    """Run M1-M5. Returns (tier, evidence_dict). Pure over its inputs + one replay run."""
    problems: List[str] = []
    ambers: List[str] = []
    have = frozenset(record.get("unit_inputs", [])) | {"plan"}
    scores = {s["predicate"]: s for s in record.get("scores", [])}

    # mode-aware expected set (Decision D1): a `tier_a_only` view is expected to carry ONLY the
    # GREEN image-attribute predicates, so coverage is checked against that subset, not the full
    # registry. Every other mode expects the full registry.
    if record.get("mode") == "tier_a_only":
        expected_specs = [p for p in R.PREDICATES
                          if p["kind"] == "image_attr" and p["tier_hint"] == "GREEN"]
    else:
        expected_specs = list(R.PREDICATES)

    # M5a: coverage — every EXPECTED predicate present exactly once
    if len(record.get("scores", [])) != len(scores):
        problems.append("duplicate predicate entries")
    expected_ids = {p["id"] for p in expected_specs}
    missing = [p["id"] for p in expected_specs if p["id"] not in scores]
    if missing:
        problems.append(f"coverage_gap:missing={missing[:5]}{'...' if len(missing) > 5 else ''}")
    extra = [pid for pid in scores if pid not in expected_ids]
    if extra:
        problems.append(f"unexpected_predicate:{extra[:3]}")   # a plan metric in a Tier-A view

    replay_vals = _replay(record) if replay and not problems else {}

    for spec in expected_specs:
        pid = spec["id"]
        s = scores.get(pid)
        if s is None:
            continue
        applicable = spec["requires"] <= have
        st = s["status"]

        if st == D.SCORED:
            # M3 dependency/fabrication: scored without its required inputs
            if not applicable:
                problems.append(f"FABRICATION:{pid} scored but requires "
                                f"{sorted(spec['requires'] - have)} absent from unit")
                continue
            # M2 evidence validity
            ev = s.get("evidence")
            if not isinstance(ev, dict) or ev.get("kind") not in ("image_region", "global_image", "plan_chain"):
                problems.append(f"EVIDENCE:{pid} missing/invalid evidence")
                continue
            if ev["kind"] == "plan_chain" and not (isinstance(ev.get("locator"), dict)
                                                   and ev["locator"].get("grid_hash") and ev.get("upstream")):
                problems.append(f"EVIDENCE:{pid} plan_chain lacks grid_hash/upstream")
                continue
            # M1 replay
            if replay:
                rv = replay_vals.get(pid)
                if rv is None:
                    problems.append(f"REPLAY:{pid} not reproducible from image")
                    continue
                tol = 0.0 if spec["audit_class"] == "replayable" else TOL
                if abs(rv - s["value"]) > tol + 1e-9:
                    problems.append(f"REPLAY:{pid} mismatch claimed={s['value']} replay={rv}")
                    continue
            # tiering
            if spec["tier_hint"] == "AMBER" or ev.get("confidence", 0) < 0.6:
                ambers.append(pid)
        elif st == D.ABSTAINED:
            # M4 abstention audit
            if applicable:
                problems.append(f"ABSTENTION_LAUNDERING:{pid} abstained though applicable")
            else:
                claimed = set(s.get("missing_inputs", []))
                actual = set(spec["requires"] - have)
                if claimed != actual:
                    problems.append(f"ABSTENTION:{pid} claims missing={sorted(claimed)} actual={sorted(actual)}")
        else:  # UNKNOWN
            problems.append(f"UNKNOWN:{pid} reason={s.get('reason')}")

    tier = "RED" if problems else ("AMBER" if ambers else "GREEN")
    n_scored = sum(1 for s in scores.values() if s["status"] == D.SCORED)
    return tier, {"checker": CHECKER_ID, "problems": problems, "amber_predicates": ambers,
                  "n_scored": n_scored, "replayed": bool(replay),
                  "mechanical_primary": True,
                  "note": "AMBER awaits the ≠-mind inference judge (advisory); RED is final unless overridden by David"}


def run_checker(stage_dir: str, *, replay: bool = True) -> Dict:
    """The GATE loop: verdict every quarantined-unverdicted unit; GREEN -> accepted/ (the
    controller-role move), AMBER awaits adjudication, RED stays quarantined."""
    paths = stage.ensure_stage(stage_dir)
    verdicts = stage.verdict_by_unit(paths)
    out = {"GREEN": [], "AMBER": [], "RED": []}
    for qf in sorted(paths.quarantine.glob("*.json")):
        uid = qf.stem
        if uid in verdicts:
            continue
        wrapper = json.loads(qf.read_text())
        record = wrapper.get("output", wrapper)   # cpp.stage envelope
        tier, evidence = verify_record(record, replay=replay)
        stage.write_verdict(paths, uid, tier, evidence, checker_id=CHECKER_ID)
        if tier == "GREEN":
            unit = next((u for u in stage.read_queue_units(paths) if u["unit_id"] == uid), {"unit_id": uid})
            stage.accept_output(paths, unit, record, controller_id="controller")
        out[tier].append(uid)
    return out
