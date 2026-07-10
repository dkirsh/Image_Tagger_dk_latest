#!/usr/bin/env python3
"""Saliency worker (isolated). Prints one JSON line of saliency statistics.

Preferred backend: DeepGaze IIE/III (research-only weights). Run in a venv with
torch + deepgaze_pytorch:
    CNFA_SALIENCY_PYTHON=/opt/venvs/saliency/bin/python

Emits: {"ok": true, "peak_salience": float, "concentration": float}.

This scaffold includes a **spectral-residual saliency fallback** (Hou & Zhang,
2007) computed with NumPy so the pipeline returns a saliency signal before the
DeepGaze weights are installed. Because DeepGaze weights are research-only, the
adapter is licence-tagged RESEARCH; the fallback here is licence-clean and can
be used as the permissive substitute in a shipped build.
"""
import argparse
import json
import sys


def deepgaze_saliency(image_path):
    """Real path — DeepGaze IIE/III fixation-density map.

    TODO: load DeepGazeIIE(), build a centre-bias, run model(image_tensor,
    centerbias) -> log-density; exponentiate and normalise to a saliency map.
    Returns a HxW float array in [0,1] or raises if unavailable.
    """
    raise NotImplementedError("wire DeepGaze here")


def spectral_residual_saliency(image_path):
    """Permissive fallback: spectral-residual saliency (Hou & Zhang, 2007)."""
    import numpy as np
    from PIL import Image

    img = Image.open(image_path).convert("L").resize((128, 128))
    a = np.asarray(img, dtype="float64")
    F = np.fft.fft2(a)
    log_amp = np.log(np.abs(F) + 1e-9)
    phase = np.angle(F)
    from scipy.ndimage import uniform_filter

    spectral_residual = log_amp - uniform_filter(log_amp, size=3)
    sal = np.abs(np.fft.ifft2(np.exp(spectral_residual + 1j * phase))) ** 2
    sal = uniform_filter(sal, size=3)
    sal = (sal - sal.min()) / (np.ptp(sal) + 1e-9)
    return sal


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--params", default=None)
    args = ap.parse_args()
    try:
        import numpy as np

        try:
            sal = deepgaze_saliency(args.image)
            source = "deepgaze"
        except Exception:
            sal = spectral_residual_saliency(args.image)
            source = "spectral_residual_fallback"

        sal = np.asarray(sal, dtype="float64")
        peak = float(sal.max())
        p = sal / (sal.sum() + 1e-9)
        entropy = float(-(p * np.log(p + 1e-12)).sum())
        max_entropy = float(np.log(p.size))
        concentration = float(1.0 - entropy / max_entropy) if max_entropy > 0 else 0.0
        print(json.dumps({
            "ok": True, "source": source,
            "peak_salience": peak, "concentration": concentration,
        }))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)[:200]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
