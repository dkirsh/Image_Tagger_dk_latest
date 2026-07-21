# Tanishq — Onboarding & Sprint List (Image Tagger / Cognitive+Wellness Code)

*Prepared 2026-07-21. Your task list as a research student on the project. Read §0–§2 first (setup +
the lay of the land), then work the sprints in §4. §3 is your flagship task — the image database — and
it has a full build brief you can hand to yourself or to Claude/Codex. Ask David or check the linked
docs whenever a "why" isn't obvious; understanding the science behind an attribute matters as much as
the code.*

---

## 0. What this project is (one screen)

We are building the **Visual Tagger**: it reads a picture of an interior and returns, per image, a set
of **computed visual attributes** — how cluttered, how bright/glary, how open, how much prospect/refuge,
etc. — each one *tiered* for honesty and, for many, carrying a cryptographic **M1′ audit signature** that
proves the number is genuine. The Tagger is the measurement half of a bigger system: **Article Eater /
Knowledge Atlas** (the research-literature engine that grounds each attribute in evidence) and the
**image corpus** (real interiors we tag, search, and use as experiment stimuli). Full narrative:
`docs/Visual_Tagger_Clean_Account_2026-07-21` (ask David for it) and the plan of record
`docs/L6_CORRECTNESS_PROGRAM_2026-07-21.md` + `docs/L6_PROGRAM_REVISIONS_v2_2026-07-21.md`.

