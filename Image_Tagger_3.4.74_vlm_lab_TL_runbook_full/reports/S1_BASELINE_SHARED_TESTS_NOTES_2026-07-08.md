# S1 Baseline Shared Test Notes

Date: 2026-07-08  
Repo: Image_Tagger_dk_latest  
Active app root: Image_Tagger_3.4.74_vlm_lab_TL_runbook_full  

## Command attempted

    PYTHONPATH=. pytest tests/test_feature_registry_coverage.py tests/test_science_pipeline_smoke.py -v

## Result

BLOCKED / FAILING BASELINE

## Details

### tests/test_science_pipeline_smoke.py

Collection was blocked because the light MPIB virtual environment created from requirements-install.txt does not include SQLAlchemy.

Observed error:

    ModuleNotFoundError: No module named 'sqlalchemy'

This appears to be an environment/dependency issue rather than an S1 implementation failure.

### tests/test_feature_registry_coverage.py

The registry coverage test ran separately and failed on pre-existing dangling registry keys.

Representative dangling keys include:

* affordance.L059
* affordance.L059_norm
* affordance.L079
* affordance.L079_norm
* affordance.L091
* affordance.L091_norm
* affordance.L130
* affordance.L130_norm
* affordance.L141
* affordance.L141_norm
* spatial.room_function.bathroom
* spatial.room_function.bedroom
* spatial.room_function.home_office
* spatial.room_function.kitchen
* spatial.room_function.living_room
* style.bohemian
* style.farmhouse
* style.industrial
* style.japandi
* style.mid_century_modern

## Interpretation

These are baseline blockers observed before starting Sprint S1 implementation work. Next step is to inspect the feature registry coverage test and the existing feature stub registry to determine whether these keys should be backed by compute functions, stubs, or registry updates.
