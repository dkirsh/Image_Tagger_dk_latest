# perceived_clutter 2AFC study — deploy & collect

## 2026-07-30 · companion to `clutter_study.html`

The study is a single self-contained HTML file (`clutter_study.html`, ~2 MB, 22 stimuli embedded as
data URLs, 84 randomized/counterbalanced pairs, reaction-time capture, 3 attention checks, consent +
role capture). No server, no dependencies, no browser storage. It runs by double-clicking.

## Run it (Stephan + the RA, now)

1. Send them the file (or the hosted link below). They open it, read consent, enter an identifier +
   role, and do ~8–12 minutes of "which room looks more cluttered?".
2. On the final screen they click **Download my responses (JSON)** and send you the file (named
   `clutter_<id>_<code>.json`). That's the zero-infrastructure path — bulletproof for known raters.

## Auto-collect (optional, and required for crowd)

Set one line — `submit_endpoint` — inside the HTML's `CFG` (near the top of the `<script>`) to a URL that
accepts a JSON POST. When set, the page uploads automatically *and* still offers the download as a
fallback. Two easy endpoints:

- **Google Apps Script web app** — a ~10-line `doPost(e)` that appends `e.postData.contents` as a row to a
  Google Sheet; deploy as "web app, anyone can access", paste that URL.
- **Cloudflare Worker** (or any tiny function) writing to KV / a database.

Your existing `adaptive_preference` backend also has a results endpoint if you'd rather keep it in-house.

## Host it (for remote raters / crowdsourcing)

It's one static file, so any static host works: **GitHub Pages** (drop it in a repo, enable Pages) or
**Netlify / Cloudflare Pages** (drag-and-drop). Then the link is shareable.

**Prolific** (recommended over MTurk for research quality): host the file, create a Prolific study
pointing at the URL, and use the **completion code** shown on the final screen as the code participants
paste back. Pay + approve in Prolific.

## Before paying strangers: IRB / consent

Lab members rating internal stimuli is typically low-risk, but **public paid crowdsourcing is
human-subjects data collection and needs IRB approval + a proper consent form first.** The page has a
minimal consent gate; swap in your approved language before any Prolific run. (This is a drafting aid, not
legal advice — confirm with your IRB.)

## What's in the starter set (and how to grow it)

22 interior scenes spanning low→high clutter (elevator, conference room, auditorium … → computer room,
kitchen, warehouse, TV studio). Scene names are **hidden from raters** to avoid priming. This is a
demonstration set; for a real validation, scale to ~30–40 stimuli and rebuild (stage more `corpus_L6`
interiors, re-run the build). Two design notes: your 164 photometric A/B "pairs" are *lighting*
manipulations, not clutter, so they aren't used here; and for validation we deliberately use a **fixed
random** comparison set (not the adaptive sampler), because adaptive selection would bias the tagger↔human
correlation.

## The analysis step (after data comes back)

1. Pool the JSON files → pairwise choices.
2. Fit a Thurstonian / Bradley-Terry **latent clutter scale** per rater and pooled (the
   `adaptive_preference` core already does this; or a short offline fit).
3. Once `faithful_clutter` scores exist for these 22 images, compute **Spearman ρ(faithful_clutter, human
   latent)** and pairwise accuracy with CIs → write the `perceived_clutter` entry in
   `validation_ledger.json` (verdict per the threshold rule).
4. A **VLM dry-run** (VLM as stand-in rater over the same 84 pairs) can pre-populate all of this before a
   single human runs — proving the loop and giving a provisional ρ. Ready to build on your go.

## Regenerate / modify

The instrument is generated from a config (stimuli + trial list). To change stimuli, counts, the
question, or wire the endpoint, re-run the build after staging new images. Keep the neutral achromatic
surround and keyboard controls — they're methodological, not cosmetic.
