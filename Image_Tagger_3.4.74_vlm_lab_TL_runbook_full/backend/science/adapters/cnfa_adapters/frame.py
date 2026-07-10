"""A minimal AnalysisFrame for running/testing adapters OUTSIDE the repo.

In the real Image Tagger pipeline, the frame is constructed by the pipeline and
carries precomputed buffers (gray_image, edges, segmentation, ...). For unit
tests and the `examples/run_all.py` demo we only need something that (a) exposes
an RGB image and (b) collects attributes. `StandaloneFrame` is that — and
because the adapters duck-type the frame (see base.get_rgb/get_gray/get_path),
they run against this identically to the way they'll run in the repo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np


@dataclass
class AttributeRecord:
    key: str
    value: Any
    meta: Dict[str, Any] = field(default_factory=dict)


class StandaloneFrame:
    def __init__(self, image_rgb: np.ndarray, image_path: str | None = None):
        self.image_rgb = np.ascontiguousarray(np.asarray(image_rgb)[:, :, :3].astype(np.uint8))
        self.image_path = image_path
        self.attributes: Dict[str, AttributeRecord] = {}

    # Mirrors the repo frame's writer, with metadata kwargs.
    def add_attribute(self, key: str, value: Any, **meta: Any) -> None:
        self.attributes[key] = AttributeRecord(key=key, value=value, meta=meta)

    # Convenience for tests / demo.
    def as_dict(self) -> Dict[str, Any]:
        return {k: r.value for k, r in self.attributes.items()}

    def records(self):
        return list(self.attributes.values())

    @classmethod
    def from_path(cls, path: str) -> "StandaloneFrame":
        from PIL import Image

        rgb = np.asarray(Image.open(path).convert("RGB"))
        return cls(rgb, image_path=path)
