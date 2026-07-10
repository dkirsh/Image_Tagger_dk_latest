"""ReflectionExposureAdapter — score how much a reflective interior shows a
person to themselves (self-exposure) and to others (seen-via-reflection),
emitted as cnfa.reflection.* attributes alongside the visual and acoustic banks.

Given a room polygon, its wall optical reflectances, and a viewpoint (the
gathering point), it runs the mirror-image construction and emits:

  * cnfa.reflection.self_exposure_index         — 0..1, strength of self-reflection here
  * cnfa.reflection.self_exposure               — raw reflectance*subtended sum
  * cnfa.reflection.self_image_count            — # surfaces returning a self-image
  * cnfa.reflection.nearest_self_image_distance — round-trip distance to nearest reflection (m)
  * cnfa.reflection.reflected_exposure          — share of observers who see you via a bounce

Reads from the frame: `reflection_corners` (polygon) OR `acoustic_corners`
(reused geometry), `viewpoint` (the person), and optionally
`reflection_materials` (float / preset / material name / per-edge list),
`reflection_observers` (public standpoints), `reflection_occluders` (interior
partitions as Surfaces), and `person_size`. No-ops on image-only frames. Owned /
permissive (pure geometry, NumPy only).
"""
from __future__ import annotations

from ..base import AnalyzerAdapter, License
from .reflection_exposure import annotate_reflection


class ReflectionExposureAdapter(AnalyzerAdapter):
    name = "reflection_exposure"
    tool = "cnfa-reflection(clean-room)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE
    enable_flag = "enable_reflection_exposure"
    requires = ()
    provides = (
        "cnfa.reflection.self_exposure",
        "cnfa.reflection.self_exposure_index",
        "cnfa.reflection.self_image_count",
        "cnfa.reflection.nearest_self_image_distance",
        "cnfa.reflection.reflected_exposure",
    )

    def _analyze(self, frame) -> None:
        corners = getattr(frame, "reflection_corners", None)
        if corners is None:
            corners = getattr(frame, "acoustic_corners", None)
        viewpoint = getattr(frame, "viewpoint", None)
        if corners is None or viewpoint is None:
            return
        materials = getattr(frame, "reflection_materials", 0.0)
        observers = getattr(frame, "reflection_observers", None)
        occluders = getattr(frame, "reflection_occluders", None)
        person_size = getattr(frame, "person_size", 1.7)
        bundle = annotate_reflection(corners, viewpoint, materials,
                                     observers=observers, occluders=occluders,
                                     person_size=person_size)
        for key, value in bundle.items():
            units = "m" if key.endswith("nearest_self_image_distance") else None
            self.emit(frame, key, value, units=units)
