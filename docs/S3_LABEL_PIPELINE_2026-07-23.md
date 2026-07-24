# S3 — Label pipeline: design generator + BT aggregator (built 2026-07-23, Cowork/Opus, overnight)

Closes the two offline, no-corpus-image pieces the S3 doc listed as **"still to build (offline, feeds
the console)"** — the `design.json` generator and the aggregation step — so the existing
`viz/labeling_console.html` now has both an input builder and an output analyser. Both are **read-only
on the corpus, fabricate no labels, and are verified end-to-end headless** (design schema + graph
connectivity; aggregator recovers a known ground truth). *Not committed to git* — placed in the working
tree for review + your normal `push_latest` protocol.

## Files (in `scripts/`)
- **`build_label_design.py`** — `corpus_L6/manifest.csv` → `design.json` in the exact schema the
  console consumes (`items / construct_order / pairs / anchor / gold`). Emits (1) the **82 designed A/B
  pairs** as clean single-construct edges, construct inferred from the manifest `notes` via an auditable
  `NOTES_MAP` (surfaced in `<out>.sidecar.json`); (2) a **balanced, connected, sparse pairwise** sample
  over the singletons per construct — stage-1 of ASAP. Self-validates (every referenced key is an item;
  gold answers legal; each construct's comparison graph is connected — the identifiability condition for
  Bradley–Terry). `--pairs-only` gives a lean pilot design (A/B + anchors + gold, no global pairwise).
- **`aggregate_labels.py`** — console judgment CSV(s) → `corpus_L6/human_labels.csv`
  (`filename, construct, human_score, ci_low, ci_high, n_judgments, agreement`). Worker gold-QC →
  **regularised Davidson–Bradley–Terry** per construct (tie-aware: "can't tell" is modelled as a tie,
  not dropped; ridge prior keeps the scale identifiable/separation-safe) → latent score per image;
  Likert anchors → mean+CI; **cluster bootstrap over workers** for CIs. This is the file S4 calibration
  fits every computed attribute against.
- **`verify_label_pipeline.py`** — synthesises a manifest, builds a design, simulates crowd judgments
  from a known latent truth (good + gold-failing bad workers + ties), aggregates, and asserts:
  design schema valid + graphs connected; **bad workers dropped by gold QC**; recovered BT scores track
  ground truth (Spearman **ρ ≈ 0.75–0.85** in the last run); Likert means recovered; output schema
  matches `human_labels.csv`. Run: `python scripts/verify_label_pipeline.py` (exit 0 = pass).

## Real-manifest smoke (2026-07-23 snapshot, 538 rows)
`build_label_design.py` on the live manifest: **82 A/B pairs** (inferred construct: restorative 42 /
preference 38 / openness 1 / clutter 1 — reflecting that the current A/B set is photometric daylight/
contrast manips, which map to restoration/affect), **538 items**, per-construct global-pairwise graphs
all **connected**. `--pairs-only` yields the 82-pair + 12-anchor pilot design.

## Wiring / how to run
```bash
# 1. build the design the console loads (full campaign)
python scripts/build_label_design.py --manifest corpus_L6/manifest.csv --out corpus_L6/design.json
#    or a lean pilot:
python scripts/build_label_design.py --pairs-only --out corpus_L6/design_pilot.json
# 2. (run the console; collect CSVs) then aggregate:
python scripts/aggregate_labels.py judgments_*.csv --out corpus_L6/human_labels.csv --drop-too-slow
```
Load `design.json` via the console's consent-screen control; set `imageBaseUrl` to the Drive/CDN
public base (needs the S0 Drive backfill so images are public-read).

## Review notes / next
- **Audit the A/B→construct mapping** in `design.json.sidecar.json` — the `notes`-keyword heuristic is
  editable in `NOTES_MAP`; the panel should confirm each designed pair targets the intended crowd
  construct (most are daylight manips → `restorative`/`preference`, which is defensible but worth a look).
- **Stage-2 ASAP** (adaptive, high-information pair selection) is the natural follow-on: re-run the
  builder after the pilot with the aggregator's BT estimates to bias sampling toward informative pairs.
  The stage-1 balanced/connected design is what BT needs pre-pilot; the hook is noted in the builder.
- **Backend**: still a thin POST sink or CSV pooling for the pilot (unchanged from the S3 doc).
- **Gates unchanged**: images must be public-read on Drive (S0 backfill) before the console can load the
  real corpus; the aggregator works on CSVs regardless.
