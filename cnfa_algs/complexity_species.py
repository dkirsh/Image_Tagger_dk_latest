"""Complexity-species hypotheses and active-learning selection queues.

These values are early image-computable hypotheses for human review. They are
not answer keys and, until human calibration exists, are not calibrated
probabilities. Late or observer-dependent species explicitly abstain.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import cv2
import numpy as np
from PIL import Image


HYPOTHESIS_SCHEMA = "cnfa.complexity-species-hypotheses/v1"
QUEUE_SCHEMA = "cnfa.complexity-selection-queues/v1"
HANDOFF_SCHEMA = "cnfa.complexity-species-handoff/v1"
MODEL_VERSION = "complexity-species-proxy-v2"

SPECIES_CONTRACT: dict[str, dict[str, Any]] = {
    "surface_density": {
        "operation": "visual_search_crowding",
        "stage": "early",
        "channel": "both",
        "image_computable": True,
        "observer_dependence": "low",
    },
    "arrangement_disorder": {
        "operation": "legibility_wayfinding",
        "stage": "early",
        "channel": "cognitive",
        "image_computable": True,
        "observer_dependence": "medium",
    },
    "variety": {
        "operation": "encoding_interest",
        "stage": "early",
        "channel": "cognitive",
        "image_computable": True,
        "observer_dependence": "medium",
    },
    "textural_discomfort": {
        "operation": "comfort_stress",
        "stage": "early",
        "channel": "affective",
        "image_computable": True,
        "observer_dependence": "low",
    },
    "semantic_incongruity": {
        "operation": "scene_comprehension",
        "stage": "late",
        "channel": "cognitive",
        "image_computable": False,
        "observer_dependence": "medium",
    },
    "concealed_order": {
        "operation": "task_fit_legibility",
        "stage": "late",
        "channel": "both",
        "image_computable": False,
        "observer_dependence": "high",
    },
}

_BASE_CONFIDENCE = {
    "surface_density": 0.45,
    "arrangement_disorder": 0.25,
    "variety": 0.35,
    "textural_discomfort": 0.45,
}


class ComplexityContractError(ValueError):
    """Raised when a species or handoff record violates the v1 contract."""


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 6)


def _gray256(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ComplexityContractError("image must be a non-empty numpy array")
    if image.ndim == 2:
        gray = image
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.ndim == 3 and image.shape[2] in (3, 4):
        bgr = image[:, :, :3]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    else:
        raise ComplexityContractError("image must be grayscale, BGR, or BGRA")
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    gray = cv2.resize(gray, (256, 256), interpolation=cv2.INTER_AREA)
    rgb = cv2.resize(rgb, (256, 256), interpolation=cv2.INTER_AREA)
    return gray, rgb


def _contrast_energy(gray: np.ndarray) -> float:
    """Cowork reference primitive: mean local contrast at three scales."""
    g = gray.astype(np.float32)
    energy = 0.0
    for kernel in (3, 7, 15):
        mean = cv2.blur(g, (kernel, kernel))
        variance = cv2.blur(g * g, (kernel, kernel)) - mean * mean
        energy += float(np.sqrt(np.clip(variance, 0, None)).mean())
    return energy / 3.0


def _png_size(array: np.ndarray) -> int:
    buf = io.BytesIO()
    Image.fromarray(array.astype(np.uint8)).save(buf, "PNG")
    return len(buf.getvalue())


def _arrangement_disorder(gray: np.ndarray) -> tuple[float, int, int]:
    """Coarse compressibility ratio from the supplied reference implementation."""
    coarse = cv2.resize(gray, (48, 48), interpolation=cv2.INTER_AREA)
    compressed = _png_size(coarse)
    shuffled = coarse.ravel().copy()
    np.random.default_rng(0).shuffle(shuffled)
    shuffled_size = _png_size(shuffled.reshape(48, 48))
    return compressed / (shuffled_size + 1e-9), compressed, shuffled_size


def _spectral_discomfort(gray: np.ndarray) -> float:
    """Supplied mid/high-frequency amplitude fraction proxy."""
    spectrum = np.abs(np.fft.fftshift(np.fft.fft2(gray.astype(np.float32))))
    height, width = spectrum.shape
    yy, xx = np.mgrid[0:height, 0:width]
    radius = np.sqrt((yy - height / 2) ** 2 + (xx - width / 2) ** 2)
    radius /= 0.5 * min(height, width)
    total = spectrum.sum() + 1e-9
    return float(spectrum[(radius > 0.35) & (radius <= 1.0)].sum() / total)


def _color_variety(rgb: np.ndarray) -> int:
    return int(len(np.unique((rgb // 32).reshape(-1, 3), axis=0)))


def _confidence(species: str, score: float) -> tuple[float, float]:
    """Low confidence near an uncalibrated .5 boundary; never exceed method cap."""
    margin_factor = 0.5 + abs(score - 0.5)
    confidence = _BASE_CONFIDENCE[species] * margin_factor
    return _clip01(confidence), _clip01(1.0 - confidence)


def _computed_species(
    species: str,
    severity: float,
    measure: str,
    components: Mapping[str, Any],
    failure_modes: Sequence[str],
) -> dict[str, Any]:
    severity = _clip01(severity)
    provisional_threshold = 0.50
    provisional_slope = 8.0
    presence = 1.0 / (1.0 + math.exp(-provisional_slope * (severity - provisional_threshold)))
    confidence, uncertainty = _confidence(species, presence)
    reported_components = dict(components)
    reported_components["presence_mapping"] = {
        "kind": "provisional_logistic",
        "severity_threshold": provisional_threshold,
        "slope": provisional_slope,
    }
    return {
        "species": species,
        **SPECIES_CONTRACT[species],
        "status": "hypothesis",
        "presence_probability": _round(presence),
        "provisional_severity": _round(severity),
        "uncertainty": _round(uncertainty),
        "confidence": _round(confidence),
        "calibration": "engineering_proxy_uncalibrated",
        "measure": measure,
        "components": _jsonable(reported_components),
        "failure_modes": list(failure_modes),
    }


def _delegated_species(species: str, reason: str) -> dict[str, Any]:
    return {
        "species": species,
        **SPECIES_CONTRACT[species],
        "status": "delegated",
        "presence_probability": None,
        "provisional_severity": None,
        "uncertainty": 1.0,
        "confidence": 0.0,
        "calibration": "not_image_computable",
        "measure": None,
        "components": {},
        "failure_modes": [reason],
    }


def hypothesize_complexity_species(
    image: np.ndarray,
    *,
    image_id: str,
    image_sha256: str | None = None,
    source_ref: str | None = None,
) -> dict[str, Any]:
    """Return the complete six-species hypothesis vector for one image."""
    if not image_id or not isinstance(image_id, str):
        raise ComplexityContractError("image_id must be a non-empty string")
    if source_ref is not None:
        path = Path(source_ref)
        if path.is_absolute() or ".." in path.parts:
            raise ComplexityContractError("source_ref must be corpus-relative")

    gray, rgb = _gray256(image)
    coarse_gray = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
    fine_raw = _contrast_energy(gray)
    coarse_raw = _contrast_energy(coarse_gray)
    fine = _clip01(fine_raw / 32.0)
    coarse = _clip01(coarse_raw / 32.0)
    density = 0.7 * fine + 0.3 * coarse

    disorder_raw, png_bytes, shuffled_bytes = _arrangement_disorder(gray)
    disorder = _clip01(disorder_raw)
    color_count = _color_variety(rgb)
    variety = _clip01(math.log1p(color_count) / math.log(513.0))
    spectral_raw = _spectral_discomfort(gray)
    discomfort = _clip01(spectral_raw)

    species = [
        _computed_species(
            "surface_density",
            density,
            "two_scale_reference_contrast_energy_v1",
            {
                "coarse": coarse,
                "fine": fine,
                "coarse_raw": coarse_raw,
                "fine_raw": fine_raw,
            },
            [
                "normalisation is provisional until calibrated against human identification",
                "texture and object density can be conflated",
            ],
        ),
        _computed_species(
            "arrangement_disorder",
            disorder,
            "coarse_png_compressibility_ratio_v1",
            {
                "ratio": disorder_raw,
                "compressed_bytes": png_bytes,
                "shuffled_bytes": shuffled_bytes,
            },
            [
                "WEAK: natural texture can be mistaken for layout disorder",
                "compression is sensitive to image resampling and tonal noise",
            ],
        ),
        _computed_species(
            "variety",
            variety,
            "quantised_rgb_color_count_v1",
            {"quantised_color_count": color_count, "maximum_bins": 512},
            [
                "colour bins do not distinguish material or semantic variety",
                "illumination changes can alter the score",
            ],
        ),
        _computed_species(
            "textural_discomfort",
            discomfort,
            "mid_high_spectral_energy_fraction_v1",
            {"spectral_fraction_raw": spectral_raw},
            [
                "spectral proxy is not a direct report of felt discomfort",
                "relation to human comfort remains uncalibrated",
            ],
        ),
        _delegated_species(
            "semantic_incongruity",
            "late scene-grammar judgment requires a VLM or human observer",
        ),
        _delegated_species(
            "concealed_order",
            "latent order depends on observer expertise and intended activity",
        ),
    ]
    record = {
        "schema_version": HYPOTHESIS_SCHEMA,
        "model_version": MODEL_VERSION,
        "image_id": image_id,
        "image_sha256": image_sha256,
        "source_ref": source_ref,
        "species": species,
    }
    validate_hypothesis_record(record)
    return record


def validate_hypothesis_record(record: Mapping[str, Any]) -> None:
    if record.get("schema_version") != HYPOTHESIS_SCHEMA:
        raise ComplexityContractError("unsupported hypothesis schema_version")
    if not isinstance(record.get("image_id"), str) or not record["image_id"]:
        raise ComplexityContractError("image_id must be a non-empty string")
    rows = record.get("species")
    if not isinstance(rows, list):
        raise ComplexityContractError("species must be a list")
    names = [row.get("species") for row in rows if isinstance(row, Mapping)]
    if set(names) != set(SPECIES_CONTRACT) or len(names) != len(SPECIES_CONTRACT):
        raise ComplexityContractError("species vector must contain each v1 species exactly once")
    for row in rows:
        name = row["species"]
        for key, expected in SPECIES_CONTRACT[name].items():
            if row.get(key) != expected:
                raise ComplexityContractError(f"{name}.{key} violates the species contract")
        for key in ("presence_probability", "provisional_severity", "uncertainty", "confidence"):
            value = row.get(key)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not 0.0 <= float(value) <= 1.0
            ):
                raise ComplexityContractError(f"{name}.{key} must be null or in [0,1]")
        if row["image_computable"]:
            if row.get("status") != "hypothesis":
                raise ComplexityContractError(f"{name} must emit a hypothesis")
            if row.get("presence_probability") is None or row.get("provisional_severity") is None:
                raise ComplexityContractError(f"{name} must emit numeric hypotheses")
            if row.get("calibration") != "engineering_proxy_uncalibrated":
                raise ComplexityContractError(f"{name} must disclose uncalibrated status")
        else:
            if row.get("status") != "delegated":
                raise ComplexityContractError(f"{name} must be delegated")
            if row.get("presence_probability") is not None or row.get("provisional_severity") is not None:
                raise ComplexityContractError(f"{name} must abstain from pixel-only scoring")
            if row.get("confidence") != 0.0 or row.get("uncertainty") != 1.0:
                raise ComplexityContractError(f"{name} must report full uncertainty")
    arrangement = next(row for row in rows if row["species"] == "arrangement_disorder")
    if arrangement["confidence"] > 0.25:
        raise ComplexityContractError("arrangement_disorder confidence exceeds WEAK-method cap")


def build_selection_queues(
    hypotheses: Iterable[Mapping[str, Any]],
    identify_rows: Iterable[Mapping[str, Any]] = (),
    *,
    severity_bins: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """Build deterministic boundary, coverage, and model-human-disagreement queues."""
    if severity_bins < 2:
        raise ComplexityContractError("severity_bins must be at least 2")
    records = list(hypotheses)
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    computable: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for record in records:
        validate_hypothesis_record(record)
        for row in record["species"]:
            key = (record["image_id"], row["species"])
            if key in by_key:
                raise ComplexityContractError(f"duplicate hypothesis for {key}")
            by_key[key] = row
            if row["image_computable"]:
                computable.append((record, row))

    boundary = []
    coverage_groups: dict[tuple[str, int], list[tuple[Mapping[str, Any], Mapping[str, Any]]]] = defaultdict(list)
    for record, row in computable:
        probability = float(row["presence_probability"])
        boundary_closeness = 1.0 - 2.0 * abs(probability - 0.5)
        boundary.append(
            {
                "schema_version": QUEUE_SCHEMA,
                "queue": "boundary",
                "image_id": record["image_id"],
                "species": row["species"],
                "priority": _round(max(0.0, boundary_closeness) * float(row["uncertainty"])),
                "reason": {
                    "presence_probability": probability,
                    "uncertainty": row["uncertainty"],
                },
            }
        )
        severity = min(float(row["provisional_severity"]), 1.0 - 1e-12)
        bin_index = int(severity * severity_bins)
        coverage_groups[(row["species"], bin_index)].append((record, row))

    coverage = []
    for (species, bin_index), group in coverage_groups.items():
        count = len(group)
        for record, row in group:
            coverage.append(
                {
                    "schema_version": QUEUE_SCHEMA,
                    "queue": "coverage",
                    "image_id": record["image_id"],
                    "species": species,
                    "priority": _round(1.0 / count),
                    "reason": {
                        "severity_bin": bin_index,
                        "severity_bins": severity_bins,
                        "region_count": count,
                        "provisional_severity": row["provisional_severity"],
                    },
                }
            )

    human: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in identify_rows:
        if row.get("type") != "identify":
            continue
        present = row.get("present")
        if present == "cannot_tell":
            continue
        if present not in ("yes", "no"):
            raise ComplexityContractError("identify.present must be yes, no, or cannot_tell")
        key = (row.get("image_id"), row.get("species"))
        if key not in by_key:
            raise ComplexityContractError(f"identify row has no tagger hypothesis: {key}")
        human[key].append(1 if present == "yes" else 0)

    disagreement = []
    for (image_id, species), values in human.items():
        hypothesis = by_key[(image_id, species)]
        if not hypothesis["image_computable"]:
            continue
        human_rate = sum(values) / len(values)
        model_rate = float(hypothesis["presence_probability"])
        disagreement.append(
            {
                "schema_version": QUEUE_SCHEMA,
                "queue": "disagreement",
                "image_id": image_id,
                "species": species,
                "priority": _round(abs(model_rate - human_rate)),
                "reason": {
                    "tagger_presence_probability": model_rate,
                    "human_presence_rate": _round(human_rate),
                    "human_identification_count": len(values),
                },
            }
        )

    for queue in (boundary, coverage, disagreement):
        queue.sort(key=lambda row: (-float(row["priority"]), row["species"], row["image_id"]))
    return {"boundary": boundary, "coverage": coverage, "disagreement": disagreement}


def write_handoff(
    output_dir: str | Path,
    hypotheses: Iterable[Mapping[str, Any]],
    identify_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Write durable JSONL queues plus a hash-bearing manifest."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    records = sorted(list(hypotheses), key=lambda row: row["image_id"])
    for record in records:
        validate_hypothesis_record(record)
    queues = build_selection_queues(records, identify_rows)

    payloads = {
        "hypotheses.jsonl": records,
        "boundary.jsonl": queues["boundary"],
        "coverage.jsonl": queues["coverage"],
        "disagreement.jsonl": queues["disagreement"],
    }
    files = {}
    for filename, rows in payloads.items():
        raw = "".join(_canonical_json(row) + "\n" for row in rows).encode("utf-8")
        _atomic_write(output / filename, raw)
        files[filename] = {"rows": len(rows), "sha256": hashlib.sha256(raw).hexdigest()}
    manifest = {
        "schema_version": HANDOFF_SCHEMA,
        "hypothesis_schema": HYPOTHESIS_SCHEMA,
        "queue_schema": QUEUE_SCHEMA,
        "model_version": MODEL_VERSION,
        "files": files,
        "notes": [
            "tagger outputs are hypotheses, not answer keys",
            "numeric image-computable values are uncalibrated engineering proxies",
            "semantic_incongruity and concealed_order deliberately abstain",
        ],
    }
    _atomic_write(output / "manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    return manifest


def _canonical_json(value: Any) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def _atomic_write(path: Path, raw: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)
