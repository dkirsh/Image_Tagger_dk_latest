# S3 — 2AFC Labeling Console (built 2026-07-21, Cowork/Opus, overnight)

`viz/labeling_console.html` — a self-contained (zero external assets) construct-validation console
implementing Part C of the L6 program, **revised per the 2026-07-21 panel findings**. Verified
end-to-end in headless Chromium: consent → instructions → gold qualification → rating loop → done,
all screens transition, full queue completes, **0 JS console errors**, completion code emitted.

## What it does
- **2AFC pairwise** as the workhorse (scale-free → Bradley-Terry downstream) + a small **anchored
  Likert** battery on a shared anchor set (fixes the BT origin / licenses a hedonic zero) — this is the
  psychometrics panel's budget correction (don't spend 90% on between-worker Likert).
- **Revised construct set** (env-psych panel): `clutter`, `openness`, `restorative` (PRS-flavoured
  wording), `mystery` (ADDED — the human target for blind_corner / barrier_permeability), `refuge`
  (ADDED — validates prospect-refuge as a *pair*), `preference` (criterion). **Wayfinding-ease DROPPED**
  (not judgeable from a single photo); **calm/stress folded into affect** (Russell valence+arousal in
  the Likert battery: `affect_val`, `affect_aro`; restorativeness `prs_away`, `prs_fascin`).
- **QC:** gold qualification (must pass ⅔; independent answers incl. an identical-image → "can't tell"
  catch), interleaved gold/attention every 5 trials, **L/R physical-position counterbalancing** +
  per-worker **side-bias** capture, **min-time guard** (fast clicks rejected + flagged), RT capture,
  a **confidence** (sure/unsure) toggle, keyboard `←/→/space`.
- **No browser storage** (in-memory only, per artifact rules). Each judgment either **POSTs** to a
  configurable endpoint or is **exported as CSV** matching the `human_labels.csv` schema.

## Data schema (one row per judgment)
`worker_id, session_id, kind(pair|likert), pair_id, construct, left_item, right_item, chosen_side,
chosen_item, response, confidence, rt_ms, is_gold, gold_answer, gold_pass, item, likert_key,
ua_desktop, ts_utc`  + a session-meta header line (`side_bias`, `gold_pass_rate`).

## Wiring to the real corpus
Set `CONFIG.imageBaseUrl` (via the consent-screen operator field) to the Drive/CDN public base; load a
`design.json` (schema documented at the bottom of the HTML). Items are referenced by corpus filename.
Absent a design.json, an **in-canvas procedural demo** (6 interiors with controllable busyness/
brightness/openness, defensible golds) runs so the flow is clickable offline.

## Still to build (offline, feeds the console)
- **`design.json` generator**: two-stage **active pairwise sampling (ASAP)** over the 200 singletons +
  inject the 80 designed A/B pairs as high-information edges + long-range anchors for BT graph
  connectivity (psychometrics panel). Random-sparse is 1.5–3× less efficient and risks a disconnected/
  non-identifiable graph.
- **Aggregation**: regularized/Bayesian Bradley-Terry (separation-safe prior) + **Davidson tie model**
  ("can't tell" = tie, don't drop) → `corpus_L6/human_labels.csv` with per-item scores + cluster-
  bootstrap CIs.
- **Backend**: a thin POST sink (Flask/Cloud Run) or CSV pooling for the pilot.
- **Pilot on Prolific/CloudResearch** (40–60/platform), then the campaign. Corpus images must be
  public-read on Drive (or a CDN mirror) for the console to load them.

## Research connectors surfaced (2026-07-21)
Suggested in the app for the literature track: **Consensus**, **alphaXiv** (arXiv full-text),
**Scholar Gateway**, plus **PubMed** / **bioRxiv** (authless) are in the registry. Connect + enable in
chat to let future sessions pull primary sources directly instead of via web search.
