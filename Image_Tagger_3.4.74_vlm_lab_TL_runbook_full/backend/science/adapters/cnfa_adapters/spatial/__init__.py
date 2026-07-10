"""Space-side annotation: isovists and the visibility-graph measure set."""
from .isovist import (
    Plan,
    cast_rays,
    isovist_measures,
    line_of_sight,
    visibility_graph,
)
from .isovist_adapter import IsovistAdapter, annotate_plan
from .prospect_refuge import (
    ProspectRefugeAdapter,
    annotate_prospect_refuge,
    dead_ground_ratio,
    first_detection_distance,
    social_covisibility,
    visible_mask,
    visual_exposure,
)
from .acoustic_visibility import (
    audibility_field,
    eavesdrop_exposure,
    eavesdropping_zones,
    geodesic_sound_distance,
)
from .acoustic_pyroom import (
    MATERIAL_PRESETS,
    calibrated_fields,
    floor_grid,
    focusing_gain,
    intelligible_eavesdrop,
    sti_from_rir,
    sweep_gathering_points,
)
from .acoustic_adapter import AcousticPrivacyAdapter
from .reflection_exposure import (
    OPTICAL_REFLECTANCE,
    REFLECTIVE_PRESETS,
    Surface,
    annotate_reflection,
    optical_reflectance,
    seen_via_reflection,
    self_exposure,
    self_exposure_field,
    self_images,
    surfaces_from_corners,
)
from .reflection_adapter import ReflectionExposureAdapter

__all__ = [
    "Plan",
    "cast_rays",
    "isovist_measures",
    "line_of_sight",
    "visibility_graph",
    "IsovistAdapter",
    "annotate_plan",
    "ProspectRefugeAdapter",
    "annotate_prospect_refuge",
    "visible_mask",
    "dead_ground_ratio",
    "visual_exposure",
    "first_detection_distance",
    "social_covisibility",
    "audibility_field",
    "eavesdropping_zones",
    "eavesdrop_exposure",
    "geodesic_sound_distance",
    "calibrated_fields",
    "sti_from_rir",
    "focusing_gain",
    "intelligible_eavesdrop",
    "sweep_gathering_points",
    "floor_grid",
    "MATERIAL_PRESETS",
    "AcousticPrivacyAdapter",
    "Surface",
    "surfaces_from_corners",
    "optical_reflectance",
    "self_images",
    "self_exposure",
    "self_exposure_field",
    "seen_via_reflection",
    "annotate_reflection",
    "OPTICAL_REFLECTANCE",
    "REFLECTIVE_PRESETS",
    "ReflectionExposureAdapter",
]
