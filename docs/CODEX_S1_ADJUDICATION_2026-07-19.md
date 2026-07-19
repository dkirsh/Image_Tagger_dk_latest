# Codex S1 Reference Adjudication — real pyrtools versus `_pyrtools_min`

**Executed:** 2026-07-19 on macOS arm64  
**Repository:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest`  
**Branch:** `cnfa-algs-2026-07-14`  
**Required numerical artifact:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CLUTTER_REFERENCE_MAC_2026-07-19.json`

## Verdict

**SHIM DIVERGES.** The initial comparison reports ten values outside the declared 2% relative
tolerance. The Feature Congestion divergence is caused by P2: the shim uses a unity-sum binomial-5
Gaussian filter, whereas real pyrtools 1.0.10 uses `parse_filter('binom5', normalize=False)`, whose
coefficients sum to `sqrt(2)`. Applying that exact correction in memory removes every FC and FC-layer
mismatch. The remaining Subband Entropy differences localize to P4, where the shim's raised-cosine
lookup table and recursive frequency-pyramid construction differ from real pyrtools.

The shim must remain AMBER until P2 and P4 are corrected and this harness passes on decode-identical
inputs. P1 is consistent with the real `reflect1` convention. P3 is not the source of the observed FC
failure after P2 correction, although exact expansion-edge equivalence was not exhaustively proved.

## Environment and commands

I installed `pyrtools` in the isolated environment `/tmp/codex-pyrtools-s1`; no repository or system
package files were changed. Installed version: **pyrtools 1.0.10**. OpenCV and scikit-image were added
to that environment because the unchanged reference harness imports them.

Commands executed from `/Users/davidusa/REPOS/Image_Tagger_dk_latest`:

```text
python3 -m venv /tmp/codex-pyrtools-s1
/tmp/codex-pyrtools-s1/bin/pip install pyrtools opencv-python scikit-image
PYTHONPATH=. /tmp/codex-pyrtools-s1/bin/python scripts/reference_clutter_compare.py \
  --backend real --env mac --out docs/CLUTTER_REFERENCE_MAC_2026-07-19.json
/tmp/codex-pyrtools-s1/bin/python scripts/reference_clutter_compare.py \
  --compare docs/CLUTTER_REFERENCE_MAC_2026-07-19.json \
  docs/CLUTTER_REFERENCE_SANDBOX_2026-07-19.json
```

The real-backend run wrote eight entries. The comparator skipped two JPEGs because their decoded
pixel hashes differed between environments; this is the intended L5 safeguard, not an agreement.

## Prescribed comparison output

Every `MISMATCH` row, verbatim and in emitted order:

```text
MISMATCH Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg :: se_raw: 3.285035 vs 3.394321 (rel 0.0333)
MISMATCH Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg :: layer:contrast: 0.077065 vs 0.074848 (rel 0.0288)
MISMATCH Example Images/Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg :: layer:contrast: 0.079663 vs 0.077332 (rel 0.0293)
MISMATCH fixture:blank :: se_raw: 1.40226 vs 0.519805 (rel 0.6293)
MISMATCH fixture:clutter :: fc_raw: 5.409659 vs 4.918198 (rel 0.0908)
MISMATCH fixture:clutter :: se_raw: 2.295044 vs 2.520123 (rel 0.0981)
MISMATCH fixture:clutter :: layer:color: 0.29807 vs 0.223438 (rel 0.2504)
MISMATCH fixture:clutter :: layer:contrast: 0.081195 vs 0.07235 (rel 0.1089)
MISMATCH fixture:gradient :: se_raw: 1.79836 vs 2.142115 (rel 0.1911)
MISMATCH fixture:gradient :: layer:contrast: 0.001997 vs 0.001363 (rel 0.3175)
```

The adjudication line verbatim:

```text
ADJUDICATION: 10 mismatches — shim diverges, check P1-P4
```

The skipped rows were:

```text
skip (decode differs): Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg
skip (decode differs): Example Images/Office-Grade-1-1536x838.jpg
```

## Localization

### Feature Congestion: P2 is responsible

Real pyrtools reports the default Gaussian filter as:

```text
[0.08838835, 0.35355339, 0.53033009, 0.35355339, 0.08838835]
sum = 1.4142135623730951
```

That is `[1, 4, 6, 4, 1] * sqrt(2) / 16`. The shim's `_BINOM5` is
`[1, 4, 6, 4, 1] / 16`, sum 1. P2 therefore copied the familiar smoothing kernel but missed
pyrtools' non-normalized filter amplitude. This error propagates through Gaussian pyramid levels
and changes local color covariance and contrast magnitudes.

I tested the exact correction without changing repository files:

