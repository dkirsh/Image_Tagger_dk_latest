# L6 Corpus Retrieval Index — function spec + prototype (2026-07-21, Cowork/Opus)

David's ask (2026-07-21): the L6 corpus on Google Drive has no retrieval index; spec the index
*function* first, then build it. Done — spec below, prototype shipped (`scripts/build_corpus_index.py`
→ `corpus_L6/index.json` + `corpus_L6/index.html`).

## Function — what the index must let us retrieve
Three audiences, one index:
1. **Viz-attribute testing** — "give me N interiors filtered by type / resolution / licence / A/B
   pairing, and (once scored) by computed attribute values" (e.g. high clutter, low openness, biophilic).
2. **Students** — browse varied *examples of a space type* (corridor, atrium, classroom, …) as stimuli.
3. **Architects** — find examples *meeting a spec* (e.g. high-prospect + daylit + biophilic interiors).

## Retrieval dimensions (implemented)
Per-image record joins `manifest.csv` (category, `pair_id`, `pair_expected_better`, notes) with
`_provenance.csv` (source, licence, `width/height`, `sha256`, `gdrive_path`, class-`query`), enriched
with two derived fields:
- **`arch_type`** — the fine room/space class (67 MIT-Indoor classes + SUN397 indoor classes), from
  the provenance `query` (fallback: parse trailing `_<class>.png`).
- **`space_family`** — a browsable grouping (`circulation / work / learning / domestic / hospitality /
  retail / civic / industrial / other`) so students/architects can browse without knowing the 67 classes.

Queryable/facetable: `filename, space_family, arch_type, category (interiors/pairs/collections/niches),
source, license, px_bucket (>=2048 / 1024-2047 / 512-1023 / <512), on_drive, pair_id,
pair_expected_better`, free-text search over filename+type+notes, and an **optional `scores.csv` join**
(`filename,<attr>=value,…`) — the hook so that once `annotate` has run over the corpus you can retrieve
by *computed viz-attribute* directly (the primary audience-1 use).

## Prototype output (current snapshot: 530 images)
- `index.json` — `{summary, records[]}`; `summary.facets` are the retrieval facets with counts.
  Programmatic retrieval = filter `records` on any dimension; join scores by filename.
- `index.html` — self-contained browsable index: filter dropdowns per facet + search + sort; A/B pair
  badges; Drive badge. Thumbnails render when `window.IMG_BASE` is set to the Drive/CDN public base
  (else metadata-only cards). Verified headless: filters work (circulation → 21), 0 JS errors.
- Snapshot facets: space_family + arch_type populated; **161/530 on Drive** (the 200-row Drive backfill
  is still owed — see S0); 82 A/B pairs; sources mit_indoor67 219 / sun397 142 / curated 169.

## Regenerate (corpus is still growing)
`python3 scripts/build_corpus_index.py [--scores corpus_L6/scores.csv]` — read-only on the corpus,
rebuilds both outputs. Re-run after collection finishes and after the Drive backfill so `on_drive`
and thumbnails are complete. `index.json/html` are derived artifacts (not committed; regenerate).

## Next (to make it fully serve audience 1 + public thumbnails)
1. **Score join** — run `annotate` over the corpus → `corpus_L6/scores.csv` (filename + the 68
   predicates' scalars/tiers) → the index gains attribute-range retrieval + sorting. (Gated on the
   corpus being stable + the compute pass.)
2. **Public image URLs** — the console + the index thumbnails need Drive public-read links (or a CDN
   mirror). Depends on the S0 Drive backfill (own client_id) completing.
3. **Optional server mode** — a thin query API over index.json for large-scale programmatic retrieval;
   the static HTML suffices for browse + pilot.