Current state: **68 attributes** compute; **28** carry the M1′ signature; **19 GREEN / 49 AMBER**
mechanically; **0 construct-validated yet** (that's the human-labelling campaign, ahead of us). Your work
moves the audit coverage, the corpus/database, and the deployment forward.

---

## 1. Environment setup

**Repo.** `github.com/dkirsh/Image_Tagger_dk_latest`, branch **`cnfa-algs-2026-07-14`** (remote name
`latest`). David will `git push` the latest commits before you start — confirm you see the commit
`Morning summary 2026-07-21` (or newer) in the log after cloning.

```bash
git clone https://github.com/dkirsh/Image_Tagger_dk_latest.git
cd Image_Tagger_dk_latest
git checkout cnfa-algs-2026-07-14
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy opencv-python-headless scikit-image pillow
pip install reference/visual_clutter-1.0.7-py3-none-any.whl   # the FC/SE dependency (vendored)
export PYTHONPATH=.
```

**Confirm it works (do this before any sprint):**
```bash
python3 annotation_socket/m1_prime.py                       # -> "m1_prime self-test: PASS"
python3 annotation_socket/tests/test_m1_prime.py            # -> "M1' TESTS PASSED"
for t in annotation_socket/tests/test_*.py; do python3 "$t"; done   # per-file (pytest may be absent)
bash verify_collector_fix.sh                                # corpus integrity audit (edit REPO path at top if needed)
```
If `annotator.py` fails on `from cpp import stage`, you also need the control modules in
`/Users/davidusa/REPOS/_control/{cpp,supervisor}` on `PYTHONPATH` (ask David — they live outside this repo).

**Where the data lives.**
- **Images (local):** `corpus_L6/` — PNGs under `interiors/ pairs/ collections/ nature_glass/ materials/`.
  PNGs are **git-ignored** (too big); only `manifest.csv` + `_provenance.csv` are tracked.
- **Images (cloud master):** Google Drive `gdrive:corpus_L6` via rclone (David owns the credential; a
  backfill is in progress). Each row's `gdrive_path` in `_provenance.csv` points to its Drive copy.
- **The index/database:** `corpus_L6/manifest.csv` (curation: category, A/B pairing) + `_provenance.csv`
  (source, licence, resolution, sha, gdrive_path, class). There is a lightweight generated index
  (`scripts/build_corpus_index.py` → `index.json`/`index.html`) — **your Sprint A turns this into a real
  queryable database.**
- **Example test images:** `Example Images/` (jpg/webp) — canonical inputs for the stage smoke.
- **Knowledge Atlas:** the web server you already sysadmin — the evidence engine the Tagger binds to.
- **Experiment Maker:** `REPOS/Experiment_Maker` (has `psychopy_tests/`, the adaptive-preference system) —
  where the human experiments that validate attributes get built.

**Where to add images.** New corpus images go through `scripts/collect_corpus_L6.py` (web sources
openverse/unsplash/pexels, academic mit_indoor/sun397/places365, `--from-dir`), which writes the PNG +
appends to `manifest.csv`/`_provenance.csv` + mirrors to Drive with `--gdrive`. **Never hand-edit
`collect_corpus_L6.py` blind** — David edits it on the Mac; pull, merge, preserve his filename-digest
fix. Corpus must be **PNG** (a cross-platform JPEG-decode issue). Run `--status` to see targets.

**Working discipline (please internalise — this is the culture of the repo):**
- **Determinism is sacred.** Many attributes ship an audit digest; if you make an operator
  non-deterministic (unseeded kmeans, thread-dependent reduction), you turn genuine records RED. Test
  "emit twice → identical digest" before committing anything that touches an operator.
- **Honest tiers, no overclaim.** An operator that can't read a space should *abstain*, not guess.
- **Never `git add -A`** — add named files only. `*prompt*.md` is git-ignored (use `git add -f` if a
  prompt doc must be committed).
- **Human data = IRB.** Anything measured on people (the labelling campaign, cognitive tasks) needs
  ethics approval + consent first. Don't collect human data without it.
- **You move fast — pair it with a review gate.** Ping David or a second reader on anything touching
  data integrity, the audit layer, or an experiment's correctness before it lands.

---

## 2. How to read a sprint

Each sprint below has: **Goal · Tasks · Done-when (acceptance) · Guardrails · Depends-on**. Work them
roughly in order; A, B, E can run in parallel. Log progress in `TASKS.md`. Ask before changing anything
in `annotation_socket/` (the audit core) without a test.

---

## 3. SPRINT A — Build the image database *(your flagship)*

**Goal.** Turn the corpus from "a folder of PNGs + two CSVs" into a real, queryable **image database**
that indexes every image by all the terms we care about *and joins in the computed visual-attribute
scores*, so anyone can ask "give me interiors high on prospect and low on clutter" and get real images
back. This is the substrate for the student/architect/ANFA search described in §4-G.

**Why it matters.** Right now the visual-attribute *terms* (our 68 attributes) and the *images* are not
connected in any queryable store. Connecting them is what makes the corpus useful as stimuli and as a
design-precedent library.

### Build brief (the prompt — hand this to yourself/Claude/Codex)

> Build `scripts/corpus_db.py` that creates and populates a **SQLite** database `corpus_L6/corpus.db`
> from `corpus_L6/manifest.csv` + `corpus_L6/_provenance.csv` + an optional `corpus_L6/scores.csv`
> (per-image attribute scores from the Tagger, produced in Sprint E). Provide: `build` (create+load),
> `query` (filter/sort by any field, ranges on attributes, free-text), and a `--rebuild` idempotent
> reload. Add SQLite **FTS5** full-text over filename+type+notes. Ship a tiny CLI and a `query()` Python
> API. Re-point `scripts/build_corpus_index.py`'s HTML at the DB so the browse UI reads live data. Keep
> it dependency-light (stdlib `sqlite3`) and deterministic. Unit-test: load a fixture, assert row counts
> match the CSVs, assert an attribute-range query returns the expected images, assert FTS returns hits.

**Schema — the tables and, crucially, the vocabulary of terms to index** (this is the part where you
need to know *what* we index; group the columns like this):

1. **`images`** — one row per image:
   - *identity/provenance:* `filename` (PK), `sha256`, `source` (mit_indoor67 / sun397 / unsplash /
     pexels / openverse / curated), `source_id`, `creator`, `license`, `license_url`, `orig_url`,
     `collected_utc`, `gdrive_path`, `width`, `height`, `px_bucket` (>=2048 / 1024–2047 / 512–1023 / <512).
   - *taxonomy:* `category` (interiors / pairs / collections / nature_glass / materials), `arch_type`
     (the room class — the 67 MIT-Indoor classes + SUN indoor classes, e.g. corridor, conference_room,
     classroom, atrium, lobby, office, library, restaurant, …), `space_family` (circulation / work /
     learning / domestic / hospitality / retail / civic / industrial / other).
   - *A/B pairing:* `pair_id`, `pair_role` (A/B/base/variant), `pair_expected_better`, `manipulation`
     (daylight / glare / warmth / contrast / geometry / …), `notes`.
2. **`attributes`** — a reference table of our **68 visual-attribute terms**, one row each, with
   `attr_id` (e.g. `cnfa.fluency.feature_congestion`), `family` (fluency-clutter / light / geometry-space /
   layout-wellbeing / acoustic / material / cognitive-salience), `human_label` (a plain name),
   `tier_hint`, `m1p_audited` (bool), `atlas_node_ids` (evidence links into the Knowledge Atlas),
   `unit`/`range`, and a one-line `definition`. **Seed this table from the live registry**
   (`annotation_socket/registry.py` → `PREDICATES`) so it can't drift. The families & members to index:
     - **fluency-clutter (16):** feature_congestion, subband_entropy, fractal_dimension,
       fractal_mid_d_band, spectral_slope_deviation, edge_orientation_entropy, edge_clarity_mean,
       symmetry_score_horizontal, color_palette_entropy, processing_load_proxy, proto_object_count,
       multiscale_gradient, multiscale_unique_color, grayscale_gabor_entropy_proxy, local_congestion_proxy, complexity_partition.
     - **light (11):** brightness_variance, glare-risk, warm_vs_cool_ratio, vertical_illuminance_proxy,
       luminance_gradient_contrast, shadow_softness, sun_patch_geometry, spotlight_pool_geometry,
       dark_zone_map, evening_ambience, temperature_mismatch.
     - **geometry-space (11):** prospect, enclosure_index, contour_angularity, orderliness_alignment,
       verticality_cues, ceiling_openness_relative, double_height_space, blind_corner_index,
       barrier_permeability, threshold_emphasized, choice_richness.
     - **layout-wellbeing / C-series (26):** visual_integration, connectivity, intelligibility,
       wayfinding_load, setting_fit, spatial_generosity, triangulation_ignition, stranded_amenity_index,
       collaborator_proximity, path_overlap, focus_speech_privacy, distraction_distance, view_equity,
       daylight_proximity, prospect_refuge, crowding_risk, focus_collab_separation, active_design,
       territory, local_control, air_quality, restoration_nature, chronic_soundscape, thermal,
       circadian_contrast, social_connectedness.
     - **acoustic (2):** street_noise_intrusion, acoustic_absorption_proxy.
     - **material (1):** texture_density.  **cognitive-salience (1):** landmark_salience.
3. **`scores`** — the join between attributes and images (the Sprint-E output): `filename`, `attr_id`,
   `value` (scalar), `tier`, `confidence`, `abstained` (bool), `m1p_digest`, `computed_utc`,
   `pctile_in_corpus` (percentile of this value across the corpus, so "high/low X" queries are easy).
   *This table is literally "the visual-attribute terms connected to the images."*
4. **`human_labels`** *(fills later from the 2AFC campaign)* — `filename`, `construct` (clutter /
   openness / restorative / mystery / refuge / preference), `human_score`, `ci_low`, `ci_high`,
   `n_judgments`, `agreement`.

**Queries the DB must serve** (write these as tests / example CLI calls): by space-type/family; by
attribute range with corpus-percentile ("prospect ≥ p80 AND clutter ≤ p20"); by A/B pair + target
construct; by licence + resolution (for reusable stimuli); by human-label construct; free-text; and the
three user journeys in §4-G. Include a `--export` to CSV for the Experiment Maker.

**Done-when:** `corpus.db` builds from the CSVs; row counts match; the `attributes` table is seeded from
the registry (68 rows); attribute-range + FTS queries return correct images; the browse HTML reads the
DB; unit tests pass. **Guardrails:** stdlib-only, idempotent, deterministic; don't mutate the CSVs.
**Depends-on:** nothing to start the schema; the `scores` table fills from Sprint E.

---

## 4. The other sprints

### SPRINT B — Finish the M1′ audit coverage (40 attributes remain)
**Goal.** Take audited coverage from 28/68 toward full. **Tasks:** implement the geometry/plan
`plan_ref` audit (a cheap `grid_hash`+`cell_m` tag on every plan-consumer, so C2…C29 prove they used the
plan C1 certified — spec in `L6_PROGRAM_REVISIONS_v2 §4`), and the CC-3 value-input criteria M1′ on
**fixed synthetic plan fixtures**. **Done-when:** the new bindings emit in a real annotate run and replay
MATCH; `test_m1_prime.py` extended and green; coverage number rises. **Guardrails:** this is the audit
core — every new binding needs the determinism + genuine-MATCH + real-field-tamper test (copy the pattern
in `test_operator_extract_bindings`). Pair-review before merge. **Depends-on:** read `m1_prime.py` first.

### SPRINT C — Cross-environment determinism (CC-9b)
**Goal.** Make the audit survive Mac↔server. **Tasks:** pin threads (`cv2.setNumThreads(1)`,
`OMP/OPENBLAS/MKL_NUM_THREADS=1`) at annotator import; record a per-record **env fingerprint** (cv2 build,
BLAS vendor, versions); implement the **per-field exact/tolerance schema** so large-magnitude float stats
compare within a declared eps and emit a second `TOL-MATCH` verdict (spec in revisions §4). **Done-when:**
the same PNG produces a `DIGEST-MATCH` on one machine and a `TOL-MATCH` across two; the docstring's
overstated cross-env claim is corrected. **Guardrails:** don't loosen same-machine tamper detection.

### SPRINT D — Wave-3 detector deployment (with David's model choice)
**Goal.** Replace colour heuristics for biophilia/material with real segmentation masks. **Tasks:** once
David picks the model (DEC-1: a pinned ADE20K-trained ONNX), you **stand it up** — version-hash it,
wire vegetation/window-view/water/material masks into the operators, add negative-control tests (green
paint ≠ vegetation). This is deployment/sysadmin + wiring, your strength. **Done-when:** the masked
operators score/abstain honestly and the negative controls pass. **Depends-on:** DEC-1 (David).

### SPRINT E — Corpus scoring pipeline (connects to Sprint A)
**Goal.** Run the Tagger over the whole corpus → `corpus_L6/scores.csv` (filename, attr_id, value, tier,
confidence, abstained, m1p_digest) → load into the DB's `scores` table. **Tasks:** a batch runner over
`corpus_L6/**.png` that calls the annotator, flattens the record's scored values, and writes the CSV;
compute corpus percentiles; make it resumable and deterministic. **Done-when:** every corpus image has a
score row per scored attribute; the DB `scores` table populates; a spot-check matches a single-image
annotate. **Guardrails:** PNG-only; log abstentions; don't overwrite on partial runs. **Depends-on:**
Sprint A schema; a working annotator (control modules).

### SPRINT F — Labelling console backend + deploy
**Goal.** Take the 2AFC labelling console (`viz/labeling_console.html`, already built + verified) from a
demo to a running study. **Tasks:** a thin backend (Flask/Cloud Run or Apps Script) that receives the
POSTed judgments into a table / CSV keyed to the schema; wire image URLs to the Drive/CDN public links;
generate the `design.json` (which pairs/anchors/golds); deploy behind the lab server you admin; dry-run
end-to-end. **Done-when:** a test session's judgments land server-side with the right schema. **Guardrails:**
**IRB approval + consent before any real participant**; no PII; keep gold answers out of the client DOM
(there's a flag-guarded test seam to remove for production).

### SPRINT G — Annotated-image search & display
**Goal.** The front door: a search UI over the DB that returns real images with their attribute overlays.
**Tasks:** wire the browse UI to `corpus.db` (Sprint A); add the attribute-range + construct filters; hook
each result to the Tagger's layered viewer / question-composer so a user sees *where* and *why* an image
scores as it does; implement the three journeys (student stimulus-set export, architect precedent search,
ANFA evidence view). **Done-when:** a user can filter by attribute + type and open an annotated overlay.
**Depends-on:** Sprints A + E; the viewer in `viz/`.

---

## 5. Sequencing & what to do first
1. **Day 1:** §1 setup; get all tests green; read the clean-account + correctness-program docs.
2. **Week 1:** Sprint A schema + loader (from the CSVs) — get `corpus.db` building and queryable on
   metadata even before scores exist. In parallel, start Sprint E's batch runner.
3. **Week 2:** Sprint E scores → fill the DB `scores` table → Sprint A's attribute-range queries light up.
4. **Then:** B/C (audit depth, with review), D when David lands DEC-1, F/G for the campaign + search.
Log everything in `TASKS.md`; flag blockers early; when in doubt about an attribute's *meaning*, ask —
the science is half the job.
