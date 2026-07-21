# MPIB Verification Patch Report

Date: 2026-07-08  
Repo: Image_Tagger_dk_latest  
Active app root: Image_Tagger_3.4.74_vlm_lab_TL_runbook_full  

## Initial verification

Command:

    PYTHONPATH=. pytest tests/test_mpib_low_level.py -v

Initial result:

* 3 tests collected.
* 2 passed.
* 1 failed.
* Failing test: tests/test_mpib_low_level.py::test_extract_mpib_features_emits_full_key_set
* Failure reason: expected at least 18 finite MPIB feature values, but observed 17.

## Diagnosis

The full 20-key MPIB feature set was emitted, but three edge-density fields were non-finite:

* edge_density_straight
* edge_density_nonstraight
* edge_density_total

Directly calling get_edge_density() showed the underlying error:

    TypeError: cannot unpack non-iterable numpy.int32 object

The issue came from the Hough line output shape returned by the installed OpenCV version. The code assumed line[0] always contained four coordinates. On this environment, that assumption failed.

## Patch

Updated backend/science/math/mpib_low_level.py so each Hough line is flattened before coordinate unpacking:

    coords = np.asarray(line).reshape(-1)
    if coords.size < 4:
        continue
    x1, y1, x2, y2 = coords[:4].astype(int)

This keeps the same edge-density logic but makes the coordinate extraction robust to OpenCV output shape differences.

## After-patch verification

Command:

    PYTHONPATH=. pytest tests/test_mpib_low_level.py -v

Result:

* 3 tests collected.
* 3 passed.

Status: ACCEPTED
