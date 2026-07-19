# Codex S1B — Real-pyrtools per-subband entropy note

**Executed:** 2026-07-19 on macOS arm64  
**Repository:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest`  
**Backend:** real `pyrtools 1.0.10` in `/tmp/codex-pyrtools-s1`  
**Dump:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/SUBBAND_DUMP_MAC_2026-07-19.json`

## Result

The deterministic 120×160 horizontal-gradient fixture was processed through the vendored
`visual_clutter` reference and real `pyrtools.pyramids.SteerablePyramidFreq` with height 3 and
order 3. The JSON contains **14 entries per channel** for L, a, and b: 3 levels × 4 orientations,
plus `residual_highpass` and `residual_lowpass`. Each entry records shape, coefficient mean,
coefficient standard deviation, and the vendored package's entropy utility applied to the flattened
coefficient array.

The principal L-channel coefficient standard deviations by scale are:

| Level | Orientation 0 | Orientation 1 | Orientation 2 | Orientation 3 |
|---:|---:|---:|---:|---:|
| 0 | 0.166406898 | 0.058833723 | 0.0 | 0.058833723 |
| 1 | 0.867128499 | 0.306576221 | 0.0 | 0.306576221 |
| 2 | 4.792331144 | 1.694344925 | 0.0 | 1.694344925 |

The L residuals are:

| Residual | Shape | Mean | Standard deviation | Entropy |
|---|---:|---:|---:|---:|
| highpass | 120×160 | 0.0 | 0.123204208 | 1.189447906 |
| lowpass | 15×20 | 141.121724731 | 99.401893376 | 2.649158683 |

All full-precision values, including chroma channels, are in the JSON artifact. Some analytically
zero orientation bands receive nonzero entropy from the reference entropy/histogram routine; the
dump records this behavior verbatim rather than correcting it.

## Exact real-pyrtools source expressions

The following expressions are from the MIT-licensed `pyrtools 1.0.10` file
`pyrtools/pyramids/SteerablePyramidFreq.py` in the isolated environment.

### Initial hi0/lo0 transition and `twidth`

The constructor default is `twidth=1`. It coerces this to a positive integer, then uses the same
raised-cosine table for both complementary masks, centered at `-twidth/2`:

```python
twidth = int(twidth)
(Xrcos, Yrcos) = rcosFn(twidth, (-twidth/2.0), np.asarray([0, 1]))
Yrcos = np.sqrt(Yrcos)
YIrcos = np.sqrt(1.0 - Yrcos**2)
lo0mask = pointOp(log_rad, YIrcos, Xrcos[0], Xrcos[1]-Xrcos[0])
hi0mask = pointOp(log_rad, Yrcos, Xrcos[0], Xrcos[1]-Xrcos[0])
```

Thus the hi0/lo0 stage has a **one-octave transition** under the default call used here. There is
no separate hi0/lo0 width.

### Level ordering: `Xrcos` shifts before the bands

At the beginning of every level loop, real pyrtools shifts `Xrcos` down by exactly one octave.
Only then does it construct the level's `himask`:

```python
for i in range(self.num_scales):
    Xrcos -= np.log2(2)
    log_rad_test = np.reshape(log_rad, (1, log_rad.shape[0] * log_rad.shape[1]))
    himask = pointOp(log_rad_test, Yrcos, Xrcos[0], Xrcos[1]-Xrcos[0])
```

Since `np.log2(2) == 1`, the shift occurs **before** the oriented bands at each level, not after.
The band coefficients then use the current `lodft`, angular mask, and that level's `himask`:

```python
banddft = (-1j) ** self.order * lodft * anglemask * himask
band = np.fft.ifft2(np.fft.ifftshift(banddft))
```

### Crop and lowpass ordering: `log_rad` is never incremented

After all orientations for a level are emitted, pyrtools computes the centered half-size crop and
slices `log_rad`, `angle`, and `lodft` identically:

```python
dims = np.asarray(lodft.shape)
ctr = np.ceil((dims+0.5)/2).astype(int)
lodims = np.ceil((dims-0.5)/2).astype(int)
loctr = np.ceil((lodims+0.5)/2).astype(int)
lostart = ctr - loctr
loend = lostart + lodims

log_rad = log_rad[lostart[0]:loend[0], lostart[1]:loend[1]]
angle = angle[lostart[0]:loend[0], lostart[1]:loend[1]]
lodft = lodft[lostart[0]:loend[0], lostart[1]:loend[1]]
```

It then applies the complementary lowpass lookup using the **already shifted current `Xrcos`** and
the **cropped but numerically unchanged `log_rad`**:

```python
YIrcos = np.abs(np.sqrt(1.0 - Yrcos**2))
log_rad_tmp = np.reshape(log_rad, (1, log_rad.shape[0] * log_rad.shape[1]))
lomask = pointOp(log_rad_tmp, YIrcos, Xrcos[0], Xrcos[1]-Xrcos[0])
lomask = lomask.reshape(lodft.shape[0], lodft.shape[1])
lodft = lodft * lomask
```

There is **no `log_rad += 1`, `log_rad = log_rad + 1`, or equivalent increment** before either
lookup. Scale progression is represented solely by shifting `Xrcos` before each level. Therefore,
the shim expression that adds `1.0` to cropped `log_rad` is not source-equivalent and shifts the
next radial lookup by an additional octave.

## S1B conclusion

The remaining SE divergence is consistent with P4, and the source establishes the first exact fix:
remove the shim's `+ 1.0` from the recursive `log_rad` crop. The full P4 repair must also retain the
real `rcosFn` table and `pointOp` origins recorded in the S1 adjudication; changing the crop alone
does not establish equivalence. After those source-equivalent changes, rerun this same per-subband
dump on both backends and compare coefficients and entropy band by band before aggregating SE.

## Verification boundary

Verified: JSON validity, real-pyrtools version, deterministic fixture construction, 42 dumped
subbands/residuals, and the exact analysis-constructor expressions above. Not verified in this task:
a post-fix shim dump, because the prompt authorizes evidence artifacts only and expressly forbids
implementation changes.
