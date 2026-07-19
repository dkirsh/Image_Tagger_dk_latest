"""
annotation_socket.annotator — the WORKER (socket properties 1,2,3,4,7).

Pull-driven: claims one unit (an image) from the controller-written queue, annotates it,
writes the record to quarantine/, emits events. It NEVER writes accepted/, control.jsonl,
verdicts.jsonl (the CPP [W:] boundary — enforced by cpp.stage.assert_can_write), and it
never self-assigns work (claim via O_EXCL).

Every predicate value is built ONLY through derivation.scored/abstain/unknown — the vision
trust chokepoint. Content-addressed: unit_id = sha256(image_bytes + MODEL_VERSION); a unit
already carrying a verdict or accepted output is skipped BEFORE claiming (zero redundant
work on re-run).
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
from typing import Dict, FrozenSet, List

sys.path.insert(0, "/home/claude/_control_deps")     # cpp library (sandbox vendored copy)
sys.path.insert(0, "/home/claude")                    # cnfa_algs
sys.path.insert(0, "/Users/davidusa/REPOS/_control")  # cpp library (Mac path)
from cpp import stage

from . import registry as R
from . import derivation as D

WORKER_ID = "cnfa-annotator"


# --------------------------------------------------------------------- content addressing
def unit_id_for(image_path: str) -> str:
    b = Path(image_path).read_bytes()
    return hashlib.sha256(b + R.MODEL_VERSION.encode()).hexdigest()[:16]


# --------------------------------------------------------------------- the annotation core
def _field_argmax_bbox(field, img_shape, tile: int = 3):
    """Honest image_region locator for a field-carrying attribute: the bbox (x0,y0,x1,y1)
    of the field's hottest tile, scaled to image coords."""
    import numpy as np
    f = np.nan_to_num(np.asarray(field, float))
    fh, fw = f.shape[:2]
    H, W = img_shape[:2]
    r, c = np.unravel_index(int(f.argmax()), f.shape[:2])
    sy, sx = H / fh, W / fw
    y0, x0 = int(max(0, (r - tile // 2) * sy)), int(max(0, (c - tile // 2) * sx))
    y1, x1 = int(min(H, (r + tile // 2 + 1) * sy)), int(min(W, (c + tile // 2 + 1) * sx))
    return [x0, y0, x1, y1]


def annotate_image(image_path: str, unit_inputs: FrozenSet[str] = frozenset(),
                   input_values: Dict | None = None) -> Dict:
    """Compute the annotation record for one image: geometry once, then every APPLICABLE
    predicate through the chokepoint; every inapplicable one ABSTAINED with the named
    missing inputs. Returns the quarantine-ready record."""
    import cv2, numpy as np
    import cnfa_algs as ca
    from cnfa_algs import attributes as A
    from cnfa_algs import reliable_attrs as RA
    from cnfa_algs import wave1_ops as W1
    from cnfa_algs import clutter_stack as CS
    from cnfa_algs import complexity_partition as CP
    from cnfa_algs import faithful_clutter as FC
    from cnfa_algs.plan import infer_plan_from_image, FREE
    from cnfa_algs import space_syntax as ss, setting_classifier as st, affordance as af

    from . import m1_prime as MP
    img = MP.load_for_m1p(image_path)   # SINGLE shared loader (Codex S0S2 MED-4: no inline duplicate)
    H, W = img.shape[:2]

    # ---- shared geometry (computed once; every plan metric cites it as upstream) ----
    vx, vy, vconf = ca.estimate_vanishing_point(img)
    planes, pconf = ca.segment_planes(img, (vx, vy))
    Z, _, dconf = ca.DepthProvider()(img, planes, (vx, vy))
    pg = infer_plan_from_image(img, planes, Z)
    gh = D.grid_hash(pg.grid)
    chain = [{"step": "vanishing_point", "value": [round(vx, 1), round(vy, 1)], "conf": round(vconf, 2)},
             {"step": "segment_planes", "signal": "kmeans-heuristic(seed1234)", "conf": round(pconf, 2)},
             {"step": "depth", "signal": "geometric_vp_fallback", "conf": round(dconf, 2)},
             {"step": "plan", "grid_hash": gh, "cell_m": round(pg.cell_m, 4),
              "conf": round(getattr(pg, "confidence", 0.4), 2)}]
    geom_conf = min(pconf, dconf, getattr(pg, "confidence", 0.4))

    def img_ev(res, kind_default="global_image"):
        """Evidence from an AttributeResult: region if it carries a field, else global."""
        if getattr(res, "field", None) is not None:
            return D.evidence_image("image_region", _field_argmax_bbox(res.field, (H, W)),
                                    res.method, res.confidence)
        return D.evidence_image(kind_default, "full_frame", res.method, res.confidence)

    def plan_ev(signal: str, conf: float):
        return D.evidence_image("plan_chain", {"grid_hash": gh, "free_cells": int((pg.grid == FREE).sum())},
                                signal, min(conf, geom_conf), upstream=chain)

    scores: List[Dict] = []
    have = frozenset(unit_inputs)

    # ---- Tier-A attributes ----
    attr_fns = {
        "cnfa.light.brightness_variance":         lambda: A.brightness_variance(img),
        "cnfa.fluency.edge_clarity_mean":         lambda: A.edge_clarity(img),
        "cnfa.fluency.symmetry_score_horizontal": lambda: A.symmetry_horizontal(img),
        "cnfa.fluency.color_palette_entropy":     lambda: A.palette_entropy(img),
        "cnfa.fluency.processing_load_proxy":     lambda: A.processing_load(img),
        "cnfa.fractal_dimension":                 lambda: fractal(),
        "glare-risk":                             lambda: A.glare_risk(img),
        "cnfa.light.warm_vs_cool_ratio":          lambda: A.warmth_ratio(img),
        "cnfa.cognitive.landmark_salience":       lambda: A.landmark_salience(img),
        "cnfa.spatial.enclosure_index":           lambda: A.enclosure_index(img, planes, Z),
        "cnfa.spatial.prospect":                  lambda: A.prospect(img, planes, Z),
        "acoustic_absorption_proxy":              lambda: A.acoustic_absorption(img, planes, Z),
        "cnfa.light.vertical_illuminance_proxy":  lambda: A.vertical_illuminance_proxy(img, planes),
        "cnfa.fluency.spectral_slope_deviation":  lambda: RA.spectral_discomfort_deviation(img),
        "cnfa.fluency.edge_orientation_entropy":  lambda: RA.edge_orientation_entropy(img),
        "cnfa.geometry.contour_angularity":       lambda: RA.contour_angularity_index(img),
        "cnfa.fluency.grayscale_gabor_entropy_proxy": lambda: RA.subband_entropy_clutter(img),
        "cnfa.fluency.local_congestion_proxy":    lambda: RA.feature_congestion_clutter(img),
        # Wave-1 classical-CV operators (Sprint COMP-CORRECT S2, 2026-07-19) — all AMBER
        "cnfa.light.luminance_gradient_contrast": lambda: W1.luminance_gradient_contrast(img),
        "cnfa.light.shadow_softness":             lambda: W1.shadow_softness(img),
        "cnfa.light.sun_patch_geometry":          lambda: W1.sun_patch_geometry(img),
        "cnfa.light.evening_ambience":            lambda: W1.evening_ambience(img),
        "cnfa.light.temperature_mismatch":        lambda: W1.temperature_mismatch(img),
        "cnfa.light.spotlight_pool_geometry":     lambda: W1.spotlight_pool_geometry(img),
        "cnfa.light.dark_zone_map":               lambda: W1.dark_zone_map(img),
        "cnfa.material.texture_density":          lambda: W1.texture_density(img),
        "cnfa.geometry.orderliness_alignment":    lambda: W1.orderliness_alignment(img),
        # clutter-stack layers (C-CLUT-2a/b/c, 2026-07-19) — all AMBER, profile-only (no blend)
        "cnfa.fluency.proto_object_count":        lambda: CS.proto_object_count(img),
        "cnfa.fluency.multiscale_gradient":       lambda: CS.multiscale_gradient(img),
        "cnfa.fluency.multiscale_unique_color":   lambda: CS.multiscale_unique_color(img),
        # semantic complexity partition (regionalized signed complexity, DT-1 fix)
        "cnfa.fluency.complexity_partition":      lambda: CP.complexity_partition(img),
        # FAITHFUL V6/V7 (adjudicated reference port; proxies stay per Q3)
        "cnfa.fluency.feature_congestion":        lambda: FC.feature_congestion_faithful(img),
        "cnfa.fluency.subband_entropy":           lambda: FC.subband_entropy_faithful(img),
    }
    # ---- plan metrics from the inferred plan alone ----
    def _vga():
        return ss.vga_metrics(pg, stride=3)
    _vga_cache = {}
    def vga():
        if "v" not in _vga_cache:
            _vga_cache["v"] = _vga()
        return _vga_cache["v"]

    _frac_cache = {}
    def fractal():
        if "f" not in _frac_cache:
            _frac_cache["f"] = A.fractal_dimension_local(img)
        return _frac_cache["f"]

    plan_fns = {
        "C1.visual_integration":  lambda: (vga()["extras"]["integration_norm"], vga()["method"], vga()["confidence"]),
        "C2.connectivity":        lambda: (vga()["extras"]["connectivity_norm"], vga()["method"], vga()["confidence"]),
        "C3.intelligibility":     lambda: (vga()["scalar"], vga()["method"], vga()["confidence"]),
        "C4.wayfinding_load":     lambda: (lambda w: (w["scalar"], w["method"], w["confidence"]))(ss.wayfinding_load(pg, stride=3)),
        "C13.setting_fit":        lambda: (lambda f: (f["scalar"], f["method"], f["confidence"]))(st.segment_fit(st.classify_settings(pg))),
        "C24.spatial_generosity": lambda: (lambda g: (g["scalar"], g["method"], g["confidence"]))(af.spatial_generosity(pg)),
    }

    from .predicates import triangulation as TRI
    from .predicates import stranded_amenity as STR
    geom_conf_c = min(pconf, dconf, getattr(pg, "confidence", 0.4))
    compound_fns = {
        "C01.triangulation_ignition":
            lambda: TRI.compute(img, planes, Z, pg, vga(), geom_conf_c, chain),
        "C29.stranded_amenity_index":
            lambda: STR.compute(img, planes, Z, pg, vga(), geom_conf_c, chain),
    }
    from .predicates import fractal_band as FB
    compound_fns["cnfa.fluency.fractal_mid_d_band"] = lambda: FB.compute(img, fractal())

    # street-noise (declared-input): tokens name the inputs; VALUES ride input_values (Codex S0S2
    # HIGH-1 — a token without its value is a unit-construction error -> UNKNOWN, fail closed).
    def _street_noise():
        from cnfa_algs.street_noise import street_noise_fields
        iv = input_values or {}
        leq = iv.get("outdoor_leq")
        fs = iv.get("facade_spec") or {}
        missing = [k for k, v in [("outdoor_leq", leq), ("facade_spec.facade_row", fs.get("facade_row")),
                                  ("facade_spec.Rp", fs.get("Rp"))] if v is None]
        if missing:
            return D.unknown("cnfa.acoustic.street_noise_intrusion",
                             f"declared_input_value_missing:{','.join(missing)}")
        nc = pg.grid.shape[1]
        rp_in = fs["Rp"]
        Rp = np.full(nc, float(rp_in)) if np.isscalar(rp_in) else np.asarray(rp_in, float)
        if Rp.shape[0] != nc:
            return D.unknown("cnfa.acoustic.street_noise_intrusion",
                             f"facade_spec.Rp_length_{Rp.shape[0]}_vs_grid_cols_{nc}")
        r = street_noise_fields(pg, int(fs["facade_row"]), Rp,
                                fs.get("alpha", 0.10), outdoor_leq=float(leq))
        if r.get("status") != "scored":
            return D.unknown("cnfa.acoustic.street_noise_intrusion",
                             f"street_noise:{r.get('status')}")
        ev = plan_ev(r["method"], r["confidence"])
        rec = D.scored("cnfa.acoustic.street_noise_intrusion", r["scalar"], ev, "AMBER", (H, W))
        rec["extras"] = r["extras"]          # declared constants + cell landmarks for audit
        return rec
    compound_fns["cnfa.acoustic.street_noise_intrusion"] = _street_noise

    for spec in R.PREDICATES:
        pid = spec["id"]
        if not (spec["requires"] <= (have | {"plan"})):
            scores.append(D.abstain(pid, spec["requires"] - (have | {"plan"})))
            continue
        try:
            if pid in attr_fns:
                res = attr_fns[pid]()
                if res.scalar is None:
                    # signal ABSENT on this image (Codex S0S2 HIGH-2): applicable + worker ran,
                    # but the measured signal does not exist here. Registry-gated abstention
                    # subtype with the operator's own absence evidence; never a number.
                    if pid in R.MAY_LACK_SIGNAL:
                        scores.append(D.abstain_signal(pid, res.method,
                                                       getattr(res, "extras", None) or {}))
                    else:
                        scores.append(D.unknown(pid, f"signal_undefined:{res.method[:60]}"))
                else:
                    scores.append(D.scored(pid, res.scalar, img_ev(res), spec["tier_hint"], (H, W)))
            elif pid in plan_fns:
                val, signal, conf = plan_fns[pid]()
                scores.append(D.scored(pid, val, plan_ev(signal, conf), spec["tier_hint"], (H, W)))
            elif pid in compound_fns:
                scores.append(compound_fns[pid]())      # full scored/zero/unknown record
            else:
                # applicable per requirements but no binding on an image-only unit path
                scores.append(D.unknown(pid, "no_binding_for_supplied_inputs"))
        except Exception as e:
            scores.append(D.unknown(pid, f"compute_failed:{type(e).__name__}"))

    # ---- M1' sufficient-statistic emission (S0, 2026-07-19): every SCORED predicate with a
    # bound audit_class ships its pre-scalar signature so verify can replay the METHOD, not
    # just the number. Emission failure is recorded, never silently dropped.
    from . import m1_prime as MP
    for s in scores:
        if s["status"] == D.SCORED and s["predicate"] in MP.M1P_BINDINGS:
            ac, mp_params = MP.M1P_BINDINGS[s["predicate"]]
            try:
                s["m1p"] = MP.emit(ac, img, **mp_params)
            except Exception as e:
                s["m1p"] = {"audit_class": ac, "error": f"emit_failed:{type(e).__name__}"}

    n_scored = sum(1 for s in scores if s["status"] == D.SCORED)
    n_abst = sum(1 for s in scores if s["status"] == D.ABSTAINED)
    n_unknown = len(scores) - n_scored - n_abst
    return {
        "unit_id": unit_id_for(image_path),
        "image_path": image_path,
        "image_sha256": hashlib.sha256(Path(image_path).read_bytes()).hexdigest(),
        "model_version": R.MODEL_VERSION,
        "unit_inputs": sorted(have),
        "input_values": input_values or {},
        "geometry_chain": chain,
        "scores": scores,
        "coverage": {"applicable": n_scored + n_unknown, "scored": n_scored,
                     "abstained": n_abst, "unknown": n_unknown,
                     "total_registry": len(R.PREDICATES)},
        "worker": WORKER_ID, "ts_ms": int(time.time() * 1000),
    }


# --------------------------------------------------------------------- the pull loop
def run_worker(stage_dir: str, max_units: int = 10) -> Dict:
    """Claim->annotate->quarantine->events, until the queue is drained. Skips units already
    verdicted/accepted BEFORE claiming (content-addressed idempotency)."""
    paths = stage.ensure_stage(stage_dir)
    done_units = stage.accepted_units(paths) | set(stage.verdict_by_unit(paths))
    processed, skipped = [], []
    for _ in range(max_units):
        unit = None
        for u in stage.read_queue_units(paths):
            uid = u["unit_id"]
            if uid in done_units or uid in stage.claimed_units(paths):
                if uid in done_units and uid not in skipped:
                    skipped.append(uid)
                continue
            if stage.claim(paths, uid, WORKER_ID):
                unit = u
                break
        if unit is None:
            break
        uid = unit["unit_id"]
        stage.emit_event(paths, uid, WORKER_ID, "started")
        try:
            rec = annotate_image(unit["image_path"], frozenset(unit.get("inputs", [])))
            if rec["unit_id"] != uid:
                stage.emit_event(paths, uid, WORKER_ID, "failed",
                                 reason=f"content-address mismatch {rec['unit_id']}!={uid}")
                continue
            stage.emit_event(paths, uid, WORKER_ID, "heartbeat",
                             note=f"scored={rec['coverage']['scored']}")
            stage.write_quarantine(paths, uid, rec, worker=WORKER_ID)
            stage.emit_event(paths, uid, WORKER_ID, "done",
                             coverage=rec["coverage"])
            processed.append(uid)
        except Exception as e:
            stage.emit_event(paths, uid, WORKER_ID, "failed", reason=repr(e)[:200])
    return {"processed": processed, "skipped_content_addressed": skipped}


# --------------------------------------------------------------- Tier-A-only GREEN view (D1)
def tier_a_view(record: Dict) -> Dict:
    """Decision D1: a GREEN-eligible view of a full annotation record containing ONLY the
    GREEN-ceiling image-attribute predicates (no inferred-plan metrics). Pure filter — no new
    compute, no new failure mode; the unit can now verdict GREEN because every predicate in it
    rides no heuristic geometry. Stamped `mode='tier_a_only'` so a consumer can never confuse it
    with a full (plan-inclusive) record."""
    green_img = {p["id"] for p in R.PREDICATES
                 if p["kind"] == "image_attr" and p["tier_hint"] == "GREEN"}
    kept = [s for s in record["scores"] if s["predicate"] in green_img]
    n_scored = sum(1 for s in kept if s["status"] == D.SCORED)
    n_abst = sum(1 for s in kept if s["status"] == D.ABSTAINED)
    n_unknown = len(kept) - n_scored - n_abst
    out = dict(record)
    out["mode"] = "tier_a_only"
    out["scores"] = kept
    out["coverage"] = {"applicable": n_scored + n_unknown, "scored": n_scored,
                       "abstained": n_abst, "unknown": n_unknown, "total_registry": len(green_img)}
    return out