```python
from cnfa_algs import _pyrtools_min as p
p._BINOM5 = p._BINOM5 * np.sqrt(2.0)
```

The corrected shim was run through the same eight-entry harness. All FC, color, contrast, and
orientation values then agreed with real pyrtools within 2%. The residual comparator output
contained four SE mismatches and no FC/layer mismatches. This experimentally isolates the FC error
to P2.

**Exact P2 fix:** define `_BINOM5` as
`np.array([1., 4., 6., 4., 1.]) * (np.sqrt(2.0) / 16.0)`. Retain level 0 as the original image.
For exact source parity, apply the horizontal correlation first and the vertical correlation
second, as `GaussianPyramid._build_next` does, although separability made order immaterial in the
tested cases.

### Subband Entropy: P4 is responsible

`se_raw` is independent of the FC layer combination and remains discrepant after the P2 correction.
Inspection of real `SteerablePyramidFreq` and `tools.utils.rcosFn` reveals four concrete P4
differences:

1. **Raised cosine.** Replace `_rcos_table` with the pyrtools construction:

   ```python
   sz = 256
   X = np.pi * np.arange(-sz - 1, 2) / (2 * sz)
   Y = values[0] + (values[1] - values[0]) * np.cos(X) ** 2
   Y[0] = Y[1]
   Y[sz + 2] = Y[sz + 1]
   X = position + (2 * width / np.pi) * (X + np.pi / 4)
   ```

   The shim instead places the table over `position + width*(-1..257)/256` and evaluates another
   cosine expression. Its transition is shifted relative to pyrtools.

2. **Frequency grid.** Construct `xramp, yramp` exactly as real pyrtools:

   ```python
   xramp, yramp = np.meshgrid(np.linspace(-1, 1, N + 1)[:-1],
                              np.linspace(-1, 1, M + 1)[:-1])
   ```

3. **Angular lookup.** For the real-valued pyramid, use
   `Ycosn = sqrt(const) * cos(Xcosn)**order` without the shim's half-plane zeroing. Apply `pointOp`
   to the unwrapped `angle` with origin `Xcosn[0] + pi*b/num_orientations`; do not wrap each angular
   difference into `[-pi, pi]` before lookup.

4. **Recursive lowpass.** After cropping `log_rad`, do **not** add `1.0`. Real pyrtools shifts
   `Xrcos` down one octave on each iteration, crops `log_rad` unchanged, computes
   `lomask = pointOp(log_rad, YIrcos, Xrcos[0], increment)`, and multiplies the cropped `lodft` by
   that mask. The shim's `log_rad = cropped_log_rad + 1.0` changes the radial bands.

**Exact P4 recommendation:** port the analysis-only constructor statements from pyrtools 1.0.10
verbatim for grid creation, `rcosFn`, `pointOp` origins, angular masks, crop bounds, and lowpass
masking. Preserve only the small compatibility wrapper that exposes the required coefficient keys.
Do not attempt to repair P4 by tuning entropy output: the error is in the pyramid coefficients.

### P1 and P3

- **P1:** NumPy `mode='reflect'` excludes the boundary sample and matches the tested meaning of
  pyrtools `reflect1` (reflection through the edge sample while maintaining subsampling parity).
  No independent mismatch remained attributable to P1 after the P2 correction.
- **P3:** Real `upConv` performs expansion/convolution without automatic gain compensation, as P3
  states. The vendored package's unity-sum collapse filter therefore remains attenuated relative to
  the old MATLAB expansion. The FC comparison after P2 correction passed, so P3 does not explain
  this adjudication's FC mismatches. Exact edge pixels of the C expansion routine were inspected but
  not exhaustively proven equal to the SciPy implementation; this boundary remains explicitly
  unverified.

## DT-1 on real pyrtools

DT-1 is confirmed. With real pyrtools 1.0.10 and the identical vendored reference, Farnsworth
(foliage-framed) ranks above the cluttered industrial office on both measures:

| Image | FC raw | SE raw |
|---|---:|---:|
| Industrial office | 4.466692 | 3.285035 |
| Farnsworth House | 4.692364 | 3.453811 |

Thus the DT-1 result is not caused by the shim. It is a domain-transfer result of the reference
measure: vegetation's color, contrast, and orientation variation is counted as clutter. The
appropriate adjudication remains the labeled interior corpus at L6.

## Completion boundary

Verified here: real-backend execution, version, eight JSON entries, comparison at the repository's
2% gate, numerical P2 intervention, source-level P1–P4 inspection, and DT-1 values. Not verified:
Mac-to-sandbox values for the two decode-skipped JPEGs, exhaustive equality of every edge pixel in
`upConv`, or L6 construct validity on labeled interiors.
