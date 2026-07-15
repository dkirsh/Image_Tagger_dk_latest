# Image_Tagger_dk_latest

This repository contains both the **Image Tagger web application** (student-ready
work surface) and the **Cognitive-Code computation engine** (`cnfa_algs/`) — the
research core that computes environmental-cognition attributes of interior spaces
from visual input.

## The Research Engine — `cnfa_algs/`

The cognitive-code computation engine turns David Kirsh's cognitive-code
dimensions into computable, localisable, displayable annotations of interior
spaces. Start here:

1. **Why this exists:** [`docs/VISION_AND_DIRECTION_2026-07-14.md`](docs/VISION_AND_DIRECTION_2026-07-14.md)
   — "Reading Space", the founding direction document.
2. **Architecture & module map:** [`cnfa_algs/ARCHITECTURE.md`](cnfa_algs/ARCHITECTURE.md)
   — dependency graph, data flow, all 26 modules with purpose and exports.
3. **Pipeline contract:** [`cnfa_algs/CONTRACT.md`](cnfa_algs/CONTRACT.md)
   — Stage 0→3 pipeline schema, parallelism rules, `AttributeResult` schema.
4. **Scientific parameters:** [`cnfa_algs/JUSTIFICATION_TABLE.md`](cnfa_algs/JUSTIFICATION_TABLE.md)
   — every parameter → citation → rationale → limitation.
5. **Change history:** [`cnfa_algs/CHANGELOG.md`](cnfa_algs/CHANGELOG.md)
6. **Run instructions:** [`cnfa_algs/README.md`](cnfa_algs/README.md)

**Master status** (cross-project): `/Users/davidusa/REPOS/MASTER_STATUS_ALL_PROJECTS_2026-07-14.md`

## The Web Application

### Active App Root

Work in this folder:

```bash
cd Image_Tagger_3.4.74_vlm_lab_TL_runbook_full
```

Historical sibling folders such as `TRS_v1.1/`, `image_decomposition/`,
`low-level-image-features/`, and `ImageDecomposer/` are reference material.
Do not implement student sprint work there unless a sprint contract explicitly
says so.


## What Was Added For The Student Handoff

- Architectural tag backlog:
  `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ARCHITECTURAL_TAG_OPERATIONAL_BACKLOG_2026-07-07.md`
- Student sprint contracts:
  `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/STUDENT_ARCHITECTURAL_TAG_SPRINT_CONTRACTS_2026-07-07.md`
- Visual attribute inventory:
  `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/reports/IMAGE_TAGGER_VISUAL_ATTRIBUTE_INVENTORY_2026-07-07.md`
- MPIB-compatible low-level feature bridge:
  `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/mpib_low_level.py`

The live canonical science version is now `3.4.75-canonical-mpib-v1`.
It enables `enable_mpib_low_level` by default and writes a
`mpib_low_level_json` science artifact.

## Student Setup

For the full app, install Docker Desktop, then run:

```bash
cd Image_Tagger_3.4.74_vlm_lab_TL_runbook_full
./auto_install.sh
```

For a light local verification of the MPIB bridge:

```bash
cd Image_Tagger_3.4.74_vlm_lab_TL_runbook_full
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-install.txt
PYTHONPATH=. pytest tests/test_mpib_low_level.py
```

The backend Docker image already installs `scikit-image`. The host
requirements also include `scikit-image` so direct local imports of `skimage`
work during student checks.

## First Student Reading Order

1. `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/STUDENT_START_HERE.md`
2. `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/README_v3.md`
3. `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/STUDENT_ARCHITECTURAL_TAG_SPRINT_CONTRACTS_2026-07-07.md`
4. `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ARCHITECTURAL_TAG_OPERATIONAL_BACKLOG_2026-07-07.md`

