# Integrating the cognitive-code adapters into the science pipeline

This folder adds an open-source visual-attribute bank (`cnfa_adapters/`) plus a
clean-room isovist engine, wrapped as a pipeline-compatible analyzer
(`cnfa_bridge.py`). It is **opt-in and non-invasive**: nothing here changes
`core.py`, `pipeline.py`, or the canonical run tags until you wire it in.

## Test it now (no database)

```bash
cd Image_Tagger_3.4.74_vlm_lab_TL_runbook_full
pip install -r backend/science/adapters/requirements-permissive.txt
python backend/science/adapters/run_cnfa_standalone.py path/to/room.jpg
```

This builds a real `AnalysisFrame(image_id=0, original_image=rgb)`, runs the
adapters, and prints the `cnfa.*` attributes it wrote to `frame.attributes`.
Verified: 49 permissive attributes land on the real frame.

## Wire into the pipeline (3 lines, opt-in)

In `backend/science/pipeline.py`:

```python
# 1) import
from backend.science.adapters.cnfa_bridge import CNFAAdapters

# 2) in SciencePipeline.__init__:
self.cnfa = CNFAAdapters(policy="commercial")   # owned/permissive build

# 3) in process_image(), alongside the other analyzers:
if getattr(self.config, "enable_cnfa_adapters", False):
    self.cnfa.analyze(frame)
```

And add one flag to `SciencePipelineConfig.__init__` (default off so canonical
runs are untouched):

```python
self.enable_cnfa_adapters = False
```

Because `add_attribute` is the same call the existing analyzers use, the new
`cnfa.*` values flow into `frame.attributes` (and `frame.metadata[key]`) exactly
like `complexity.*` or `color.*`.

## Two builds (owned vs research)

`CNFAAdapters(policy=...)` enforces the licence gate:

* `policy="commercial"` — **owned build**: permissive (MIT/BSD/Apache) adapters
  only. This is what you ship and own.
* `policy="research"` — adds the GPL / non-commercial model workers (DeepGaze,
  ResMem, pyiqa, material models) for validation. Never ship this build.

See `LICENSING.md` for the per-adapter position.

## Registering the new keys (when you activate it)

The repo enforces a three-file registry (`feature_stubs.py`,
`contracts/attributes.yml`, `features_canonical.jsonl`). The 49 permissive keys
(and the isovist/topology keys) are listed in
`cnfa_adapters/registry.py::STUB_TO_FUNCTION`. When you turn the bridge on for a
canonical run, add those keys to the three registry files (and move any that
were `cnfa.*` stubs out of `STUB_FEATURE_KEYS`) so `test_feature_registry_coverage`
stays green. Until then, keep `enable_cnfa_adapters=False` for canonical runs.

## The isovist engine (space-side)

`cnfa_adapters/spatial/` computes the full Benedikt isovist measure set and the
space-syntax visibility-graph measures (integration, connectivity, mean depth,
clustering, intelligibility) from an occupancy plan. It runs when the frame
carries a `plan` (a `Plan`) and a `viewpoint`; on image-only frames it no-ops.
This is the 3D-model / floor-plan path and the foundation for the wayfinding
layer (isovist-driven movement / max-visibility probabilistic paths).

```python
from backend.science.adapters.cnfa_adapters.spatial import Plan, annotate_plan
plan = Plan.from_image(floorplan_gray)          # dark ink = walls
attrs = annotate_plan(plan, viewpoint=(x, y))   # cnfa.spatial.* + cnfa.topology.*
```

## What maps to what

`cnfa_adapters/mapping.py` holds the proximal → distal → psychological/neural
mapping for every attribute, with an honesty flag (`established` /
`supported-with-debate` / `proxy` / `exploratory`). Run
`python -m backend.science.adapters.cnfa_adapters.mapping` to print it.
