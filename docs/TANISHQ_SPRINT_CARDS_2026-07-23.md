# Tanishq — Tagger Sprint Cards (assignable work)

*Generated 2026-07-23 (Fable/Cowork) from the live queue `TASKS.md`. Each card is self-contained: goal,
steps, acceptance test, files, dependencies, owner. Pick a card, claim it in `TASKS.md`, ship it under
the repo protocol. Pair-with-review on anything touching the registry or M1′. Authoritative queue is
still `TASKS.md`; this file is the how-to-pick-it-up companion.*

---

## How to use this file
- **Claim** a card by putting your name + date in the `TASKS.md` row and moving it to in-progress.
- **Definition of done (every card):** code + a passing test/harness + the attribute (if any) emits an
  **M1′** block + honest tier (GREEN/AMBER/RED with evidence, never a bare tier) + a one-line entry in
  `TASKS.md` "Completed" with the commit hash.
- **Conventions (root `CLAUDE.md`):** never `git add -A` (add named files only); `git --no-optional-locks`;
  lock-sweep stale `.git/*.lock` before committing; abstain-with-evidence rather than guess; every
  Codex-handed task names its committed artifact path (artifact contract).
- **Push:** `bash push_latest.sh` (remote `latest`, branch `cnfa-algs-2026-07-14`). Sandbox can't push
  over SSH — David pushes, or run the provided `push_tagger_sprints.sh`.
- **Blocked on David decisions:** DEC-1 (segmentation model), DEC-2 (Faithful-V2 FOV policy),
  DEC-3 (V6/V7 retirement) — see `TASKS.md §Decisions open`. Cards that need them are marked ⛔DEC.

---

## READY NOW (no decision needed)

### CARD LEG-1 · P2 · Legibility Field (VL) — NEW attribute *(the one just spec'd)*
**Goal.** Build `ATTR-LEG1 Legibility Field`: for wayfinding cues (signage / room numbers / arrows),
compute readability as luminance-contrast × adaptation-luminance × visual-angle vs the eye's
contrast-sensitivity limit, and emit a position-tagged VL heat-map + per-sign legibility distance.
**Spec (read first).** `docs/JOB_LEGIBILITY_FIELD_WAYFINDING_2026-07-23.md` (full model + references:
Adrian Visibility Level, Rea–Ouellette RVP, Barten CSF).
**Steps.**
1. **Tier-1 (do first, standard CV):** per-pixel *relative* luminance (`Y=0.2126R+0.7152G+0.0722B` on
   linearized sRGB); scene-text/sign detection + OCR → target region + x-height(px); Weber contrast of
   stroke vs sign-field; a first-pass VL field with a fixed adaptation luminance. **Label output
   `calibration: relative_uncalibrated`.**
2. Emit the annotation schema from the spec (§4): per-target JSON + a raster `legibility_field[sign]`.
3. Gate by line-of-sight: reuse the existing **isovist/spatial** machinery so VL(p,s)=0 unless s is in
   the isovist from p and in the gaze cone.
4. Register `ATTR-LEG1` in `docs/CNFA_ATTRIBUTE_INVENTORY_2026-07-18.md` as **SPEC+PLAN** with the tier map.
**Acceptance test.** On a test image with a known sign: legibility falls off with distance; a low-contrast
sign yields shorter `D_max` than a high-contrast one at equal size; output validates against the schema;
M1′ block emitted; neg-control (no sign) → empty field, not a hallucinated one.
**Files.** new `viz/` or `ops/` module for LEG1; `docs/CNFA_ATTRIBUTE_INVENTORY_*` (register); reuse
isovist code in the spatial/geometry ops.
**Blocked by.** none for Tier-1. Tier-2 (real cd/m² + legibility distances) needs the **HDR-fisheye +
Sekonic** cross-cal (David decision d). David also owes: `VL_crit` threshold, age term, chroma channel.

### CARD CC-3 · P1 · Declared-input VALUE bundles (C5–C23)
**Goal.** Push predicates **C5–C23** through the `input_values` channel (the one street-noise opened), with
full-socket fixtures per predicate, so declared inputs produce real units instead of abstaining blind.
**Steps.** For each of C5–C23: define its declared-input socket; write a full-socket fixture (known
inputs → known output); wire through `input_values`; confirm the predicate emits a value + M1′ when the
socket is filled and abstains-with-evidence when it isn't.
**Acceptance test.** Each predicate: fixture passes; filled socket → value+M1′; empty socket →
abstain-with-evidence (not a guess); no regressions in the 68-pred smoke.
**Files.** the predicate modules for C5–C23; the `input_values` channel; fixtures under `tests/`.
**Blocked by.** none.

### CARD CC-9 · P2 · Geometry-chain robustness (jitter stability)
**Goal.** Add a jittered-input stability test for the geometry chain (L5 found ~13% `cell_m`
amplification), so the Tier-B instability is measured and capped honestly.
**Steps.** Perturb inputs with controlled pixel jitter; measure output variance along the geometry chain;
report the amplification factor per predicate; add the cap/flag. (Scale anchors W2.7 wait on the detector
— that part is ⛔DEC-1.)
**Acceptance test.** Deterministic jitter → reported stability numbers; a predicate exceeding the
instability cap is flagged, not silently scored.
**Files.** geometry-chain ops; `tests/` robustness harness.
**Blocked by.** none for the jitter test (scale-anchor half needs CC-5/DEC-1).

