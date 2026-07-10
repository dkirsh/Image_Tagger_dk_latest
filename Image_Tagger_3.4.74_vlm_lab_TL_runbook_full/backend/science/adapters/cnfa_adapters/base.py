"""Adapter base class and the frame contract.

The live Image Tagger pipeline uses a uniform analyzer pattern:

    class SomeAnalyzer:
        @staticmethod
        def analyze(frame):                       # reads precomputed buffers
            frame.add_attribute("cnfa.x.y", value) # writes results

`AnalyzerAdapter` is the same shape, plus four things the harvested
open-source tools need to be trustworthy and shippable:

  * a licence class (permissive / copyleft / non-commercial / research) that a
    config gate can enforce, so copyleft or NC-weight tools can never leak into
    a commercial build by accident;
  * provenance + confidence stamped on every attribute;
  * a declared list of `cnfa.*` keys the adapter fills (`provides`), so a test
    can check the registry stays in sync;
  * defensive frame access, so the very same adapter runs against the real
    repo `AnalysisFrame` *and* against the standalone frame used for testing
    outside the repo (see frame.py). It duck-types the frame rather than
    importing it.

To drop these into the repo: copy the `cnfa_adapters` package under
`backend/science/adapters/`, register each adapter behind its `enable_flag`
in `pipeline.py`, and move the keys it `provides` out of `STUB_FEATURE_KEYS`.
"""
from __future__ import annotations

import enum
import os
import tempfile
from typing import Any, Iterable, Optional

import numpy as np

from . import compat


class License(str, enum.Enum):
    """Commercial-use class for an adapter's upstream dependency + weights."""

    PERMISSIVE = "permissive"        # MIT / BSD / Apache — safe to ship
    COPYLEFT = "copyleft"            # GPL/AGPL — isolate, do not link into product
    NONCOMMERCIAL = "noncommercial"  # CC-BY-NC code or weights — research/eval only
    RESEARCH = "research"            # released for research; terms unclear/unset


# ----------------------------------------------------------------------------
# Frame access helpers — duck-typed so we don't depend on exact field names.
# ----------------------------------------------------------------------------
_RGB_ATTRS = ("original_image", "image_rgb", "rgb_image", "img_rgb", "image", "rgb")
_GRAY_ATTRS = ("gray_image", "image_gray", "img_gray", "gray")
_PATH_ATTRS = ("image_path", "path", "file_path", "filename", "source_path")


def get_rgb(frame: Any) -> np.ndarray:
    """Return an HxWx3 uint8 RGB array from whatever the frame exposes."""
    for name in _RGB_ATTRS:
        arr = getattr(frame, name, None)
        if arr is not None:
            arr = np.asarray(arr)
            if arr.ndim == 3 and arr.shape[2] >= 3:
                rgb = arr[:, :, :3]
                if rgb.dtype != np.uint8:
                    rgb = np.clip(rgb * (255.0 if rgb.max() <= 1.0 else 1.0), 0, 255).astype(np.uint8)
                return np.ascontiguousarray(rgb)
    # Fall back to a path we can open.
    path = get_path(frame, required=False)
    if path:
        from PIL import Image

        return np.ascontiguousarray(np.asarray(Image.open(path).convert("RGB")))
    raise ValueError("frame exposes no RGB image (looked for %s) or path" % (_RGB_ATTRS,))


def get_gray(frame: Any) -> np.ndarray:
    """Return an HxW uint8 grayscale array (writable), matching how the
    Aesthetics-Toolbox expects it: PIL 'L' conversion, range [0, 255]."""
    for name in _GRAY_ATTRS:
        arr = getattr(frame, name, None)
        if arr is not None:
            arr = np.asarray(arr)
            if arr.dtype != np.uint8:
                arr = np.clip(arr * (255.0 if arr.max() <= 1.0 else 1.0), 0, 255).astype(np.uint8)
            return compat.writable_gray(arr)
    # Derive from RGB the same way the toolbox does.
    from PIL import Image

    rgb = get_rgb(frame)
    gray = np.array(Image.fromarray(rgb).convert("L"))  # np.array => writable copy
    return gray


