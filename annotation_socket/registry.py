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

MODEL_VERSION = "cnfa_algs-2026-07-19+seed1234+reliableA+reviewfix+codex2fix+codex3fix+m1prime+wave1+codexS0S2fix+clutterstack"   # sprint Reliable-A: V9,V2,V13,V1,V6,V7 + C01,C29   # bump on any algorithm/seed change

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
    _spec("cnfa.fluency.fractal_mid_d_band",       "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V9 (AMBER per Fable F5): declared trapezoid over whole-interior Canny box-count D. R2 "
          "does NOT prove a valid scale range (checkerboard D=0,R2=1); response constants are "
          "engineering. Scaling validity + labeled calibration owed before GREEN."),
    _spec("cnfa.fluency.spectral_slope_deviation", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V2 (AMBER + RENAMED per Fable F2): radial 1/f power-slope + mid-band residual. This is "
          "NOT the 2-D Penacchio-Wilkins discomfort metric (radial averaging discards the 2-D "
          "Fourier-energy distribution) and does NOT use FOV (removed). Scale-dependent; ship as "
          "a named spectral statistic only."),
    _spec("cnfa.fluency.edge_orientation_entropy", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V13 (AMBER per Fable F1, blank-image bug FIXED -> abstains on <40 edge px). 2nd-order "
          "is a first-neighbour proxy, NOT the Grebenkina pairwise-over-distances measure."),
    _spec("cnfa.geometry.contour_angularity", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V1 (AMBER per Fable F8): whole-image contour curve/corner statistic; NOT validated "
          "architectural valence (foliage/textiles/people counted). Dead lens-bow flag removed."),
    _spec("cnfa.fluency.grayscale_gabor_entropy_proxy", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V6 (AMBER + RENAMED per Fable F3): grayscale Gabor-magnitude entropy PROXY. NOT the "
          "published Rosenholtz Subband Entropy (no CIELab, no steerable pyramid, invented divisor). "
          "Clutter family - not a validated replacement (Decision D2)."),
    _spec("cnfa.fluency.local_congestion_proxy", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "V7 (AMBER + RENAMED per Fable F4): local-variance colour/contrast/orientation PROXY "
          "with declared arbitrary weights. NOT the published Feature Congestion. Clutter family."),
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

    # ---- Wave-1 classical-CV operators (Sprint COMP-CORRECT S2, 2026-07-19; Codex Section-D
    # keeps). ALL AMBER: computationally verified on fixtures + 9-interior smoke; construct
    # validation corpus-blocked. Constants declared in each result's extras.
    _spec("cnfa.light.luminance_gradient_contrast", "image_attr", IMAGE_ONLY, "replayable", "AMBER",
          "large-scale light architecture (sigma=diag/64); fullscale=60 calibrated on 9-interior smoke"),
    _spec("cnfa.light.shadow_softness", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "penumbra 10-90% width over chromaticity-stable edges; hard flag in px; abstains <25 edges"),
    _spec("cnfa.light.sun_patch_geometry", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "bright warm straight-boundary patch GEOMETRY — candidate, cannot prove sun"),
    _spec("cnfa.light.evening_ambience", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "McCamy CCT proxy + dimness + skew; AWB confound declared"),
    _spec("cnfa.light.temperature_mismatch", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "max weighted mired gap between chromaticity clusters; abstains on low saturation"),
    _spec("cnfa.light.spotlight_pool_geometry", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "top-hat pool geometry ONLY; social-exposure claim deferred to seat-input compound"),
    _spec("cnfa.light.dark_zone_map", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "dark zones map, NOT 'safety'; abstains on globally-dark input"),
    _spec("cnfa.material.texture_density", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "RESIDUAL micro-texture EXCLUDING structured/periodic pattern (wallpaper/ribbing read as structure and mask out — Codex S0S2 MED; periodic-texture stat is future work)"),
    _spec("cnfa.geometry.orderliness_alignment", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "LSD segment orientation order (segment-scale; V13 stays pixel-scale); abstains <20 segments"),
    # ---- clutter-stack layers (C-CLUT-2a/b/c, 2026-07-19: post-2007 clutter literature —
    # proto-object numerosity + interpretable structural/chromatic layers; see
    # docs/PAPER_NOTE_ROSENHOLTZ_CLUTTER_2007_AND_AFTER_2026-07-19.md). NO combined scalar:
    # layer weights for interiors are a corpus-time fit. All AMBER.
    _spec("cnfa.fluency.proto_object_count", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "mean-shift proto-object COUNT (Yu et al. 2014 family) — numerosity layer; PROXY"),
    _spec("cnfa.fluency.multiscale_gradient", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "MSG-inspired multi-scale Sobel mean (arXiv:2501.15890) — structural layer; named PROXY"),
    _spec("cnfa.fluency.multiscale_unique_color", "image_attr", IMAGE_ONLY, "replayable_tol", "AMBER",
          "MUC-inspired occupied color-bin fraction — chromatic-variety layer; named PROXY"),

    # street-noise acoustic operator (declared-input; docs/STREET_NOISE_ACOUSTIC_OPERATOR_SPEC)
    _spec("cnfa.acoustic.street_noise_intrusion", "plan_metric",
          frozenset({"outdoor_leq", "facade_spec"}), "replayable_tol", "AMBER",
          "facade-transmission energy model x ISO3382-3 masking; ABSTAINS without Leq_out + R'"),

    # ---- plan metrics computable from the INFERRED plan alone (Tier B chain) ----
    _spec("C1.visual_integration",  "plan_metric", PLAN, "replayable_tol", "AMBER",
          "VGA on inferred PlanGrid; heuristic geometry caps at AMBER"),
    _spec("C2.connectivity",        "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C3.intelligibility",     "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C4.wayfinding_load",     "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C13.setting_fit",        "plan_metric", PLAN, "replayable_tol", "AMBER"),
    _spec("C24.spatial_generosity", "plan_metric", PLAN, "replayable_tol", "AMBER",
          "2D openness-contrast proxy; true awe wants Tier-C height"),
    _spec("C01.triangulation_ignition", "plan_metric", PLAN, "replayable_tol", "AMBER",
          "COMPOUND: landmark_salience x C1 integration x co-location gate to the desire-line "
          "ridge; anchor off ridge -> ~0; registration-unconfident -> UNKNOWN. Own social field "
          "(excluded from score_layout aggregation)."),
    _spec("C29.stranded_amenity_index", "plan_metric", PLAN, "replayable_tol", "AMBER",
          "COMPOUND (C01 inverse): appeal x (1-co-location gate) x usable-surface; high = "
          "attractive amenity stranded OFF the desire line (redesign flag). Own diagnostic "
          "field (excluded from score_layout aggregation)."),

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

# Predicates allowed to return a SIGNAL-ABSENT abstention (Codex S0+S2 HIGH-2, 2026-07-19):
# applicable, worker ran, but the measured signal does not exist in this image (blank wall -> no
# shadow edges / no segments / no chromaticity). verify() accepts signal_absent ONLY for these ids
# AND only with non-empty absence evidence; everything else stays fail-closed UNKNOWN->RED.
MAY_LACK_SIGNAL = frozenset({
    "cnfa.fluency.edge_orientation_entropy",     # <40 edge px (F1)
    "cnfa.geometry.contour_angularity",          # no usable contours
    "cnfa.light.luminance_gradient_contrast",    # near-blank (std<2DN)
    "cnfa.light.shadow_softness",                # <25 accepted illumination edges
    "cnfa.light.evening_ambience",               # <100 usable bright-band px
    "cnfa.light.temperature_mismatch",           # saturation too low for chromaticity
    "cnfa.light.dark_zone_map",                  # globally dark image
    "cnfa.material.texture_density",             # structure mask leaves <20%
    "cnfa.geometry.orderliness_alignment",       # <20 segments
    "cnfa.fluency.proto_object_count",           # near-blank: nothing to segment
    "cnfa.fluency.multiscale_gradient",          # near-blank
})
