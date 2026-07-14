"""
cnfa_algs.core — result schema and rendering utilities.

Every attribute algorithm returns an AttributeResult:
  key         canonical attribute key (matches feature_stubs.py naming)
  scalar      global value (float) or None
  field       optional HxW float32 map in [0,1] (dense localization)
  regions     optional list of {"kind": bbox|polygon|mask_ref, "coords":..., "label":..., "value":...}
  confidence  0..1
  method      short string naming the algorithm + tier (M1/M2/M2.5/M3)
  failure_modes  list[str]
  extras      dict of inspectable components (for composites)

Rendering: heatmap overlays with iso-contours (the "topographic curves"),
region overlays, and a gallery compositor.
"""
from __future__ import annotations
from dataclasses import dataclass, field as dfield
from typing import Any, Dict, List, Optional
import json
import numpy as np
import cv2


@dataclass
class AttributeResult:
    key: str
    scalar: Optional[float] = None
    field: Optional[np.ndarray] = None
    regions: List[Dict[str, Any]] = dfield(default_factory=list)
    confidence: float = 0.5
    method: str = ""
    failure_modes: List[str] = dfield(default_factory=list)
    extras: Dict[str, Any] = dfield(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "scalar": None if self.scalar is None else round(float(self.scalar), 4),
            "has_field": self.field is not None,
            "regions": _jsonable(self.regions),
            "confidence": round(float(self.confidence), 2),
            "method": self.method,
            "failure_modes": self.failure_modes,
            "extras": _jsonable(self.extras),
        }


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return round(float(x), 4)
    if isinstance(x, np.ndarray):
        return f"<array {x.shape}>"
    if isinstance(x, float):
        return round(x, 4)
    return x


# ---------------------------------------------------------------- rendering

def normalize01(f: np.ndarray) -> np.ndarray:
    f = f.astype(np.float32)
    lo, hi = np.nanpercentile(f, 2), np.nanpercentile(f, 98)
    if hi - lo < 1e-9:
        return np.zeros_like(f)
    return np.clip((f - lo) / (hi - lo), 0, 1)


def heatmap_overlay(img_bgr: np.ndarray, field01: np.ndarray,
                    alpha: float = 0.45, contours: int = 6,
                    cmap: int = cv2.COLORMAP_TURBO) -> np.ndarray:
    """Blend a [0,1] field over the image and draw iso-contours (topo curves)."""
    H, W = img_bgr.shape[:2]
    f = cv2.resize(field01.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    f = np.nan_to_num(f, nan=0.0)
    hm = cv2.applyColorMap((f * 255).astype(np.uint8), cmap)
    out = cv2.addWeighted(img_bgr, 1 - alpha, hm, alpha, 0)
    # iso-contours
    for lev in np.linspace(0.15, 0.9, contours):
        mask = (f >= lev).astype(np.uint8)
        cs, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, cs, -1, (255, 255, 255), 1)
    return out


def region_overlay(img_bgr: np.ndarray, regions: List[Dict[str, Any]],
                   color=(0, 220, 60)) -> np.ndarray:
    out = img_bgr.copy()
    for r in regions:
        if r["kind"] == "bbox":
            x, y, w, h = [int(v) for v in r["coords"]]
            cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
            label = r.get("label", "")
            if label:
                cv2.putText(out, label, (x, max(12, y - 4)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
        elif r["kind"] == "polygon":
            pts = np.array(r["coords"], np.int32).reshape(-1, 1, 2)
            cv2.polylines(out, [pts], True, color, 2)
        elif r["kind"] == "line":
            (x1, y1, x2, y2) = [int(v) for v in r["coords"]]
            cv2.line(out, (x1, y1), (x2, y2), r.get("color", color), 2)
    return out


def mask_overlay(img_bgr: np.ndarray, label_map: np.ndarray,
                 palette: Dict[int, tuple], alpha: float = 0.45,
                 legend: Optional[Dict[int, str]] = None) -> np.ndarray:
    H, W = img_bgr.shape[:2]
    lm = cv2.resize(label_map.astype(np.int32), (W, H), interpolation=cv2.INTER_NEAREST)
    color = np.zeros_like(img_bgr)
    for k, c in palette.items():
        color[lm == k] = c
    out = cv2.addWeighted(img_bgr, 1 - alpha, color, alpha, 0)
    if legend:
        y = 16
        for k, name in legend.items():
            cv2.rectangle(out, (6, y - 10), (18, y + 2), palette.get(k, (255, 255, 255)), -1)
            cv2.putText(out, name, (24, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (255, 255, 255), 1, cv2.LINE_AA)
            y += 16
    return out


def annotate_title(img: np.ndarray, title: str, sub: str = "") -> np.ndarray:
    out = img.copy()
    bar = np.zeros((34 if sub else 22, out.shape[1], 3), np.uint8)
    cv2.putText(bar, title, (6, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 1, cv2.LINE_AA)
    if sub:
        cv2.putText(bar, sub, (6, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (170, 200, 255), 1, cv2.LINE_AA)
    return np.vstack([bar, out])


def gallery(tiles: List[np.ndarray], cols: int = 3, pad: int = 6) -> np.ndarray:
    """Compose equally-resized tiles into a grid."""
    if not tiles:
        return np.zeros((10, 10, 3), np.uint8)
    h = max(t.shape[0] for t in tiles)
    w = max(t.shape[1] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, w - t.shape[1],
                                cv2.BORDER_CONSTANT, value=(20, 20, 20)) for t in tiles]
    rows = []
    for i in range(0, len(tiles), cols):
        row = tiles[i:i + cols]
        while len(row) < cols:
            row.append(np.full((h, w, 3), 20, np.uint8))
        rows.append(np.hstack([cv2.copyMakeBorder(t, pad, pad, pad, pad,
                    cv2.BORDER_CONSTANT, value=(20, 20, 20)) for t in row]))
    return np.vstack(rows)


def save_results_json(results: List[AttributeResult], path: str, meta: Optional[dict] = None):
    payload = {"meta": meta or {}, "attributes": [r.to_json() for r in results]}
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