def get_path(frame: Any, required: bool = True) -> Optional[str]:
    """Return a filesystem path for tools (e.g. visual-clutter) that only take
    a filename. If the frame has none, materialise a temp PNG from the RGB
    array and cache it on the frame so repeated adapters reuse one file."""
    for name in _PATH_ATTRS:
        p = getattr(frame, name, None)
        if p and os.path.exists(p):
            return p
    cached = getattr(frame, "_cnfa_tmp_path", None)
    if cached and os.path.exists(cached):
        return cached
    try:
        from PIL import Image

        rgb = get_rgb(frame)
        fd, tmp = tempfile.mkstemp(suffix=".png", prefix="cnfa_frame_")
        os.close(fd)
        Image.fromarray(rgb).save(tmp)
        try:
            setattr(frame, "_cnfa_tmp_path", tmp)
        except Exception:
            pass
        return tmp
    except Exception:
        if required:
            raise
        return None


# ----------------------------------------------------------------------------
# Adapter base class
# ----------------------------------------------------------------------------
class AnalyzerAdapter:
    """Wrap one open-source tool as a repo-compatible analyzer.

    Subclasses set the class attributes and implement ``_analyze``; the public
    ``analyze(frame)`` handles emission, provenance and error isolation.
    """

    name: str = "adapter"
    tool: str = "unknown"
    tool_version: str = "0"
    license_class: License = License.PERMISSIVE
    enable_flag: str = "enable_adapter"
    provides: tuple[str, ...] = ()      # cnfa.* keys this adapter fills
    requires: tuple[str, ...] = ()      # importable module names it needs

    # ---- capability check -------------------------------------------------
    @classmethod
    def available(cls) -> bool:
        """True iff every required dependency imports."""
        import importlib

        for mod in cls.requires:
            try:
                importlib.import_module(mod)
            except Exception:
                return False
        return True

    # ---- emission ---------------------------------------------------------
    def emit(
        self,
        frame: Any,
        key: str,
        value: Any,
        confidence: float = 1.0,
        units: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> None:
        """Write one attribute with full provenance.

        Calls ``frame.add_attribute`` with rich metadata when the frame
        accepts kwargs, and degrades gracefully to a positional call for a
        minimal frame.
        """
        try:
            fval = float(value)
            # Several QIPs return NaN/Inf on degenerate inputs (e.g. a flat
            # image has no edges -> fractal dimension is undefined). Emitting a
            # NaN attribute would poison downstream scoring, so we skip it.
            if not np.isfinite(fval):
                return
        except (TypeError, ValueError):
            fval = value
        meta = dict(
            source=self.name,
            confidence=float(confidence),
            provenance="%s@%s" % (self.tool, self.tool_version),
            license_class=self.license_class.value,
        )
        if units:
            meta["units"] = units
        if extra:
            meta.update(extra)
        try:
            # Rich frame (StandaloneFrame) accepts arbitrary metadata kwargs.
            frame.add_attribute(key, fval, **meta)
        except TypeError:
            try:
                # Real repo AnalysisFrame: add_attribute(key, value, confidence=1.0)
                frame.add_attribute(key, fval, confidence=float(confidence))
            except TypeError:
                # Minimal signature: add_attribute(key, value)
                frame.add_attribute(key, fval)

    # ---- public entry point ----------------------------------------------
    def analyze(self, frame: Any) -> None:
        """Repo-compatible entry point. Never raises: a failing adapter must
        not take down the pipeline — it logs and emits nothing."""
        if not self.available():
            return
        try:
            self._analyze(frame)
        except Exception as exc:  # pragma: no cover - defensive
            import logging

            logging.getLogger("cnfa_adapters").warning(
                "adapter %s failed: %r", self.name, exc
            )

    def _analyze(self, frame: Any) -> None:  # pragma: no cover - abstract
        raise NotImplementedError


# ---- small normalisation helpers used by several adapters ------------------
def clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def logistic(x: float, midpoint: float, scale: float) -> float:
    """Map an unbounded raw value to (0, 1) with a documented midpoint/scale."""
    return float(1.0 / (1.0 + np.exp(-(x - midpoint) / scale)))
