# Feature Registry Baseline Stub Report

Date: 2026-07-08  
Repo: Image_Tagger_dk_latest  
Active app root: Image_Tagger_3.4.74_vlm_lab_TL_runbook_full  

## Initial issue

The feature registry coverage test failed before Sprint S1 implementation work because several canonical registry keys were neither computed through frame.add_attribute(...) nor explicitly listed as intentional stubs.

Command:

    PYTHONPATH=. pytest tests/test_feature_registry_coverage.py -v

Initial result:

    FAILED

Representative dangling keys included:

* affordance.L059 and related normalized affordance outputs
* spatial.room_function.* room classifier outputs
* style.* visual style classifier outputs

## Interpretation

These keys are not part of the deterministic Sprint S1 direct-statistics implementation. They are existing canonical registry entries for affordance, room-function, and style classifiers. Since they are not currently computed in backend/science via frame.add_attribute(...), they should be marked as intentional stubs rather than treated as accidental dangling keys.

## Patch

Updated backend/science/feature_stubs.py to include the missing baseline registry keys in STUB_FEATURE_KEYS.

## After-patch verification

Command:

    PYTHONPATH=. pytest tests/test_feature_registry_coverage.py -v

Result:

* 1 test collected.
* 1 passed.

Combined baseline command:

    PYTHONPATH=. pytest tests/test_mpib_low_level.py tests/test_feature_registry_coverage.py -v

Combined result:

* 4 tests collected.
* 4 passed.

Status: ACCEPTED
