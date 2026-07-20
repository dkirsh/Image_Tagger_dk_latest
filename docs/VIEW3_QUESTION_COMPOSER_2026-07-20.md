# VIEW-3 — Question-driven composer (2026-07-20)

The question -> display-composition -> rendered-view pipeline (Sprint VIEW). Consumes ONLY the
record + sidecar (viewer contract: never recompute). `viz/question_composer.py`.

## The ≠-mind separation (the point of the task)
The composer is ADVISORY-ONLY, exactly like the inference judge. It SELECTS registered layers and
WRITES prose, but every number in the narrative is substituted FROM THE RECORD by `_fill()` — it
never invents or alters a score. The optional `compose(..., llm=callable)` hook lets an LLM curate
layer ORDER/SELECTION and rewrite prose, but its output is re-validated: any numeric claim not
present in the record is stripped to `[redacted:unverified]`. The renderer reads scores ONLY from
the record. An LLM therefore cannot change one scored value — only decide what to SHOW and how to
EXPLAIN. Fail-closed: an abstained/absent predicate is reported as such (with its named missing
inputs), never papered over. (Self-test proves a rogue LLM injecting "999.999 dB" gets it redacted.)

## Pipeline
- `classify_question(q)` -> class by keyword score (noise / clutter / biophilia / wayfinding /
  privacy / overview default). Registry-aware: each class names the REGISTERS + predicates it lights.
- `compose(question, record, manifest)` -> display-composition JSON:
  {question, question_class, layers[{key,group,reason}], focus[{kind,bbox,label}],
   narrative[{text,anchor}], how_to_read[], provenance}. Only references layers that EXIST in the
   sidecar; focus = matching semantic zones + the class predicates' evidence bboxes.
- `render_question_view(composition, sidecar_dir, unit_id, record)` -> ONE self-contained HTML
  (reuses the VIEW-1 overlay machinery): base + composed layers only, focus boxes, and a narrative
  panel whose anchored lines toggle the referenced layer on click.

## Acceptance test (David's example) — PASS
"effects of street noise on the foyer" -> class=noise; layers = acoustics (SPL/huddle) + semantic
zones + base; focus = the foreground circulation zone (foyer/entrance proxy); narrative leads with
the ACTUAL street-noise value (e.g. "street noise intrusion = 0.145 (AMBER)") and then honestly
reports the other acoustic predicates as UNSCORED with their named missing declared inputs. Renders
to a self-contained ~0.3 MB HTML. Template library covers noise/clutter/biophilia/wayfinding/privacy.

## Supporting change
- `viz/field_sidecars.py`: `layer_group` now routes cnfa.geometry.*/cnfa.arch.*/cnfa.spatial.*/
  cnfa.plan.*/C1-4 to the space_geometry register (CC-4 wave-2 ops land in the right layer group);
  `build_sidecar` now also writes `<unit>.record.json` so VIEW-3 consumers annotate ONCE.

## Owed
- Live SPL/huddle layers require the unit to carry street-noise declared inputs (outdoor_leq +
  facade_spec) — CC-3 channel; on a bare image the composer honestly shows the abstain + how to
  supply them. VIEW-4 A/B compare + VIEW-5 server sliders remain queued.
