"""
annotation_socket.registry — the predicate registry the socket annotates against.

Every predicate declares, AS DATA (socket property 8: tiering/applicability is metadata the
controller routes on, not buried in code):

  id            stable key in the annotation record
  requires      the INPUTS the predicate needs beyond the image itself. An image-only unit
                satisfies only `frozenset()` and {"plan"} (plan is INFERABLE from the image,
                Tier B). Anything else absent from the unit -> ABSTAINED, with the missing
                input named — mechanically derived, auditable (amendment #1: tri-state).
  audit_class   "replayable"  = pure deterministic python: verify() re-executes and demands
                                an exact match (the strong, author-neutral mechanical check)
                "replayable_tol" = deterministic but float-accumulation-sensitive: replay
                                with tolerance
  tier_hint     evidence-quality ceiling declared by the pipeline itself: a predicate riding
                the HEURISTIC Tier-B geometry can never self-claim GREEN (amendment #2 —
                GREEN is an outcome of evidence, not a target).
  kind          "image_attr" (Tier A, evidence = image region/global) or
                "plan_metric" (evidence = derivation CHAIN image->geometry->plan->value).

The registry is the applicable-set oracle: coverage = 100% of predicates whose `requires`
are satisfied by the unit, each reaching SCORED or a verified ABSTAINED — never silence.
"""
from __future__ import annotations
from typing import Callable, Dict, FrozenSet, List

MODEL_VERSION = "cnfa_algs-2026-07-15+seed1234"   # bump on any algorithm/seed change

# input tokens a unit may carry beyond the image
#   plan            inferable from the image (Tier B) — always satisfiable
#   seats, glazing, amenities, collab_sources, focus_seats, destinations,
#   acoustic_params, control_zones, territory_spec, air_spec, nature_cells,
#   commons, retreats, height_field, spectral_daylight
IMAGE_ONLY: FrozenSet[str] = frozenset()
PLAN: FrozenSet[str] = frozenset({"plan"})


def _spec(id, kind, requires, audit_class, tier_hint, note=""):
    return {"id": id, "kind": kind, "requires": frozenset(requires),
            "audit_class": audit_class, "tier_hint": tier_hint, "note": note}


PREDICATES: List[Dict] = [
    # ---- Tier A image attributes (evidence: image region / global-image) ----
    _spec("cnfa.light.brightness_variance",        "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.fluency.edge_clarity_mean",        "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.fluency.symmetry_score_horizontal","image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.fluency.color_palette_entropy",    "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.fluency.processing_load_proxy",    "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.fractal_dimension",                "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("glare-risk",                            "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.light.warm_vs_cool_ratio",         "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    _spec("cnfa.cognitive.landmark_salience",      "image_attr", IMAGE_ONLY, "replayable", "GREEN"),
    # these three ride the heuristic plane segmentation -> evidence ceiling AMBER
    _spec("cnfa.spatial.enclosure_index",          "image_attr", IMAGE_ONLY, "replayable", "AMBER",
          "rides heuristic segment_planes (conf~0.45); panel: labels are colour clusters"),
    _spec("cnfa.spatial.prospect",                 "image_attr", IMAGE_ONLY, "replayable", "AMBER",
          "panel: glass-house inversion — view terminates at glazing"),
    _spec("acoustic_absorption_proxy",             "image_attr", IMAGE_ONLY, "replayable", "AMBER",
          "material table over heuristic planes"),
    _spec("cnfa.light.vertical_illuminance_proxy", "image_attr", IMAGE_ONLY, "replayable", "AMBER"),

    # ---- plan metrics computable from the INFERRED plan alone (Tier B chain) ----
    _spec("C1.visual_integration",  "plan_metric", PLAN, "replayable_tol", "AMBER",
          "VGA on inferred PlanGrid; heuristic geometry caps at AMBER"),
    _spec("C2.connectivity",        "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C3.intelligibility",     "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C4.wayfinding_load",     "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C13.setting_fit",        "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C24.spatial_generosity", "plan_metric", PLAN, "replayable_tol", "AMBER",
          "2D openness-contrast proxy; true awe wants Tier-C height"),

    # ---- predicates needing inputs an image does not contain (ABSTAIN on image-only units) ----
    _spec("C5.collaborator_proximity", "plan_metric", PLAN | {"seats", "collab_pairs"}, "replayable_tol", "GREEN"),
    _spec("C6.path_overlap",           "plan_metric", PLAN | {"seats", "destinations"}, "replayable_tol", "GREEN"),
    _spec("C7.focus_speech_privacy",   "plan_metric", PLAN | {"collab_sources", "focus_seats"}, "replayable_tol", "GREEN"),
    _spec("C8.distraction_distance",   "plan_metric", frozenset({"acoustic_params"}), "replayable", "GREEN",
          "floor-global acoustic spec; NEVER scored from defaults (panel S4)"),
    _spec("C9.view_equity",            "plan_metric", PLAN | {"seats", "glazing"}, "replayable_tol", "GREEN"),
    _spec("C10.daylight_proximity",    "plan_metric", PLAN | {"seats", "glazing"}, "replayable_tol", "AMBER",
          "geometric screen; certified melanopic needs spectral_daylight"),
    _spec("C11.prospect_refuge",       "plan_metric", PLAN | {"seats"}, "replayable_tol", "AMBER"),
    _spec("C12.crowding_risk",         "plan_metric", PLAN | {"seats"}, "replayable_tol", "AMBER"),
    _spec("C14.focus_collab_separation","plan_metric", PLAN | {"collab_sources", "focus_seats"}, "replayable_tol", "GREEN",
          "DERIVED from C1 x C7 — scoring it without C7 evidence is the fabrication regression"),
    _spec("C15.active_design",         "plan_metric", PLAN | {"seats", "amenities"}, "replayable_tol", "GREEN"),
    _spec("C16.territory",             "plan_metric", frozenset({"territory_spec"}), "replayable", "GREEN"),
    _spec("C17.local_control",         "plan_metric", frozenset({"control_zones"}), "replayable", "GREEN"),
    _spec("C18.air_quality",           "plan_metric", frozenset({"air_spec"}), "replayable", "GREEN"),
    _spec("C19.restoration_nature",    "plan_metric", PLAN | {"seats", "nature_cells"}, "replayable_tol", "AMBER"),
    _spec("C20.chronic_soundscape",    "plan_metric", PLAN | {"collab_sources"}, "replayable_tol", "AMBER"),
    _spec("C21.thermal",               "plan_metric", PLAN | {"seats", "glazing"}, "replayable_tol", "AMBER"),
    _spec("C22.circadian_contrast",    "plan_metric", PLAN | {"seats", "glazing"}, "replayable_tol", "AMBER"),
    _spec("C23.social_connectedness",  "plan_metric", PLAN | {"seats", "commons"}, "replayable_tol", "AMBER"),
]

BY_ID: Dict[str, Dict] = {p["id"]: p for p in PREDICATES}


def applicable(unit_inputs: FrozenSet[str]) -> List[Dict]:
    """Predicates whose requirements are satisfied. 'plan' is always satisfiable (Tier B
    inference from the image), so it is added to every unit's input set."""
    have = frozenset(unit_inputs) | {"plan"}
    return [p for p in PREDICATES if p["requires"] <= have]


def abstained(unit_inputs: FrozenSet[str]) -> List[Dict]:
    have = frozenset(unit_inputs) | {"plan"}
    return [p for p in PREDICATES if not (p["requires"] <= have)]
