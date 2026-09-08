# Test scope and open application decisions — 2026-09-08

## Verified test commands

The repository root contains several systems with different dependency contracts. The
default root command runs the suites named in `pytest.ini`:

```bash
python3 -m pytest -q
```

Verified on `main` after commit `d2462ecc`: **251 passed, 0 failed**.

The production loop can be tested independently:

```bash
python3 -m pytest -q loop/tests
```

Verified on the same tree: **65 passed, 0 failed**.

The root suite contains `tests/`, `loop/tests/`, `validation/`,
`annotation_socket/tests/`, and `TRS_v1.1/tests/`. Inclusion in this test contract means
only that these tests run in the repository's ordinary Python environment; it does not
change the product status of the directories that contain them.

Directories named `archive` are excluded from discovery. They contain historical copies
with colliding test-module basenames and no package boundaries. No archived file was
deleted or renamed.

## Status of the active web application

The root `README.md` identifies `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/` as the active
web application. Its tests are not historical merely because they are outside the root
suite.

The application has a separate environment:

- `deploy/Dockerfile.backend` uses Python 3.11 and installs FastAPI, SQLAlchemy,
  `psycopg2-binary`, pytest, model libraries, and other application dependencies.
- `deploy/docker-compose.yml` supplies PostgreSQL 15 and sets `DATABASE_URL` for the API.
- `requirements-install.txt` is explicitly a host-side dependency list for installation
  guards. It omits FastAPI, SQLAlchemy, `psycopg2-binary`, and other application packages,
  so it is not a complete environment for the application tests.

Running the application tests directly in the host environment is therefore not a valid
substitute for a declared application test procedure. It presently produces collection
errors, including a missing `psycopg2` driver.

One source problem is independent of environment setup. The package initializer imports
`cnfa_adapters.spatial.acoustic_pyroom`, and the registry names fields supplied by that
module, but no `acoustic_pyroom.py` file is present in the active adapter tree.

## Decisions required from the application owner

The following matters must be decided before the active application's tests can become a
reproducible CI gate:

1. **Canonical test environment.** Decide whether application tests run in the backend
   Docker image, a documented Python 3.11 virtual environment, or both.
2. **Database contract.** State whether tests use the Compose PostgreSQL service, a separate
   test database, or substituted fixtures. Give the required setup and teardown commands.
3. **Application test command.** Name the exact paths to run and the expected pass, skip,
   and failure policy from a clean clone.
4. **Missing acoustic module.** Restore `acoustic_pyroom.py`, remove its imports and registry
   claims through a reviewed contract change, or document and implement an optional import.
5. **CI ownership.** Decide who owns a separate application job, which services it starts,
   and which branch protections depend on it.
6. **Model diagnostic naming.** Decide whether
   `biophilia-index-main/scripts/bottom_up_test.py` is an executable diagnostic. Importing
   it loads a model checkpoint immediately. If it is not a pytest test, rename it in a
   separate change so its role is unambiguous.
7. **Portable production-loop example.** Replace the machine-specific interpreter path
   described in `loop_runs/real_photo_2026-08-27/README.md` with a declared environment and
   give students an exact producer command that works from a clean clone.

## Completion evidence required

The application work is complete when a clean clone can execute a documented setup and
test sequence that:

- starts or substitutes every required service;
- collects the intended application tests without import errors;
- reports a declared pass count and zero failures;
- runs in CI by the same commands;
- leaves the 251-test root suite and the 65-test loop suite green; and
- reproduces one real production-loop run and its negative control without a path tied to
  one developer's machine.