### CARD VIEW-4 · P2 · A-vs-B compare view (+ corpus-labeling tool)
**Goal.** Two units side-by-side with synchronized layers — doubles as the **corpus-labeling tool** for
the L6 human-validation work.
**Steps.** Extend the layered viewer (VIEW-1) to a two-pane synchronized view; shared layer toggles;
A/B pair loading from the manifest; a label-capture control that writes to the labeling schema.
**Acceptance test.** Load an A/B pair; toggling a layer updates both panes; a label is captured and
written; 0 JS console errors (house standard).
**Files.** `viz/` viewer; the corpus manifest; labeling output schema.
**Blocked by.** VIEW-1 (done). Benefits from the corpus starter set (DK-1).

### CARD VIEW-5 · P3 · Viewer server mode
**Goal.** Parameter sliders with live recompute + batch browsing.
**Steps.** Thin server over the scoring pipeline; expose predicate parameters as sliders; live recompute
on change; batch/paged browse of the corpus.
**Acceptance test.** A slider change recomputes and re-renders the affected layer; batch browse pages
through the corpus without reload.
**Files.** `viz/` server; scoring entrypoints.
**Blocked by.** VIEW-2 (done).

### CARD DK-1-support · P0-gating · Corpus starter set (support David)
**Goal.** Help land the **starter corpus** (gates ALL L6): ~30 interiors + 15 A/B pairs + 5 each
nature-glass / materials / collections, **all PNG converted on the Mac**, `manifest.csv` from day one.
**Steps.** Mechanical: convert to PNG (L5 requires PNG — no JPEG decode divergence); build `manifest.csv`
(filename, category, pair_id, pair_expected_better, notes) from day one; verify no duplicate filenames;
run the collector `--status`.
**Acceptance test.** `--status` shows the starter targets met; manifest rows == files; 0 duplicate
filenames; all PNG.
**Files.** `corpus_L6/`, `scripts/collect_corpus_L6.py`, `scripts/build_corpus_index.py`.
**Blocked by.** David initiates the export; Tanishq can own the mechanical PNG+manifest pipeline.

---

## ~~GATED ON A DAVID DECISION~~ → **UNBLOCKED 07-23** (all decisions made)

> **DEC-1 = SegFormer-B2** (pinned ONNX + version-hash) → **CC-5 READY.**
> **DEC-2 = declared-assumption/AMBER, disclose FOV, hard-abstain only when FOV-sensitivity > threshold** → **CC-8 READY.**
> **DEC-3 = retire V6-proxy now, keep V7 one corpus cycle** → **CC-6 READY.**
> The cards below are now startable; details/options are in `TASKS.md §Decisions open`.

### CARD CC-5 · P1 · ⛔DEC-1 · Wave-3 detector wave
**Goal.** Pin one segmentation model → real vegetation / window-view / blue-space / material /
sociopetal masks + art-content & text/signage VLM gates, replacing the chromaticity heuristics; adds a
segment-count clutter layer and upgrades the partition's biophilic gate.
**Unblock.** **DEC-1** — David picks SegFormer-B0 vs **B2** (recommendation on record: B2, pinned ONNX +
version hash, because scoring is offline batch on a small corpus so B2's cost doesn't bite and mask
quality is the whole point).
**Acceptance test.** Negative controls pass — green paint ≠ vegetation; indoor plant near a window ≠
window-view greenery; masks are version-hashed with M1′ = `segmentation_mask` provenance.
**Files.** new detector ops; registry; `tests/` neg-control fixtures.

### CARD CC-8 · P2 · ⛔DEC-2 · Faithful V2 (Penacchio–Wilkins 2-D)
**Goal.** Replace the honest radial-slope V2 *proxy* with the true 2-D Penacchio–Wilkins discomfort
metric; `fft_2d` M1′ class; FOV gate.
**Unblock.** **DEC-2** — FOV policy (hard-abstain without EXIF vs declared-assumption tier; recommendation
on record: declared-assumption, AMBER, disclosed FOV, sensitivity-gated abstain).
**Acceptance test.** Faithful V2 adjudicated against a reference to ~1e-6 (as FC/SE were); FOV policy
applied per the decision.

### CARD CC-6 / CC-7 · P2 · PANEL/DEC-3 · proxy retirement + FC gain
**CC-6:** retire the V6 proxy (measured uncorrelated, −0.117) — **DEC-3** (recommendation: retire V6 now,
keep V7 one corpus cycle). **CC-7:** decide which `collapse()` is "the" FC given the reference lacks the
MATLAB ×4 upConv gain — **PANEL**.

### CARD CC-1 · P0 · CODEX artifact · External ATTACK pass
**Goal.** Adversarial attack on the un-attacked batch (clutter_stack + complexity_partition 11-class +
faithful FC/SE + wave2_geometry) — cadence rule: attack before building on top.
**Owner.** CODEX (David drops the prompt when written, DK-2); Tanishq can run the harness + disposition
findings. Artifact: `docs/CODEX_ATTACK_TAX_VERDICT_<date>.md`.

---

## Waiting-on-David summary (so nothing stalls silently)
- **DEC-1 / DEC-2 / DEC-3 — ALL DECIDED 07-23.** CC-5, CC-8, CC-6 are READY.
- **DK-1 — GO 07-23:** start the starter corpus export now (gates all L6 + VIEW-4 labeling).
- Still open: **CC-7** FC collapse gain → PANEL.  **LEG-1** thresholds (VL_crit, age, chroma, calibration) → when LEG-1 is scheduled.
