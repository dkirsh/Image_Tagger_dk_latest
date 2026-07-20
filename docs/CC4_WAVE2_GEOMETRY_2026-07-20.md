# CC-4 — Wave-2 geometry S3 remainder (2026-07-20)

Built the S3 remainder and registered the two [FULL] ops with the batch. All AMBER by the Wave-2
rule (ride VP / plane-seg / inferred-plan machinery), all ABSTAIN (scalar=None, WITH absence
evidence) when their substrate is absent — never a fabricated number. Relative quantities only;
metric scale stays W2.7 (dormant, detector-gated). W2.7 room_scale_estimate remains deferred.

## Operators (cnfa_algs/wave2_geometry.py)
- **W2.2 `cnfa.geometry.ceiling_openness_relative`** — floor-to-ceiling angular span + ceiling
  elevation/area, horizon estimated from the plane split. RELATIVE only. Abstains: no ceiling.
  Honest caveat surfaced: the span saturates ~1.0 for full-frame interiors (ceiling at top edge,
  floor at bottom) — ceiling_elevation_deg + ceiling_area_fraction carry the residual signal.
- **W2.3 `cnfa.arch.double_height_space`** — continuous f2c span + double-height flag on an
  UNCALIBRATED threshold (needs_calibration=True; POE atria pair owed). Abstains iff W2.2 does.
- **W2.4 `cnfa.geometry.blind_corner_index`** — skeleton-corner isovist CONTRACTION (bounded Σ
  form): apex sees both arms, the tightest approach sees least; blind = apex-vs-approach contraction
  > τ. No transparency gate yet (glazed corners over-counted — Wave-3). Abstains: cornerless/tiny plan.
- **W2.5 `cnfa.geometry.barrier_permeability`** — VISUAL see-through (scalar) + PHYSICAL gap
  (extras), emitted SEPARATELY and NEVER averaged (self-test locks this). OPENING == aperture+glass
  proxy (Wave-3 glass gate owed). Abstains: no wall.
- **W2.8 `cnfa.arch.threshold_emphasized`** — emphasis = frame_contrast x aperture_height x
  frame-edge presence, for an aperture EMBEDDED in a wall (allowed to die in S3). Abstains:
  no wall-embedded aperture.
- **Registered with the batch**: W2.1 verticality_cues, W2.6 choice_richness_zones (both [FULL]).

## Integration
- registry.py: 7 new `_spec`s (all AMBER, replayable_tol); 6 image-ops added to MAY_LACK_SIGNAL
  (signal-absent abstention, sanctioned); MODEL_VERSION += reliableAreconcile+wave2geomCC4.
- annotator.py: 6 image ops wired in attr_fns (img/planes/Z/pg from the shared geometry pass);
  W2.6 wired as a dict->record compound. Registry now 68 predicates (was 61).
- run_stage.py: report line hardened for signal-absent abstentions (they carry absence_evidence,
  not missing_inputs) — was a display KeyError.

## Verification (sandbox, scikit-image present)
- Module self-test `python3 -m cnfa_algs.wave2_geometry`: PASS — orderings (colonnade>shelving,
  tall>shallow ceiling, glazed>solid permeability, embedded-doorway>free-standing, L-corridor>
  straight blind), negative-control abstentions, determinism x2.
- `annotation_socket/tests/test_wave2_geometry.py`: PASS — registration/AMBER, abstain-with-evidence
  contract, permeability-axes-not-averaged, determinism.
- Real-image annotate: all 7 resolve SCORED-or-ABSTAINED, unknown=0.
- **Full 68-predicate stage smoke** (3 real images): GREEN=0 AMBER=3 RED=0; 48/48 scored, unknown=0,
  replayed, problems=[]; negative control RED+rejected; idempotent; [W:] boundary holds.

## Owed (honest)
- W2.2/W2.3 threshold + saturation calibration on the POE high/low-ceiling pair + Drive atria (L6).
- W2.4/W2.5 transparency (glass) gate arrives with the Wave-3 detector (CC-5/DEC-1).
- M1' sufficient-statistic bindings for the wave-2 ops (optional; geometry ops currently M1'-less,
  consistent with wave-1 geometry) — add when the geometry M1' classes land.
