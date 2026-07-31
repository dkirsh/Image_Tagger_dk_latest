# Teaching sets — draft v1 and notes

**2026-07-30.** First-draft graded exemplars (low / intermediate / high / ambiguous) for the four
image-measurable species, auto-selected by percentile on each species' hypothesis measure over 300 SAVOIAS
interior + scene images. Contact sheet: `teaching_sets_contact.png`. Selections + values:
`teaching_sets_manifest.json`. Reference measure algorithms (portable numpy/cv2, for Codex):
`measures2.py`.

## Method

For each species, rank the pool by its hypothesis measure and take exemplars at the ~6th / 50th / 94th
percentile (low / intermediate / high). The **ambiguous** exemplar is a near-median case that is *extreme on
a competing species' measure* — i.e., an image built to invite confusion between species (the item the
discrimination gate must catch).

| species | hypothesis measure | status |
|---|---|---|
| surface_density | contrast energy (fine congestion) | usable draft |
| arrangement_disorder | coarse-scale compressibility | **weak — see caveat 2** |
| variety | distinct-colour count | usable draft |
| textural_discomfort | mid-high spectral energy (1/f departure) | usable draft |
| semantic_incongruity | none (late/VLM) | **manual/synthetic curation** |
| concealed_order | none (observer-dependent) | **framing-based, not a measure** |

## Caveats — these sets are hypotheses to be corrected, not answer keys (per Codex #8)

1. **Scene type varies within a column.** The auto-selection lets scene type (skyline vs bedroom vs garden)
   ride along with the species. For clean teaching, exemplars within a species should be *matched in scene
   type* so only the species varies. Next pass: curate matched-scene triples.
2. **`arrangement_disorder` — REBUILT BY HAND (2026-07-30).** The coarse-compressibility auto-selection
   conflated natural texture with layout disorder (it flagged foliage as "disordered"). Retired for
   teaching. Replaced with `arrangement_disorder_schematic.png`: top-down layouts holding the *same
   furniture* constant and varying only placement — low=regimented, intermediate=slightly off,
   high=scattered, ambiguous=clustered-into-conversation-groups (non-grid but intentional — the discrimination
   trap). This isolates layout from texture/colour. Still to do: real-photo anchors (regimented rooms like
   auditorium/conference as low; a disarranged room as high — curate with Stephan). The *measure* still needs
   replacing (segment large elements → score placement regularity); flagged for Codex's lane.
3. **Two species carry no image measure.** `semantic_incongruity` needs curated or composited out-of-place
   objects; `concealed_order` is taught by expert-vs-novice framing of the *same* image. Neither is
   auto-selectable — both are human-curated by design.

## Next steps (cowork)

- Curate matched-scene exemplar triples for surface_density, variety, textural_discomfort.
- Replace the arrangement_disorder measure or hand-pick its exemplars (furniture layout, not texture).
- Build the two manual species' sets with Stephan (semantic_incongruity composites; concealed_order framing
  pairs).
- Feed the whole draft to Stephan/David for approval + objection — the first exercise of the objection loop.
