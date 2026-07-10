"""Compatibility shims for third-party toolboxes.

Two of the permissive toolboxes were written against older library versions and
break on modern Pillow / NumPy read-only buffers. Importing this module (which
the adapters do) makes them run unmodified, so we never have to fork the
upstream source — a requirement for keeping the licence position clean
(we wrap, we do not modify).
"""
from __future__ import annotations

import numpy as np


def patch_pillow_antialias() -> None:
    """Pillow >= 10 removed ``Image.ANTIALIAS``; visual-clutter still calls it."""
    import PIL.Image as _PImage

    if not hasattr(_PImage, "ANTIALIAS"):
        # LANCZOS is the modern name for the same resampling filter.
        _PImage.ANTIALIAS = _PImage.Resampling.LANCZOS  # type: ignore[attr-defined]


def writable_gray(arr: np.ndarray) -> np.ndarray:
    """Return a writable, C-contiguous copy.

    ``np.asarray(PIL.Image)`` yields a read-only buffer, which Cython inner
    loops in scikit-image (graycomatrix) and others reject with
    ``ValueError: buffer source array is read-only``. A plain ``np.array``
    copy is writable.
    """
    if arr.flags.writeable and arr.flags.c_contiguous:
        return arr
    return np.array(arr, copy=True)


# Apply the Pillow shim on import — harmless if already patched or not needed.
patch_pillow_antialias()
