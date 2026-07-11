# L4 Causal — Discovered Features

This directory holds **research output**, not pipeline code.

## How to Add a Discovery

Add an entry to `discovered_features.json`:

```json
{
  "id": "discovery_001",
  "finding": "fractal_D in [1.3, 1.5] predicts restoration > 0.7",
  "iv_keys": ["fractal_dimension"],
  "iv_level": "L0",
  "dv_keys": ["cognitive.restoration"],
  "dv_level": "L3",
  "method": "cross-validated ridge regression",
  "dataset": "UCSD_room_images_v2",
  "n_images": 500,
  "effect_size": "r² = 0.34",
  "ci_95": "[0.28, 0.40]",
  "publication": "",
  "date": "2026-06-15",
  "notes": "Robust across room types; weakest in kitchens"
}
```

## What Does NOT Go Here

- Raw data files → store in `data/`
- Analysis scripts → store in `scripts/`
- Trained models → store in `L2_structural/` with version tags
- VLM prompts → store in `L3_semantic/` with prompt hashes
