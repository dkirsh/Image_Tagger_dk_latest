# C01 — registry entry + annotator wiring (apply to the socket)

## 1. `annotation_socket/registry.py` — add one predicate (in the plan-metrics-from-plan-alone block)

```python
    _spec("C01.triangulation_ignition", "plan_metric", PLAN, "replayable_tol", "AMBER",
          "COMPOUND: landmark_salience x C1 integration x co-location gate to the desire-line "
          "ridge; anchor off the ridge -> ~0; registration-unconfident -> UNKNOWN (never guessed). "
          "Its OWN social field — excluded from score_layout aggregation (double-count guard)."),
```

`requires = PLAN` (Tier-B inferable), so C01 is applicable on every image unit; the
anchor/registration handling is internal tri-state, exactly like the other plan metrics.

## 2. `annotation_socket/annotator.py` — one binding in `plan_fns`'s sibling path

C01 needs the shared geometry (`planes, Z, pg, chain, geom_conf`) and the cached `vga()`, so it
is bound as a full-record producer rather than a scalar tuple. Add, just after `plan_fns`:

```python
    from .predicates import triangulation as TRI
    compound_fns = {
        "C01.triangulation_ignition":
            lambda: TRI.compute(img, planes, Z, pg, vga(), geom_conf, chain),
    }
```

and in the predicate loop, before the `else: unknown(...)` branch:

```python
            elif pid in compound_fns:
                scores.append(compound_fns[pid]())      # returns a full scored/zero/unknown record
```

`TRI.compute` already routes through the `derivation` chokepoint (returns `scored`/`unknown`
with a valid evidence chain), so no other change is needed. Bump `registry.MODEL_VERSION` on
first ship (replay-verification correctly rejects old accepted re-derivations otherwise).

## 3. `score_layout.py` — the double-count guard (panel caution)

Exclude `C01.*` from the aggregate valence/profile scorer. C01 reuses `landmark_salience` and
`C1 integration`, which already feed the aggregate; adding C01 back double-weights them.
C01 is consumed only as its own social field (and by the region-A-vs-B engine), never summed
into the general score.
