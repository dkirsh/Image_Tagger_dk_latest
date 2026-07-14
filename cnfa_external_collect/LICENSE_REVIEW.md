# CNFA External Tool License Review

Date: 2026-07-14

Scope: HorizonNet, depthmapX, SpatialLM, and Radiance/DAYSIM install blockers for
local Image_Tagger_dk CNFA research use. This file is not legal advice. It is a
triage record so David can decide what requires a legal call before packaging,
redistribution, paid use, or publication of derived assets.

| Tool | License | Copyleft/commercial restriction | ok-for-our-research-use? |
| --- | --- | --- | --- |
| HorizonNet | Code is MIT (`cnfa_external/repos/HorizonNet/LICENSE`). Pretrained weights are separate: the README says downloading weights means accepting the training datasets' licenses and terms. | Code has permissive MIT obligations. Weight use is not fully resolved because the dataset terms travel with the downloaded checkpoints; do not redistribute weights or derived packaged model bundles until those dataset terms are reviewed. | Yes for local research code use. FLAG for David/legal before redistributing weights, bundling checkpoints, or using output commercially. |
| depthmapX | GPLv3; bundled/used Qt5 is LGPLv3 (`cnfa_external/repos/depthmapX/releases/licenses.txt`). | GPLv3 is strong copyleft for redistribution of derivative/combined binaries. Local use is fine; redistribution inside a proprietary or closed bundle needs a legal decision. | Yes for local research runs. FLAG before redistribution, app bundling, or commercial delivery. |
| SpatialLM | Mixed. Local repo includes Llama 3.2 Community License (`cnfa_external/repos/SpatialLM/LICENSE.txt`). README says Qwen-derived model is Apache-2.0 at the base; SpatialLM1.1 model weights are CC-BY-NC-4.0; code built on Pointcept is Apache-2.0; TorchSparse is MIT. The local HF mirror `weights/SpatialLM1.1-Qwen-0.5B/README.md` declares `license: cc-by-nc-4.0`. | The current local model weights are non-commercial. Llama variants also carry Meta attribution, acceptable-use, redistribution, and 700M-MAU commercial-license terms. CUDA/PyTorch install is technically heavy and should remain manual. | Yes for non-commercial local research. FLAG for any commercial use, redistribution, public hosted service, or Llama-weight use. |
| Radiance | Radiance Software License v2.0 from radiance-online.org/download-install/license. | Permissive source/binary redistribution with copyright/license retention and no endorsement by UC/LBNL/DOE/contributors. Enhancements publicly shared without a separate written license grant broad rights to LBNL. | Yes for local research. FLAG before redistributed binaries or public derivative packages. |
| DAYSIM | Public MITSustainableDesignLab/Daysim repository carries Radiance Software License v1.0 in `License.txt`. | Permissive-like redistribution with attribution/acknowledgment and name-use restrictions; older license terms differ from current Radiance v2.0. | Yes for local research. FLAG before redistribution or bundling, because the public repo license is old Radiance v1.0. |

## Sources read

- HorizonNet local license: `cnfa_external_collect/cnfa_external/repos/HorizonNet/LICENSE`
- HorizonNet README weight notice: `cnfa_external_collect/cnfa_external/repos/HorizonNet/README.md`
- depthmapX local license notice: `cnfa_external_collect/cnfa_external/repos/depthmapX/releases/licenses.txt`
- depthmapX README: `cnfa_external_collect/cnfa_external/repos/depthmapX/README.md`
- SpatialLM local Llama license: `cnfa_external_collect/cnfa_external/repos/SpatialLM/LICENSE.txt`
- SpatialLM README license section: `cnfa_external_collect/cnfa_external/repos/SpatialLM/README.md`
- SpatialLM local model card: `cnfa_external_collect/cnfa_external/weights/SpatialLM1.1-Qwen-0.5B/README.md`
- Radiance upstream license: `https://www.radiance-online.org/download-install/license`
- DAYSIM upstream license: `https://github.com/MITSustainableDesignLab/Daysim/blob/master/License.txt`

## Manual-install scripts

Prepared but not run:

- `cnfa_external_collect/manual_install/install_horizonnet_weights.sh`
- `cnfa_external_collect/manual_install/install_depthmapx.sh`
- `cnfa_external_collect/manual_install/install_spatiallm_env.sh`
- `cnfa_external_collect/manual_install/install_radiance_daysim.sh`

Each script is guarded: without `--run` it prints the intended manual steps and
exits. This lets `bash -n` validate syntax and lets David inspect the procedure
before doing network, CUDA, or binary-install work.
