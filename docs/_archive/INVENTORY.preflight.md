# Repository Inventory

This file is intentionally machine-readable markdown.

## Schema

| column | meaning |
| --- | --- |
| `path` | repository-relative file path |
| `project` | logical subproject |
| `category` | one of `frontend`, `backend`, `ml`, `config`, `tests`, `docs`, `scripts`, `data`, `artifact`, `archive`, `noise` |
| `description` | 1-line purpose summary |
| `quality` | one of `working`, `prototype`, `broken`, `archive`, `artifact`, `vendor`, `noise` |
| `status_note` | short justification for the quality label |

## Exclusions

The following are present in the repo but omitted from the main inventory tables:

| pattern | reason |
| --- | --- |
| `**/node_modules/**` | vendored third-party packages |
| `**/__pycache__/**` | generated Python bytecode |
| `**/.pytest_cache/**` | generated pytest cache |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/logs/**` | generated install logs |

## Inventory

| path | project | category | description | quality | status_note |
| --- | --- | --- | --- | --- | --- |
| `.DS_Store` | root | noise | macOS Finder metadata file at repo root. | noise | local OS artifact |
| `.gitignore` | root | config | repo-wide ignore rules. | working | normal source-control config |
| `API_REQUEST_FAILURE_FIX_PLAN.md` | root | docs | planning note for an API failure fix. | prototype | planning document, not implementation |
| `CLAUDE.md` | root | docs | repo working guide identifying the active app and caveats. | working | current and internally consistent |
| `IMAGE_DETAIL_VIEW_SPEC.md` | root | docs | product spec for the image detail view. | prototype | design/spec artifact |
| `Image_Tagger_3.4.73_Repo_Overview.docx` | root | docs | exported overview document for an older release. | archive | versioned historical doc |
| `Image_Tagger_3.4.73_TA_and_Student_Guide.docx` | root | docs | exported TA and student guide for an older release. | archive | older release document |
| `Image_Tagger_3.4.74_Technical_Lead_Runbook.docx` | root | docs | exported technical lead runbook document. | working | aligned with current version naming |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full.txt` | root | artifact | flattened text export of the main app materials. | artifact | generated/exported bundle |
| `biophilia-index-main-20260330T171828Z-1-001.zip` | root | artifact | zipped snapshot of the standalone biophilia package. | artifact | binary snapshot |
| `docs/Environment_Cognition_Taxonomy_Hierarchical_V2.7_ActivityAffordances_RoomMarkers copy.xlsx` | root | docs | taxonomy spreadsheet for cognition and affordances. | working | source reference data/doc |
| `docs/Image Tagger Status Report.docx` | root | docs | exported project status report. | working | current status collateral |
| `TRS_v1.1/.DS_Store` | TRS_v1.1 | noise | macOS metadata inside TRS subproject. | noise | local OS artifact |
| `TRS_v1.1/.env` | TRS_v1.1 | config | local environment configuration for TRS. | working | active local config file |
| `TRS_v1.1/.env.example` | TRS_v1.1 | config | sample environment variables for TRS. | working | expected config template |
| `TRS_v1.1/.github/workflows/ci.yml` | TRS_v1.1 | config | CI workflow for TRS tests and checks. | working | standard automation config |
| `TRS_v1.1/AGENTS.md` | TRS_v1.1 | docs | agent guidance file for working in the TRS tree. | working | current repo guidance |
| `TRS_v1.1/Dockerfile.api` | TRS_v1.1 | config | container build file for the TRS API. | working | deployment config |
| `TRS_v1.1/Dockerfile.ui` | TRS_v1.1 | config | container build file for the TRS UI. | working | deployment config |
| `TRS_v1.1/INSTALL.md` | TRS_v1.1 | docs | installation instructions for TRS. | working | matches quickstart shape |
| `TRS_v1.1/README.md` | TRS_v1.1 | docs | quickstart overview for the turnkey TRS wrapper. | working | coherent and current |
| `TRS_v1.1/VERSION.txt` | TRS_v1.1 | config | version marker for the TRS package. | working | single-version metadata |
| `TRS_v1.1/backend/app/auth.py` | TRS_v1.1 | backend | auth helpers for the TRS API. | working | standard support module |
| `TRS_v1.1/backend/app/cache.py` | TRS_v1.1 | backend | cache layer for TRS API lookups. | working | typical utility module |
| `TRS_v1.1/backend/app/dashboard.py` | TRS_v1.1 | backend | dashboard support logic for TRS. | prototype | less central and likely lightly used |
| `TRS_v1.1/backend/app/db/__init__.py` | TRS_v1.1 | backend | package marker for the TRS DB layer. | working | standard package file |
| `TRS_v1.1/backend/app/db/database.py` | TRS_v1.1 | backend | database access and session utilities for TRS. | working | core infra code |
| `TRS_v1.1/backend/app/db/schema.sql` | TRS_v1.1 | backend | SQL schema for the TRS database. | working | source-of-truth SQL asset |
| `TRS_v1.1/backend/app/logging_config.py` | TRS_v1.1 | backend | logging setup for the TRS backend. | working | standard infra module |
| `TRS_v1.1/backend/app/main.py` | TRS_v1.1 | backend | FastAPI entrypoint for the TRS service. | working | primary application entrypoint |
| `TRS_v1.1/backend/app/metrics.py` | TRS_v1.1 | backend | metrics helpers for backend instrumentation. | working | support code |
| `TRS_v1.1/backend/app/middleware.py` | TRS_v1.1 | backend | request middleware for the TRS API stack. | working | standard API support |
| `TRS_v1.1/backend/app/ratelimit.py` | TRS_v1.1 | backend | rate-limiting helpers. | working | standard protection layer |
| `TRS_v1.1/backend/app/registry_loader.py` | TRS_v1.1 | backend | loads the bundled canonical registry and contracts. | working | central runtime loader |
| `TRS_v1.1/backend/app/routes.py` | TRS_v1.1 | backend | primary read-only browse routes for TRS data. | working | core API surface |
| `TRS_v1.1/backend/app/routes_health.py` | TRS_v1.1 | backend | health endpoints for readiness/liveness checks. | working | expected service endpoint |
| `TRS_v1.1/backend/app/routes_proposals.py` | TRS_v1.1 | backend | proposal-related API routes. | prototype | proposal path looks secondary |
| `TRS_v1.1/backend/app/routes_search.py` | TRS_v1.1 | backend | search endpoints over registry data. | working | expected browse functionality |
| `TRS_v1.1/backend/app/schemas.py` | TRS_v1.1 | backend | request and response schemas for the TRS API. | working | standard API model layer |
| `TRS_v1.1/backend/app/security.py` | TRS_v1.1 | backend | security helpers and policies. | working | core support layer |
| `TRS_v1.1/backend/app/settings.py` | TRS_v1.1 | backend | environment and settings loader. | working | standard config module |
| `TRS_v1.1/backend/app/webhooks.py` | TRS_v1.1 | backend | webhook integration endpoints/helpers. | prototype | integration edge path |
| `TRS_v1.1/backend/requirements.txt` | TRS_v1.1 | config | Python dependency list for TRS backend. | working | expected environment manifest |
| `TRS_v1.1/backend/science/localized/__init__.py` | TRS_v1.1 | ml | package marker for localized science code. | working | standard package file |
| `TRS_v1.1/backend/science/localized/localized_pipeline.py` | TRS_v1.1 | ml | localized tagging pipeline implementation. | prototype | spec-heavy feature area |
| `TRS_v1.1/backend/science/localized/region_pooling.py` | TRS_v1.1 | ml | region pooling logic for localized tagging. | prototype | research-oriented component |
| `TRS_v1.1/backend/science/segmentation/__init__.py` | TRS_v1.1 | ml | package marker for segmentation code. | working | standard package file |
| `TRS_v1.1/backend/science/segmentation/segformer.py` | TRS_v1.1 | ml | SegFormer-based segmentation integration. | prototype | likely optional/experimental |
| `TRS_v1.1/backend/science/spatial/wall_separation.py` | TRS_v1.1 | ml | wall separation spatial analysis logic. | prototype | research feature |
| `TRS_v1.1/bin/keys.py` | TRS_v1.1 | scripts | helper for key or credential handling. | prototype | support utility |
| `TRS_v1.1/bin/tc` | TRS_v1.1 | scripts | top-level turnkey control command. | working | primary operator CLI |
| `TRS_v1.1/bin/trs.py` | TRS_v1.1 | scripts | Python CLI entry wrapper for TRS commands. | working | active command entrypoint |
| `TRS_v1.1/clients/python/setup.py` | TRS_v1.1 | config | packaging config for the Python TRS client. | working | normal package metadata |
| `TRS_v1.1/clients/python/trs_client/__init__.py` | TRS_v1.1 | backend | package init for the Python TRS client. | working | standard package file |
| `TRS_v1.1/clients/python/trs_client/compliance.py` | TRS_v1.1 | backend | compliance checks for client-consumed artifacts. | working | client support logic |
| `TRS_v1.1/clients/python/trs_client/examples/image_tagger.py` | TRS_v1.1 | docs | example client usage against image tagger data. | working | example code artifact |
| `TRS_v1.1/clients/python/trs_client/validator.py` | TRS_v1.1 | backend | schema/contract validation helpers for the client. | working | expected client utility |
| `TRS_v1.1/contracts/localized_image_tags.schema.json` | TRS_v1.1 | config | schema for localized image tag outputs. | working | core contract asset |
| `TRS_v1.1/core/trs-core/v0.2.8/contracts/article_eater_contract_v0.2.8.json` | TRS_v1.1 | config | vendored article_eater contract bundle. | working | packaged contract |
| `TRS_v1.1/core/trs-core/v0.2.8/contracts/bn_contract_v0.2.8.json` | TRS_v1.1 | config | vendored BN contract bundle. | working | packaged contract |
| `TRS_v1.1/core/trs-core/v0.2.8/contracts/image_tagger_contract_v0.2.8.json` | TRS_v1.1 | config | vendored image tagger contract bundle. | working | packaged contract |
| `TRS_v1.1/core/trs-core/v0.2.8/contracts/preference_testing_contract_v0.2.8.json` | TRS_v1.1 | config | vendored preference testing contract. | working | packaged contract |
| `TRS_v1.1/core/trs-core/v0.2.8/contracts/registry_sha256_v0.2.8.json` | TRS_v1.1 | config | checksum manifest for the canonical registry. | working | integrity metadata |
| `TRS_v1.1/core/trs-core/v0.2.8/registry/cnfa_tag_registry_canonical_v0.2.8.yaml` | TRS_v1.1 | config | canonical TRS registry definition. | working | core registry source |
| `TRS_v1.1/core/trs-core/v0.2.8/schemas/SEMANTICS_SCHEMA_v0.2.8.md` | TRS_v1.1 | docs | semantics schema documentation. | working | spec documentation |
| `TRS_v1.1/core/trs-core/v0.2.8/schemas/json_schema/contracts/image_tagger_contract.schema.json` | TRS_v1.1 | config | JSON schema for image tagger contracts. | working | contract validation schema |
| `TRS_v1.1/core/trs-core/v0.2.8/schemas/json_schema/manifests/consumer_manifest.schema.json` | TRS_v1.1 | config | JSON schema for consumer manifests. | working | validation schema |
| `TRS_v1.1/core/trs-core/v0.2.8/schemas/json_schema/observations/image_tagger_observation.schema.json` | TRS_v1.1 | config | JSON schema for image tagger observations. | working | validation schema |
| `TRS_v1.1/core/trs-core/v0.2.8/vendor_specs/README.md` | TRS_v1.1 | docs | notes on bundled vendor specs. | working | supporting spec doc |
| `TRS_v1.1/core/trs-core/v0.2.8/vendor_specs/swagger_v0.2.8.json` | TRS_v1.1 | config | bundled OpenAPI/Swagger spec. | working | packaged API spec |
| `TRS_v1.1/docker-compose.yml` | TRS_v1.1 | config | Docker Compose stack for TRS API and UI. | working | current runtime config |
| `TRS_v1.1/docs/.DS_Store` | TRS_v1.1 | noise | macOS metadata inside TRS docs folder. | noise | local OS artifact |
| `TRS_v1.1/docs/neuroarch_localized_spec/01_Core_Specification.md` | TRS_v1.1 | docs | core specification for localized tagging. | prototype | specification for still-maturing feature |
| `TRS_v1.1/docs/neuroarch_localized_spec/02_Tag_Scope_Classification.md` | TRS_v1.1 | docs | tag scope classification spec. | prototype | spec-only artifact |
| `TRS_v1.1/docs/neuroarch_localized_spec/03_Model_Selection_Matrix.md` | TRS_v1.1 | docs | model selection matrix for localization work. | prototype | planning/spec artifact |
| `TRS_v1.1/docs/neuroarch_localized_spec/04_Wall_Identification.md` | TRS_v1.1 | docs | wall identification spec for spatial localization. | prototype | research-spec document |
| `TRS_v1.1/docs/neuroarch_localized_spec/05_Prototype_Fractal.md` | TRS_v1.1 | docs | prototype fractal analysis design note. | prototype | explicitly labeled prototype |
| `TRS_v1.1/docs/neuroarch_localized_spec/06_Implementation_Guide.md` | TRS_v1.1 | docs | implementation guide for localized spec. | prototype | feature area still speculative |
| `TRS_v1.1/docs/neuroarch_localized_spec/CNFA_Tag_Localization_Classification_v0.2.8.md` | TRS_v1.1 | docs | detailed localized classification spec. | prototype | spec collateral |
| `TRS_v1.1/docs/neuroarch_localized_spec/README.md` | TRS_v1.1 | docs | overview for the localized spec folder. | prototype | spec overview |
| `TRS_v1.1/docs/neuroarch_localized_spec/VERSION` | TRS_v1.1 | config | version marker for the localized spec bundle. | working | metadata marker |
| `TRS_v1.1/docs/neuroarch_localized_spec/cnfa_tag_localization_v0.2.8.json` | TRS_v1.1 | config | JSON form of the localized tagging spec. | prototype | spec data, not runtime path |
| `TRS_v1.1/docs/release_workflow.md` | TRS_v1.1 | docs | release workflow for TRS packaging. | working | operator documentation |
| `TRS_v1.1/frontend_streamlit/app.py` | TRS_v1.1 | frontend | Streamlit UI for browsing TRS data and health. | working | documented runtime component |
| `TRS_v1.1/frontend_streamlit/requirements.txt` | TRS_v1.1 | config | dependency list for the Streamlit UI. | working | standard environment manifest |
| `TRS_v1.1/install.sh` | TRS_v1.1 | scripts | top-level installer for the TRS stack. | working | standard bootstrap script |
| `TRS_v1.1/installer/install.sh` | TRS_v1.1 | scripts | nested installer copy used by packaging flow. | working | packaged installer variant |
| `TRS_v1.1/ops/ports.md` | TRS_v1.1 | docs | port mapping reference for TRS services. | working | operator reference |
| `TRS_v1.1/rebuild_with_localized.sh` | TRS_v1.1 | scripts | rebuild helper focused on localized features. | prototype | specialized feature workflow |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.0.3.zip` | TRS_v1.1 | artifact | packaged release archive for an older contractor bundle. | artifact | binary release artifact |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.0.3_manifest.txt` | TRS_v1.1 | artifact | manifest for the v0.0.3 packaged release. | artifact | generated release metadata |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.0.3_sha256.txt` | TRS_v1.1 | artifact | checksum for the v0.0.3 packaged release. | artifact | generated integrity file |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.2.8.zip` | TRS_v1.1 | artifact | packaged release archive for current contractor bundle. | artifact | binary release artifact |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.2.8_manifest.txt` | TRS_v1.1 | artifact | manifest for the v0.2.8 packaged release. | artifact | generated release metadata |
| `TRS_v1.1/release_artifacts/Tagging_Contractor_v0.2.8_sha256.txt` | TRS_v1.1 | artifact | checksum for the v0.2.8 packaged release. | artifact | generated integrity file |
| `TRS_v1.1/scripts/audit.py` | TRS_v1.1 | scripts | audit utility for TRS data or release state. | working | support automation |
| `TRS_v1.1/scripts/backup.py` | TRS_v1.1 | scripts | backup helper for TRS state. | working | support automation |
| `TRS_v1.1/scripts/batch.py` | TRS_v1.1 | scripts | batch processing helper for TRS tasks. | working | operational script |
| `TRS_v1.1/scripts/bulk_update.py` | TRS_v1.1 | scripts | bulk update helper over TRS records. | working | operational script |
| `TRS_v1.1/scripts/changelog.py` | TRS_v1.1 | scripts | changelog generation or management utility. | working | release support script |
| `TRS_v1.1/scripts/db_migrate.py` | TRS_v1.1 | scripts | database migration runner for TRS. | working | operational script |
| `TRS_v1.1/scripts/diff_registry.py` | TRS_v1.1 | scripts | diffs versions of the canonical registry. | working | core support tool |
| `TRS_v1.1/scripts/doctor.py` | TRS_v1.1 | scripts | health and environment doctor command. | working | documented operator tool |
| `TRS_v1.1/scripts/find_duplicates.py` | TRS_v1.1 | scripts | duplicate detection utility. | working | support automation |
| `TRS_v1.1/scripts/generate_contracts.py` | TRS_v1.1 | scripts | generates packaged contract artifacts. | working | core build tool |
| `TRS_v1.1/scripts/generate_docs.py` | TRS_v1.1 | scripts | documentation generation helper. | working | build support script |
| `TRS_v1.1/scripts/lint_registry.py` | TRS_v1.1 | scripts | lint checks for the canonical registry. | working | quality guard |
| `TRS_v1.1/scripts/maintenance.py` | TRS_v1.1 | scripts | maintenance helper for routine ops tasks. | working | support automation |
| `TRS_v1.1/scripts/merge_proposals.py` | TRS_v1.1 | scripts | merges proposal changes into registry state. | prototype | proposal workflow edge path |
| `TRS_v1.1/scripts/migrate.py` | TRS_v1.1 | scripts | generic migration wrapper. | working | support automation |
| `TRS_v1.1/scripts/propose_cli.py` | TRS_v1.1 | scripts | CLI for proposal creation/update flows. | prototype | proposal workflow edge path |
| `TRS_v1.1/scripts/quality_score.py` | TRS_v1.1 | scripts | computes quality scoring/report metrics. | working | support analysis tool |
| `TRS_v1.1/scripts/release.py` | TRS_v1.1 | scripts | release packaging/orchestration script. | working | release automation |
| `TRS_v1.1/scripts/validate_registry.py` | TRS_v1.1 | scripts | validates registry integrity against schemas. | working | core validation tool |
| `TRS_v1.1/scripts/validation_report.py` | TRS_v1.1 | scripts | produces a registry validation report. | working | reporting helper |
| `TRS_v1.1/tests/conftest.py` | TRS_v1.1 | tests | pytest fixtures and shared test setup. | working | normal test support |
| `TRS_v1.1/tests/test_database.py` | TRS_v1.1 | tests | tests database behavior and queries. | working | active test coverage |
| `TRS_v1.1/tests/test_diff_registry.py` | TRS_v1.1 | tests | tests registry diff tooling. | working | active test coverage |
| `TRS_v1.1/tests/test_generate_contracts.py` | TRS_v1.1 | tests | tests contract generation scripts. | working | active test coverage |
| `TRS_v1.1/tests/test_integration.py` | TRS_v1.1 | tests | integration test coverage for TRS flows. | working | active integration suite |
| `TRS_v1.1/tests/test_security.py` | TRS_v1.1 | tests | tests auth and security behavior. | working | active security coverage |
| `TRS_v1.1/tests/test_validate_registry.py` | TRS_v1.1 | tests | tests registry validation behavior. | working | active test coverage |
| `biophilia-index-main/.gitignore` | biophilia-index-main | config | ignore rules for the standalone biophilia package. | working | standard source-control config |
| `biophilia-index-main/CITATIONS.md` | biophilia-index-main | docs | citation requirements for reused MMSFormer work. | working | normal research doc |
| `biophilia-index-main/LICENSE` | biophilia-index-main | docs | software license for the standalone package. | working | normal package metadata |
| `biophilia-index-main/README.md` | biophilia-index-main | docs | usage and architecture guide for the biophilic index package. | working | coherent package readme |
| `biophilia-index-main/configs/fmb_rgbt.yaml` | biophilia-index-main | config | MMSFormer config for the FMB dataset/setup. | working | model config asset |
| `biophilia-index-main/configs/mcubes_rgbadn.yaml` | biophilia-index-main | config | MMSFormer config for MCubeS RGBADN setup. | working | model config asset |
| `biophilia-index-main/configs/pst_rgbt.yaml` | biophilia-index-main | config | MMSFormer config for PST setup. | working | model config asset |
| `biophilia-index-main/environment.yaml` | biophilia-index-main | config | conda environment definition. | working | environment manifest |
| `biophilia-index-main/requirements.txt` | biophilia-index-main | config | pip requirements for the package. | working | environment manifest |
| `biophilia-index-main/scripts/biophilia.py` | biophilia-index-main | ml | CLI and library entrypoint for biophilic index scoring. | working | main package behavior |
| `biophilia-index-main/scripts/biophilia_config.yaml` | biophilia-index-main | config | factor weighting and runtime config for index scoring. | working | core runtime config |
| `biophilia-index-main/scripts/biophilia_docs.md` | biophilia-index-main | docs | detailed docs for biophilic index calculation. | working | supporting docs |
| `biophilia-index-main/scripts/bottom_up_test.py` | biophilia-index-main | tests | experimental bottom-up test script. | prototype | script-style experiment |
| `biophilia-index-main/scripts/natural_texture_presence.py` | biophilia-index-main | ml | natural texture scoring factor using segmentation outputs. | working | core model logic |
| `biophilia-index-main/scripts/palette.py` | biophilia-index-main | ml | palette utilities for segmentation overlays. | working | support ML utility |
| `biophilia-index-main/scripts/plant_presence.py` | biophilia-index-main | ml | plant detection scoring factor using Mask R-CNN. | working | core model logic |
| `biophilia-index-main/scripts/run_mmsformer.py` | biophilia-index-main | ml | MMSFormer inference wrapper. | working | core model integration |
| `biophilia-index-main/scripts/visual_helpers.py` | biophilia-index-main | ml | helper functions for visualizing model outputs. | working | support ML utility |
| `biophilia-index-main/semseg/__init__.py` | biophilia-index-main | ml | package marker for semantic segmentation code. | working | standard package file |
| `biophilia-index-main/semseg/augmentations.py` | biophilia-index-main | ml | image augmentation logic for training/inference. | working | normal ML utility |
| `biophilia-index-main/semseg/augmentations_mm.py` | biophilia-index-main | ml | multimodal augmentation helpers. | working | normal ML utility |
| `biophilia-index-main/semseg/datasets/__init__.py` | biophilia-index-main | ml | dataset package marker. | working | standard package file |
| `biophilia-index-main/semseg/datasets/fmb.py` | biophilia-index-main | ml | dataset adapter for FMB. | working | model training/inference support |
| `biophilia-index-main/semseg/datasets/mcubes.py` | biophilia-index-main | ml | dataset adapter for MCubeS. | working | model training/inference support |
| `biophilia-index-main/semseg/datasets/pst.py` | biophilia-index-main | ml | dataset adapter for PST. | working | model training/inference support |
| `biophilia-index-main/semseg/datasets/unzip.py` | biophilia-index-main | scripts | helper to unpack dataset archives. | working | utility script |
| `biophilia-index-main/semseg/losses.py` | biophilia-index-main | ml | training loss functions. | working | core ML component |
| `biophilia-index-main/semseg/metrics.py` | biophilia-index-main | ml | segmentation evaluation metrics. | working | core ML component |
| `biophilia-index-main/semseg/models/__init__.py` | biophilia-index-main | ml | model package marker. | working | standard package file |
| `biophilia-index-main/semseg/models/backbones/__init__.py` | biophilia-index-main | ml | backbone package marker. | working | standard package file |
| `biophilia-index-main/semseg/models/backbones/mmsformer.py` | biophilia-index-main | ml | MMSFormer backbone implementation. | working | core ML model code |
| `biophilia-index-main/semseg/models/base.py` | biophilia-index-main | ml | base model abstractions. | working | core framework utility |
| `biophilia-index-main/semseg/models/heads/__init__.py` | biophilia-index-main | ml | model heads package marker. | working | standard package file |
| `biophilia-index-main/semseg/models/heads/segformer.py` | biophilia-index-main | ml | SegFormer head implementation. | working | core ML model code |
| `biophilia-index-main/semseg/models/layers/__init__.py` | biophilia-index-main | ml | layers package marker. | working | standard package file |
| `biophilia-index-main/semseg/models/layers/common.py` | biophilia-index-main | ml | common model layers. | working | core ML utility |
| `biophilia-index-main/semseg/models/layers/initialize.py` | biophilia-index-main | ml | layer initialization helpers. | working | core ML utility |
| `biophilia-index-main/semseg/models/mmsformer.py` | biophilia-index-main | ml | top-level MMSFormer model definition. | working | core ML model code |
| `biophilia-index-main/semseg/optimizers.py` | biophilia-index-main | ml | optimizer factory helpers. | working | training utility |
| `biophilia-index-main/semseg/schedulers.py` | biophilia-index-main | ml | LR scheduler helpers. | working | training utility |
| `biophilia-index-main/semseg/utils/__init__.py` | biophilia-index-main | ml | utils package marker. | working | standard package file |
| `biophilia-index-main/semseg/utils/utils.py` | biophilia-index-main | ml | general segmentation utility functions. | working | support ML utility |
| `biophilia-index-main/semseg/utils/visualize.py` | biophilia-index-main | ml | visualization helpers for segmentation outputs. | working | support ML utility |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/.DS_Store` | Image_Tagger | noise | macOS metadata inside the main app tree. | noise | local OS artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/.claude/settings.local.json` | Image_Tagger | noise | local Claude/Codex settings for this app tree. | noise | local tool state |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/.github/workflows/auto_installer_smoke.yml` | Image_Tagger | config | CI workflow for the auto-installer smoke path. | working | active automation |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/.github/workflows/ci.yml` | Image_Tagger | config | older CI workflow for the main app. | working | still part of automation |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/.github/workflows/ci_v3.yml` | Image_Tagger | config | current v3 CI workflow with guardian and smoke checks. | working | current automation path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CANONICAL_ANCHOR.json` | Image_Tagger | config | canonical anchor/lock metadata for guarded repo state. | working | governance metadata |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.23_tag_inspector.md` | Image_Tagger | docs | changelog entry for tag inspector work. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.24_tag_inspector_help.md` | Image_Tagger | docs | changelog entry for inspector help text. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.25_role_help_strips.md` | Image_Tagger | docs | changelog entry for role help strips. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.27_priority_help.md` | Image_Tagger | docs | changelog entry for priority help. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.28_pipeline_health_view.md` | Image_Tagger | docs | changelog entry for pipeline health view. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.30_pipeline_health_tests.md` | Image_Tagger | docs | changelog entry for pipeline health tests. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.31_bn_canon_sanity.md` | Image_Tagger | docs | changelog entry for BN canon sanity work. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.32_restorativeness_H1.md` | Image_Tagger | docs | changelog entry for restorativeness work. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.36_upload_guard_and_bn_guard.md` | Image_Tagger | docs | changelog entry for upload and BN guards. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.60_semantic_tags_vlm.md` | Image_Tagger | docs | changelog entry for semantic VLM tags. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.62_science_tag_coverage_enforced.md` | Image_Tagger | docs | changelog entry for science tag coverage enforcement. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.63_bn_db_tightening_and_health.md` | Image_Tagger | docs | changelog entry for BN DB tightening. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/CHANGELOG_v3.4.64_bn_db_migration_helper.md` | Image_Tagger | docs | changelog entry for migration helper work. | archive | release-history note |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/Makefile` | Image_Tagger | config | helper targets for VLM health and dev workflows. | working | active project automation |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/PROJECT_CONSTITUTION.md` | Image_Tagger | docs | governance rules including no-delete and honesty requirements. | working | central governance doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/README_v3.md` | Image_Tagger | docs | primary architecture and usage guide for the current app. | working | coherent and current |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/STUDENT_START_HERE.md` | Image_Tagger | docs | student onboarding entrypoint. | working | current onboarding doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/VERSION` | Image_Tagger | config | single source of truth for app version. | working | core version marker |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/ai/copilot_policy.json` | Image_Tagger | config | policy controlling allowed AI copilot actions. | working | active tooling policy |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/ai/installer_copilot.py` | Image_Tagger | scripts | helper for AI-assisted installer workflow. | prototype | tool-integration helper |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/ai/providers.py` | Image_Tagger | backend | provider abstraction for Gemini/OpenAI/Anthropic integrations. | prototype | VLM path is optional/stubbed |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/ai/providers.sample.env` | Image_Tagger | config | sample provider environment variables. | working | expected config template |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/ai/triage_schema.json` | Image_Tagger | config | JSON schema for AI triage payloads. | working | contract/config asset |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/VERSION` | Image_Tagger | archive | version marker for an archived pre-sprint snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/backend/science/spatial/depth_plugin.py` | Image_Tagger | archive | archived depth plugin implementation from an early snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/backend/science/vision/materials.py` | Image_Tagger | archive | archived materials analysis implementation. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/install.sh` | Image_Tagger | archive | archived installer script. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/scripts/science_harness.py` | Image_Tagger | archive | archived science harness script. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/sprint_s0s1s2_pre/tests/test_governance_integrity.py` | Image_Tagger | archive | archived governance integrity test. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step10_admin_training_export_ui/CHANGELOG_step10_admin_training_export_ui.txt` | Image_Tagger | archive | archived changelog for training export UI step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step11_api_smoketests/CHANGELOG_step11_api_smoketests.txt` | Image_Tagger | archive | archived changelog for API smoke tests step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step12_ux_help_layer/CHANGELOG_step12_ux_help_layer.txt` | Image_Tagger | archive | archived changelog for UX help layer step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step13_router_wiring/CHANGELOG_step13_router_wiring.txt` | Image_Tagger | archive | archived changelog for router wiring step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step14_guardian_install_tests/CHANGELOG_step14_guardian_install_tests.txt` | Image_Tagger | archive | archived changelog for guardian/install tests step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step6_monitor/CHANGELOG_step6_monitor_supervision.txt` | Image_Tagger | archive | archived changelog for monitor supervision step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step7_tag_inspector/CHANGELOG_step7_tag_inspector.txt` | Image_Tagger | archive | archived changelog for tag inspector step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step8_admin_cockpit/CHANGELOG_step8_admin_cockpit.txt` | Image_Tagger | archive | archived changelog for admin cockpit step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/step9_training_export/CHANGELOG_step9_training_export.txt` | Image_Tagger | archive | archived changelog for training export step. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.18_pre_s0s1_2025-11-24_s0s1/backend/science/spatial/depth_plugin.py` | Image_Tagger | archive | archived depth plugin variant from v3.4.18 pre snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.18_pre_s0s1_2025-11-24_s0s1/backend/science/vision/materials.py` | Image_Tagger | archive | archived materials variant from v3.4.18 pre snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.18_pre_s0s1_2025-11-24_s0s1/install.sh` | Image_Tagger | archive | archived installer from v3.4.18 pre snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.18_pre_s0s1_2025-11-24_s0s1/scripts/science_harness.py` | Image_Tagger | archive | archived science harness from v3.4.18 pre snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.18_pre_s0s1_2025-11-24_s0s1/tests/test_governance_integrity.py` | Image_Tagger | archive | archived governance test from v3.4.18 pre snapshot. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.20_pre_merge_3.4.21_2025-11-23/VERSION` | Image_Tagger | archive | version marker for an archived pre-merge snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.20_pre_merge_3.4.21_2025-11-23/backend/api/v1_debug.py` | Image_Tagger | archive | archived debug API router. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.20_pre_merge_3.4.21_2025-11-23/install.sh` | Image_Tagger | archive | archived install script from pre-merge snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.20_pre_merge_3.4.21_2025-11-23/tests/test_governance_integrity.py` | Image_Tagger | archive | archived governance test from pre-merge snapshot. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.21_pre_merge_3.4.22_canon_guard/VERSION` | Image_Tagger | archive | version marker for canon-guard archive snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3.4.21_pre_merge_3.4.22_canon_guard/scripts/canon_guard.py` | Image_Tagger | archive | archived canon guard script. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/backend/api/v1_discovery.py` | Image_Tagger | archive | archived discovery API from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/backend/schemas/annotation.py` | Image_Tagger | archive | archived annotation schema from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/backend/science/vision/objects.py` | Image_Tagger | archive | archived object-vision code from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/backend/scripts/seed_attributes.py` | Image_Tagger | archive | archived seed script from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/backend/scripts/seed_tool_configs.py` | Image_Tagger | archive | archived tool-config seed script from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/install.sh` | Image_Tagger | archive | archived installer from phase 0. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_14_phase0/tests/test_v3_api.py` | Image_Tagger | archive | archived API test from phase 0. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/backend/api/v1_discovery.py` | Image_Tagger | archive | archived discovery API from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/backend/schemas/annotation.py` | Image_Tagger | archive | archived annotation schema from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/backend/science/vision/objects.py` | Image_Tagger | archive | archived object vision code from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/backend/scripts/seed_attributes.py` | Image_Tagger | archive | archived seed attributes script from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/backend/scripts/seed_tool_configs.py` | Image_Tagger | archive | archived seed tool configs script from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/install.sh` | Image_Tagger | archive | archived installer from phase0 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase0_rebuild/tests/test_v3_api.py` | Image_Tagger | archive | archived API tests from phase0 rebuild. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase1/README_v3.md` | Image_Tagger | archive | archived README for phase1 snapshot. | archive | historical doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_15_phase1/v3_governance.yml` | Image_Tagger | archive | archived governance file for phase1. | archive | historical config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_16_phase1_rebuild/README_v3.md` | Image_Tagger | archive | archived README for phase1 rebuild. | archive | historical doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_16_phase1_rebuild/v3_governance.yml` | Image_Tagger | archive | archived governance file for phase1 rebuild. | archive | historical config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_16_phase2/deploy/Dockerfile.backend` | Image_Tagger | archive | archived backend Dockerfile from phase2. | archive | historical config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_17_phase2_rebuild/deploy/Dockerfile.backend` | Image_Tagger | archive | archived backend Dockerfile from phase2 rebuild. | archive | historical config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_18_phase3_rebuild/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM science module from phase3 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_18_phase3_rebuild/backend/science/pipeline.py` | Image_Tagger | archive | archived science pipeline from phase3 rebuild. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/context/cognitive.py` | Image_Tagger | archive | archived cognitive context module from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/core.py` | Image_Tagger | archive | archived science core from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/math/color.py` | Image_Tagger | archive | archived color metrics module from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/math/complexity.py` | Image_Tagger | archive | archived complexity metrics module from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/math/fractals.py` | Image_Tagger | archive | archived fractal metrics module from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM metrics module from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/backend/science/pipeline.py` | Image_Tagger | archive | archived science pipeline from science upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_21_science_upgrade/scripts/run_science_on_sample.py` | Image_Tagger | archive | archived sample science runner. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_22_discovery_upgrade/backend/api/v1_discovery.py` | Image_Tagger | archive | archived discovery API from discovery upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_23_smokescience_upgrade/install.sh` | Image_Tagger | archive | archived installer from smokescience upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_23_smokescience_upgrade/scripts/smoke_science.py` | Image_Tagger | archive | archived science smoke script. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_24_monitor_tightening/backend/api/v1_supervision.py` | Image_Tagger | archive | archived supervision API from monitor tightening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_24_monitor_tightening/backend/models/annotation.py` | Image_Tagger | archive | archived annotation model from monitor tightening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_24_monitor_tightening/backend/schemas/supervision.py` | Image_Tagger | archive | archived supervision schema from monitor tightening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_24_monitor_tightening/tests/test_v3_api.py` | Image_Tagger | archive | archived v3 API tests from monitor tightening. | archive | historical test |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_25_guardian_upgrade/scripts/guardian.py` | Image_Tagger | archive | archived guardian script from guardian upgrade. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_25_guardian_upgrade/v3_governance.yml` | Image_Tagger | archive | archived governance file from guardian upgrade. | archive | historical config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_26_phase5_docs_ux_ci/README_v3.md` | Image_Tagger | archive | archived README from phase5 docs/UX/CI snapshot. | archive | historical doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_26_phase5_docs_ux_ci/frontend/apps/admin/index.html` | Image_Tagger | archive | archived admin static entry HTML. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_26_phase5_docs_ux_ci/frontend/apps/explorer/index.html` | Image_Tagger | archive | archived explorer static entry HTML. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_26_phase5_docs_ux_ci/frontend/apps/monitor/index.html` | Image_Tagger | archive | archived monitor static entry HTML. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_26_phase5_docs_ux_ci/frontend/apps/workbench/index.html` | Image_Tagger | archive | archived workbench static entry HTML. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_27_science_deepening/backend/science/math/color.py` | Image_Tagger | archive | archived color metrics module from science deepening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_27_science_deepening/backend/science/math/complexity.py` | Image_Tagger | archive | archived complexity module from science deepening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_27_science_deepening/backend/science/math/fractals.py` | Image_Tagger | archive | archived fractal module from science deepening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_27_science_deepening/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM module from science deepening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_28_science_composites/README_v3.md` | Image_Tagger | archive | archived README from science composites snapshot. | archive | historical doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_28_science_composites/backend/science/pipeline.py` | Image_Tagger | archive | archived science pipeline from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_29_workbench_responsive/frontend/apps/workbench/src/App.jsx` | Image_Tagger | archive | archived responsive workbench app. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_30_auth_hardening/backend/services/auth.py` | Image_Tagger | archive | archived auth service from auth hardening. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_31_science_composites/backend/science/math/color.py` | Image_Tagger | archive | archived color metrics module from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_31_science_composites/backend/science/math/complexity.py` | Image_Tagger | archive | archived complexity module from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_31_science_composites/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM module from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_31_science_composites/backend/science/pipeline.py` | Image_Tagger | archive | archived science pipeline from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_31_science_composites_fractals/backend/science/math/fractals.py` | Image_Tagger | archive | archived fractals module from composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_auth_hardening/backend/services/auth.py` | Image_Tagger | archive | archived auth service from second auth hardening pass. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_science_composites/backend/science/math/color.py` | Image_Tagger | archive | archived color module from later composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_science_composites/backend/science/math/complexity.py` | Image_Tagger | archive | archived complexity module from later composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_science_composites/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM module from later composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_science_composites/backend/science/pipeline.py` | Image_Tagger | archive | archived pipeline from later composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_science_composites_fractals/backend/science/math/fractals.py` | Image_Tagger | archive | archived fractal module from later composites snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_32_workbench_responsive/frontend/apps/workbench/src/App.jsx` | Image_Tagger | archive | archived later responsive workbench app. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/context/cognitive.py` | Image_Tagger | archive | archived cognitive module from science refactor. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/core.py` | Image_Tagger | archive | archived science core from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/math/color.py` | Image_Tagger | archive | archived color module from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/math/complexity.py` | Image_Tagger | archive | archived complexity module from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/math/fractals.py` | Image_Tagger | archive | archived fractal module from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/math/glcm.py` | Image_Tagger | archive | archived GLCM module from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/pipeline.py` | Image_Tagger | archive | archived pipeline from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_refactor/backend/science/spatial/depth.py` | Image_Tagger | archive | archived depth module from refactor snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_33_science_smoke/scripts/smoke_science.py` | Image_Tagger | archive | archived science smoke script. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_34_router_gui/backend/main.py` | Image_Tagger | archive | archived backend entrypoint from router GUI snapshot. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_2_34_router_gui/frontend/apps/admin/src/App.jsx` | Image_Tagger | archive | archived admin app from router GUI snapshot. | archive | historical frontend |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_3_6_admin_upload_patch/CHANGELOG_v3_3_6_admin_upload_patch.txt` | Image_Tagger | archive | archived changelog for admin upload patch. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_3_7_ruthless_followup/CHANGELOG_v3_3_7_ruthless_followup.txt` | Image_Tagger | archive | archived changelog for follow-up review work. | archive | historical changelog |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/VERSION` | Image_Tagger | archive | version marker for archived sprint1 snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/api/v1_admin.py` | Image_Tagger | archive | archived admin API router from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/api/v1_annotation.py` | Image_Tagger | archive | archived annotation API router from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/api/v1_debug.py` | Image_Tagger | archive | archived debug API router from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/api/v1_discovery.py` | Image_Tagger | archive | archived discovery API router from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/main.py` | Image_Tagger | archive | archived backend entrypoint from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_13_sprint1_20251123/backend/science/pipeline.py` | Image_Tagger | archive | archived science pipeline from sprint1. | archive | historical code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_14_semantic_depth_20251123/VERSION` | Image_Tagger | archive | version marker for semantic-depth archive snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/archive/v3_4_15_feature_nav_20251123/VERSION` | Image_Tagger | archive | version marker for feature-nav archive snapshot. | archive | historical snapshot |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/auto_install.sh` | Image_Tagger | scripts | unattended installer wrapper for the main stack. | working | active bootstrap path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/__init__.py` | Image_Tagger | backend | package marker for backend code. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/__init__.py` | Image_Tagger | backend | package marker for API routers. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_admin.py` | Image_Tagger | backend | admin API routes for config, budgets, and control actions. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_annotation.py` | Image_Tagger | backend | workbench annotation API routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_bn_export.py` | Image_Tagger | backend | BN export API routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_debug.py` | Image_Tagger | backend | debug endpoints for science overlays and health views. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_discovery.py` | Image_Tagger | backend | explorer search/filter/export routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_features.py` | Image_Tagger | backend | feature catalog and metadata routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_supervision.py` | Image_Tagger | backend | monitor and supervision routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/api/v1_vlm_health.py` | Image_Tagger | backend | VLM health and variance audit routes. | working | active current router |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/data/canonical_tree_v1.json` | Image_Tagger | data | canonical hierarchy data used by the app. | working | live reference data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/data/goldilocks_attributes.csv` | Image_Tagger | data | attribute seed data for balanced/default tagging. | working | live seed data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/database/__init__.py` | Image_Tagger | backend | package marker for database code. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/database/core.py` | Image_Tagger | backend | engine, session, and base setup for SQLAlchemy. | working | core infra code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/database/google_image_data.json` | Image_Tagger | artifact | imported image metadata dataset. | artifact | data import payload |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/database/google_images_import.json` | Image_Tagger | artifact | import manifest for image ingestion. | artifact | data import payload |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/database/mixins.py` | Image_Tagger | backend | common SQLAlchemy model mixins. | working | support infra code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/main.py` | Image_Tagger | backend | FastAPI application entrypoint. | working | primary app entrypoint |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/__init__.py` | Image_Tagger | backend | package marker for ORM models. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/annotation.py` | Image_Tagger | backend | ORM models for annotations and validations. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/assets.py` | Image_Tagger | backend | ORM models for image/assets storage. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/attribute.py` | Image_Tagger | backend | ORM models for attribute metadata. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/config.py` | Image_Tagger | backend | ORM models for tool/runtime configuration. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/jobs.py` | Image_Tagger | backend | ORM models for upload and background jobs. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/science_runs.py` | Image_Tagger | backend | ORM models for canonical science runs and artifacts. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/usage.py` | Image_Tagger | backend | ORM models for usage and cost accounting. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/models/users.py` | Image_Tagger | backend | ORM models for users and roles. | working | active model layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/__init__.py` | Image_Tagger | backend | package marker for API schemas. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/admin.py` | Image_Tagger | backend | Pydantic schemas for admin routes. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/annotation.py` | Image_Tagger | backend | Pydantic schemas for annotation flows. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/bn_export.py` | Image_Tagger | backend | Pydantic schemas for BN export flows. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/common.py` | Image_Tagger | backend | shared API schema types. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/discovery.py` | Image_Tagger | backend | Pydantic schemas for explorer/discovery flows. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/supervision.py` | Image_Tagger | backend | Pydantic schemas for supervision flows. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/schemas/training.py` | Image_Tagger | backend | Pydantic schemas for training export flows. | working | active schema layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/__init__.py` | Image_Tagger | ml | package marker for science code. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/biophilia.py` | Image_Tagger | ml | biophilia scoring integration inside the main pipeline. | prototype | secondary integration path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/bn_naming_guard.py` | Image_Tagger | ml | naming guard to keep BN outputs consistent. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/context/affordance.py` | Image_Tagger | ml | affordance inference logic and model application. | broken | README notes LightGBM env compatibility issue |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/context/cognitive.py` | Image_Tagger | ml | cognitive/context scoring logic. | prototype | VLM/context path is optional |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/context/social.py` | Image_Tagger | ml | social/context inference heuristics. | prototype | research-oriented feature path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/contracts.py` | Image_Tagger | ml | contract helpers for science outputs/artifacts. | working | active pipeline support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/core.py` | Image_Tagger | ml | core science feature composition logic. | working | active pipeline core |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L059/best_params.json` | Image_Tagger | artifact | saved best-parameter metadata for affordance model L059. | artifact | trained model artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L059/lgbm_indicators_model.pkl` | Image_Tagger | artifact | pickled LightGBM indicators model for L059. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L059/lgbm_model.pkl` | Image_Tagger | artifact | pickled LightGBM model for L059. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L059/test_metrics.json` | Image_Tagger | artifact | test metrics for affordance model L059. | artifact | trained model report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L079/best_params.json` | Image_Tagger | artifact | saved best-parameter metadata for affordance model L079. | artifact | trained model artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L079/lgbm_indicators_model.pkl` | Image_Tagger | artifact | pickled LightGBM indicators model for L079. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L079/lgbm_model.pkl` | Image_Tagger | artifact | pickled LightGBM model for L079. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L079/test_metrics.json` | Image_Tagger | artifact | test metrics for affordance model L079. | artifact | trained model report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L091/best_params.json` | Image_Tagger | artifact | saved best-parameter metadata for affordance model L091. | artifact | trained model artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L091/lgbm_indicators_model.pkl` | Image_Tagger | artifact | pickled LightGBM indicators model for L091. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L091/lgbm_model.pkl` | Image_Tagger | artifact | pickled LightGBM model for L091. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L091/test_metrics.json` | Image_Tagger | artifact | test metrics for affordance model L091. | artifact | trained model report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L130/best_params.json` | Image_Tagger | artifact | saved best-parameter metadata for affordance model L130. | artifact | trained model artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L130/lgbm_indicators_model.pkl` | Image_Tagger | artifact | pickled LightGBM indicators model for L130. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L130/lgbm_model.pkl` | Image_Tagger | artifact | pickled LightGBM model for L130. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L130/test_metrics.json` | Image_Tagger | artifact | test metrics for affordance model L130. | artifact | trained model report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L141/best_params.json` | Image_Tagger | artifact | saved best-parameter metadata for affordance model L141. | artifact | trained model artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L141/lgbm_indicators_model.pkl` | Image_Tagger | artifact | pickled LightGBM indicators model for L141. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L141/lgbm_model.pkl` | Image_Tagger | artifact | pickled LightGBM model for L141. | artifact | trained model binary |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/L141/test_metrics.json` | Image_Tagger | artifact | test metrics for affordance model L141. | artifact | trained model report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/affordance_definitions.json` | Image_Tagger | data | affordance label definitions for model outputs. | working | runtime reference data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/feature_columns.json` | Image_Tagger | data | feature-column manifest for affordance models. | working | runtime reference data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/indicator_vocabulary.json` | Image_Tagger | data | indicator vocabulary for affordance predictions. | working | runtime reference data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/data/affordance_models/training_summary.json` | Image_Tagger | data | training summary for the affordance model bundle. | working | model metadata |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/feature_stubs.py` | Image_Tagger | ml | stub or placeholder feature registry entries. | prototype | name indicates partial implementation |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/features_canonical.jsonl` | Image_Tagger | data | canonical feature catalog used by the science layer. | working | active reference data |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/features_registry.py` | Image_Tagger | ml | registry logic for canonical feature metadata. | working | active support code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/index_catalog.py` | Image_Tagger | ml | catalog definitions for derived science indexes. | working | active support code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/color.py` | Image_Tagger | ml | deterministic color statistics and features. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/complexity.py` | Image_Tagger | ml | deterministic visual complexity features. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/fluency.py` | Image_Tagger | ml | perceptual fluency calculations. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/fractals.py` | Image_Tagger | ml | fractal-related image statistics. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/glcm.py` | Image_Tagger | ml | texture metrics using GLCM features. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/naturalness.py` | Image_Tagger | ml | naturalness scoring features. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/regional_frequency.py` | Image_Tagger | ml | regional frequency image metrics. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/spatial_frequency.py` | Image_Tagger | ml | spatial frequency image metrics. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/math/symmetry.py` | Image_Tagger | ml | symmetry image metrics. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/perception.py` | Image_Tagger | ml | assembly of perception-oriented science outputs. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/pipeline.py` | Image_Tagger | ml | canonical science pipeline orchestrator. | working | central production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/run_context.py` | Image_Tagger | ml | per-run context and bookkeeping for science executions. | working | active production support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/semantics/arch_parts_vlm.py` | Image_Tagger | ml | VLM-based architectural parts tagging. | prototype | optional expensive VLM path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/semantics/arch_patterns_vlm.py` | Image_Tagger | ml | VLM-based architectural pattern tagging. | prototype | optional expensive VLM path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/semantics/ontology.py` | Image_Tagger | ml | ontology definitions for semantic tagging. | working | active support data/code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/semantics/semantic_tags_vlm.py` | Image_Tagger | ml | VLM semantic tag generation orchestration. | prototype | README says disabled by default |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/spatial/depth.py` | Image_Tagger | ml | depth-related spatial feature calculations. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/spatial/depth_plugin.py` | Image_Tagger | ml | optional depth plugin integration. | prototype | optional plugin path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/spatial/isovist.py` | Image_Tagger | ml | isovist-style spatial metrics. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/spatial/isovist_25d.py` | Image_Tagger | ml | 2.5D isovist variant logic. | prototype | specialized research path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/summary.py` | Image_Tagger | ml | summarization helpers for science results. | working | active production support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/tag_derivation.py` | Image_Tagger | ml | canonical tag derivation from science outputs. | working | active production path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision.py` | Image_Tagger | ml | top-level vision helper/orchestration module. | working | active production support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/__init__.py` | Image_Tagger | ml | package marker for vision code. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/clip_material.py` | Image_Tagger | ml | CLIP-based material inference integration. | prototype | optional enricher path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/mask2former.py` | Image_Tagger | ml | Mask2Former segmentation integration. | prototype | optional model integration |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/materials.py` | Image_Tagger | ml | material heuristics and enrichers. | working | current canonical path includes heuristics |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/room_detection.py` | Image_Tagger | ml | room type detection for canonical tags. | working | README says working |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/vision/segmentation.py` | Image_Tagger | ml | segmentation wrapper used by optional science paths. | prototype | README says disabled by default |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/audit_vlm_variance.py` | Image_Tagger | scripts | runs VLM variance auditing. | working | active ops tool |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/backfill_science_runs.py` | Image_Tagger | scripts | batch backfill runner for canonical science runs. | working | explicitly documented ops path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/bn_db_health.py` | Image_Tagger | scripts | checks BN-related DB health. | working | active ops tool |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/import_images_from_json.py` | Image_Tagger | scripts | imports images and metadata from JSON payloads. | working | active data-loading utility |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/migrate_3_4_63_add_validation_fk.py` | Image_Tagger | scripts | schema migration adding validation FK constraints. | working | active migration script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/migrate_3_4_74_add_science_tables.py` | Image_Tagger | scripts | schema migration adding canonical science tables. | working | active migration script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/seed_attributes.py` | Image_Tagger | scripts | seeds attribute metadata into the database. | working | active bootstrap script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/scripts/seed_tool_configs.py` | Image_Tagger | scripts | seeds runtime tool configs into the database. | working | active bootstrap script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/__init__.py` | Image_Tagger | backend | package marker for service layer. | working | standard package file |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/annotation.py` | Image_Tagger | backend | business logic for annotation workflows. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/auth.py` | Image_Tagger | backend | header-based RBAC and auth dependencies. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/costs.py` | Image_Tagger | backend | usage and cost accounting logic. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/query_builder.py` | Image_Tagger | backend | query/filter construction helpers. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/science_runs.py` | Image_Tagger | backend | orchestration for canonical science-run lifecycle. | working | central current path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/storage.py` | Image_Tagger | backend | storage abstraction for image/assets handling. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/training_export.py` | Image_Tagger | backend | exports validated data for training or BN workflows. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/upload_jobs.py` | Image_Tagger | backend | upload job orchestration and state management. | working | active service layer |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/services/vlm.py` | Image_Tagger | backend | VLM integration and request orchestration. | prototype | optional/stubbed cost-controlled path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/tests/test_health.py` | Image_Tagger | tests | backend health endpoint tests. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/tests/test_rbac.py` | Image_Tagger | tests | RBAC behavior tests. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/versioning.py` | Image_Tagger | backend | version helper utilities. | working | support module |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/contracts/attributes.yml` | Image_Tagger | config | contract-like source file for attribute definitions. | working | active reference config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deconcat.py` | Image_Tagger | scripts | utility to de-concatenate a packed repo/text bundle. | prototype | support migration utility |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deconcat_v3_3.py` | Image_Tagger | scripts | older de-concatenation helper for v3.3-era bundles. | archive | historical support utility |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deploy/.plan.md` | Image_Tagger | docs | planning note for deployment setup. | prototype | planning doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deploy/Dockerfile.backend` | Image_Tagger | config | backend container build file. | working | active deployment config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deploy/Dockerfile.frontend` | Image_Tagger | config | frontend/Nginx container build file. | working | active deployment config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deploy/docker-compose.yml` | Image_Tagger | config | compose stack for DB, API, and frontend gateway. | working | documented runtime config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/deploy/nginx.conf` | Image_Tagger | config | reverse proxy and SPA routing config. | working | active deployment config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ACTIVE_LEARNING_PIPELINE.md` | Image_Tagger | docs | active learning pipeline documentation. | prototype | process doc for evolving feature area |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/AI_COLLAB_WORKFLOW.md` | Image_Tagger | docs | workflow rules for AI-assisted collaboration. | working | current process guide |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/BN_EXPORT_EXAMPLE.md` | Image_Tagger | docs | BN export example and explanation. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/BN_MAPPING_COG_AFFECT.md` | Image_Tagger | docs | mapping guide for cognition and affect BN outputs. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/BN_NAMING_GUIDE.md` | Image_Tagger | docs | naming conventions for BN export fields. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/BN_PRIORS_COG_AFFECT_EXAMPLE.csv` | Image_Tagger | artifact | example CSV of BN priors. | artifact | example data artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/DEBUG_VIEWS_DOCUMENTATION.md` | Image_Tagger | docs | user/operator documentation for debug views. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/FIRST_DASHBOARD_QUICKSTART.md` | Image_Tagger | docs | quickstart for the first dashboard/operator experience. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/INTERPRETING_RUTHLESS_REPORTS.md` | Image_Tagger | docs | guide to reading internal review reports. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/PRODUCTION_DEPLOYMENT.md` | Image_Tagger | docs | deployment guidance for production-like environments. | working | active operator doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/SCIENCE_DEBUG_LAYERS.md` | Image_Tagger | docs | explanation of debug layers for science outputs. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/SCIENCE_TAG_MAP.md` | Image_Tagger | docs | mapping from science outputs to canonical tags. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/STUDENT_ONBOARDING.md` | Image_Tagger | docs | student onboarding guide. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/UPLOAD_JOBS_README.md` | Image_Tagger | docs | documentation for upload job workflow. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/VLM_CASE_STUDY_HUMAN_VS_AI.md` | Image_Tagger | docs | case study comparing human and AI outputs. | working | current collateral |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/VLM_INTEGRATION.md` | Image_Tagger | docs | VLM integration notes and operator guidance. | prototype | VLM path is optional/stubbed |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/WHATS_NEW_v3_3_x.md` | Image_Tagger | docs | older release notes for v3.3.x. | archive | historical release doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/devops_quickstart.md` | Image_Tagger | docs | devops quickstart for stack setup. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/governance_guide.md` | Image_Tagger | docs | guide to guardian and governance workflow. | working | active reference doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ops/Cloud_AntiGravity_Quickstart.md` | Image_Tagger | docs | cloud deployment quickstart. | working | active ops doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ops/Student_Quickstart_v3.4.73.md` | Image_Tagger | docs | older student quickstart from v3.4.73. | archive | versioned historical doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ops/Technical_Lead_Runbook_v3.4.74.md` | Image_Tagger | docs | current technical lead runbook for operators. | working | current ops doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ops/VLM_Health_Quickstart.md` | Image_Tagger | docs | quickstart for VLM health workflows. | working | active ops doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ops/VLM_Health_SOP.md` | Image_Tagger | docs | SOP for VLM health checks. | working | active ops doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/science_overview.md` | Image_Tagger | docs | overview of the current science architecture. | working | current architecture doc |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/index.html` | Image_Tagger | frontend | HTML entrypoint for the admin SPA. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/package.json` | Image_Tagger | config | package manifest for the admin SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/postcss.config.js` | Image_Tagger | config | PostCSS config for the admin SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/public/feature_navigator.html` | Image_Tagger | frontend | static admin feature navigator helper page. | prototype | auxiliary support page |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/public/feature_onboarding.html` | Image_Tagger | frontend | static admin onboarding helper page. | prototype | auxiliary support page |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/src/App.jsx` | Image_Tagger | frontend | main admin cockpit React app. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/src/main.jsx` | Image_Tagger | frontend | admin SPA bootstrap file. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/tailwind.config.js` | Image_Tagger | config | Tailwind config for the admin SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/admin/vite.config.js` | Image_Tagger | config | Vite config for the admin SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/index.html` | Image_Tagger | frontend | HTML entrypoint for the explorer SPA. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/package.json` | Image_Tagger | config | package manifest for the explorer SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/postcss.config.js` | Image_Tagger | config | PostCSS config for the explorer SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/src/App.jsx` | Image_Tagger | frontend | main explorer React app. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/src/ImageDetailModal.jsx` | Image_Tagger | frontend | explorer modal for image details and science status. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/src/main.jsx` | Image_Tagger | frontend | explorer SPA bootstrap file. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/tailwind.config.js` | Image_Tagger | config | Tailwind config for the explorer SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/explorer/vite.config.js` | Image_Tagger | config | Vite config for the explorer SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/index.html` | Image_Tagger | frontend | HTML entrypoint for the monitor SPA. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/package.json` | Image_Tagger | config | package manifest for the monitor SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/postcss.config.js` | Image_Tagger | config | PostCSS config for the monitor SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/src/App.jsx` | Image_Tagger | frontend | main monitor React app. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/src/main.jsx` | Image_Tagger | frontend | monitor SPA bootstrap file. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/tailwind.config.js` | Image_Tagger | config | Tailwind config for the monitor SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/monitor/vite.config.js` | Image_Tagger | config | Vite config for the monitor SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/index.html` | Image_Tagger | frontend | HTML entrypoint for the workbench SPA. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/package.json` | Image_Tagger | config | package manifest for the workbench SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/postcss.config.js` | Image_Tagger | config | PostCSS config for the workbench SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/src/App.jsx` | Image_Tagger | frontend | main tagging workbench React app. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/src/main.jsx` | Image_Tagger | frontend | workbench SPA bootstrap file. | working | active frontend app |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/tailwind.config.js` | Image_Tagger | config | Tailwind config for the workbench SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/apps/workbench/vite.config.js` | Image_Tagger | config | Vite config for the workbench SPA. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/dist/explorer/assets/index-DmnNZVCq.css` | Image_Tagger | artifact | built CSS bundle for the explorer app. | artifact | generated build output |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/dist/explorer/assets/index-rCY19lNP.js` | Image_Tagger | artifact | built JS bundle for the explorer app. | artifact | generated build output |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/dist/explorer/index.html` | Image_Tagger | artifact | built HTML entry for the explorer app. | artifact | generated build output |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/index.css` | Image_Tagger | frontend | shared global CSS for the frontend monorepo. | working | active frontend asset |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/index.html` | Image_Tagger | frontend | frontend shell HTML. | working | active frontend asset |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/package-lock.json` | Image_Tagger | config | lockfile for frontend npm dependencies. | working | normal dependency lock |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/package.json` | Image_Tagger | config | root package manifest for the frontend monorepo. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/postcss.config.js` | Image_Tagger | config | root PostCSS config for the frontend monorepo. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/package.json` | Image_Tagger | config | package manifest for shared frontend components. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/api-client.js` | Image_Tagger | frontend | shared API client used by multiple SPAs. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/components/Button.jsx` | Image_Tagger | frontend | shared button component. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/components/Header.jsx` | Image_Tagger | frontend | shared header/navigation component. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/components/MaintenanceOverlay.jsx` | Image_Tagger | frontend | shared maintenance mode overlay component. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/components/Toast.jsx` | Image_Tagger | frontend | shared toast notification component. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/components/Toggle.jsx` | Image_Tagger | frontend | shared toggle component. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/shared/src/index.js` | Image_Tagger | frontend | barrel export for shared frontend modules. | working | active shared frontend code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/tailwind.config.js` | Image_Tagger | config | root Tailwind config for the frontend monorepo. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/frontend/vite.config.base.js` | Image_Tagger | config | shared Vite base config for all SPAs. | working | active frontend config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/governance.lock` | Image_Tagger | config | frozen governance state file. | working | active governance artifact |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/governance/TODO_running_list.md` | Image_Tagger | docs | running governance TODO list. | prototype | internal TODO tracker |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/cloud/full_stack_vm_setup.sh` | Image_Tagger | scripts | VM bootstrap script for full-stack deployment. | working | active ops script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/turnkey_installer_v1.3/hooks/post_install_smoke.py` | Image_Tagger | scripts | smoke test run after turnkey installation. | working | active installer support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/turnkey_installer_v1.3/installer/install.sh` | Image_Tagger | scripts | packaged turnkey installer entrypoint. | working | active installer support |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/turnkey_installer_v1.3/installer_config.json` | Image_Tagger | config | local config for the turnkey installer. | working | active installer config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/turnkey_installer_v1.3/installer_config.sample.json` | Image_Tagger | config | sample config for the turnkey installer. | working | active installer config template |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/install.sh` | Image_Tagger | scripts | main installer/bootstrap script for the stack. | working | documented primary install path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/notebooks/VLM_Health_Lab.ipynb` | Image_Tagger | docs | notebook for VLM health analysis and experimentation. | prototype | notebook-based exploratory analysis |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/release.keep.yml` | Image_Tagger | config | release retention/config metadata. | working | active release config |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/reports/Ruthless_3.4.35_five_panel_summary.md` | Image_Tagger | docs | internal review report for five-panel summary work. | working | current review collateral |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/reports/Ruthless_3.4.50_upload_orchestrator_cost_view.md` | Image_Tagger | docs | internal review report for upload/cost view work. | working | current review collateral |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/requirements-install.txt` | Image_Tagger | config | install dependency list for the main app. | working | active environment manifest |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/science_tag_coverage_v1.json` | Image_Tagger | artifact | generated coverage report for science tags. | artifact | generated report |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scrapping/Interior Architecture Dataset Construction.ipynb` | Image_Tagger | docs | notebook for constructing an interior architecture dataset. | prototype | exploratory notebook |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scrapping/dataset_wiki_unsplash.csv` | Image_Tagger | artifact | scraped dataset manifest from Wikimedia/Unsplash work. | artifact | generated dataset asset |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scrapping/unsplash_test.py` | Image_Tagger | scripts | exploratory test for Unsplash scraping. | prototype | experimental ingestion code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scrapping/wikimedia_scrape` | Image_Tagger | artifact | scrape output or placeholder file for Wikimedia work. | artifact | generated or partial scrape output |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scrapping/wikimedia_test.py` | Image_Tagger | scripts | exploratory test for Wikimedia scraping. | prototype | experimental ingestion code |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/audit_vlm_variance.py` | Image_Tagger | scripts | root-level runner for VLM variance auditing. | working | active ops script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/bn_add_cog_affect_bins.py` | Image_Tagger | scripts | augments BN outputs with cognition/affect bins. | working | active data-processing script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/bn_merge_cog_affect_priors.py` | Image_Tagger | scripts | merges cognition/affect priors into BN assets. | working | active data-processing script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/canon_guard.py` | Image_Tagger | scripts | guard validating canonical-anchor consistency. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/check_no_pycache_in_tree.py` | Image_Tagger | scripts | repo hygiene check for stray pycache files. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/critical_import_guard.py` | Image_Tagger | scripts | import smoke check for critical modules. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/export_bn_glossary.py` | Image_Tagger | scripts | exports a BN glossary from project metadata. | working | active data-processing script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/export_bn_ready_dataset.py` | Image_Tagger | scripts | exports BN-ready datasets. | working | active data-processing script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/generate_tag_coverage.py` | Image_Tagger | scripts | generates science tag coverage reports. | working | active reporting script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/guardian.py` | Image_Tagger | scripts | governance verify/freeze tool. | working | central quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/hollow_repo_guard.py` | Image_Tagger | scripts | detects empty or placeholder repo areas. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/import_harness.py` | Image_Tagger | scripts | import harness for smoke-checking module loads. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/program_integrity_guard.py` | Image_Tagger | scripts | integrity guard over key program assets. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/run_science_on_sample.py` | Image_Tagger | scripts | runs the science pipeline on a sample image. | working | active dev/ops script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/run_upload_job.py` | Image_Tagger | scripts | runs or inspects upload jobs. | working | active dev/ops script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/science_harness.py` | Image_Tagger | scripts | harness for science pipeline experimentation. | working | active dev/ops script |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/smoke_api.py` | Image_Tagger | scripts | smoke test for the API surface. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/smoke_frontend.py` | Image_Tagger | scripts | smoke test for frontend availability. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/smoke_science.py` | Image_Tagger | scripts | smoke test for the science pipeline. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/syntax_guard.py` | Image_Tagger | scripts | syntax checker for Python files. | working | active quality guard |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/vlm_turing_test_prep.py` | Image_Tagger | scripts | prepares panels/data for VLM Turing-style evaluation. | prototype | niche analysis path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/scripts/vlm_turing_test_score.py` | Image_Tagger | scripts | scores VLM Turing-style evaluation results. | prototype | niche analysis path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_admin_killswitch.py` | Image_Tagger | tests | tests admin killswitch behavior. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_admin_upload.py` | Image_Tagger | tests | tests admin upload behavior. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_arch_patterns_vlm_vlm_path.py` | Image_Tagger | tests | tests or sanity-checks VLM architectural pattern pathing. | prototype | tied to optional VLM path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_biophilia.py` | Image_Tagger | tests | tests biophilia integration behavior. | prototype | tied to secondary ML path |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_bn_canon_sanity.py` | Image_Tagger | tests | sanity checks for BN canonical naming/state. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_bn_export_smoke.py` | Image_Tagger | tests | smoke test for BN export flow. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_explorer_smoke.py` | Image_Tagger | tests | smoke test for explorer behavior. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_feature_registry_coverage.py` | Image_Tagger | tests | validates feature registry coverage/integrity. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_governance_integrity.py` | Image_Tagger | tests | checks repo governance and protected files. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_guardian.py` | Image_Tagger | tests | tests guardian verification behavior. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_monitor_tag_inspector.py` | Image_Tagger | tests | tests monitor/tag inspector behaviors. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_pipeline_health_debug.py` | Image_Tagger | tests | tests pipeline health debug views. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_science_pipeline_smoke.py` | Image_Tagger | tests | smoke test for current science pipeline. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_science_runs.py` | Image_Tagger | tests | tests canonical science run lifecycle/state. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_tag_derivation.py` | Image_Tagger | tests | tests canonical tag derivation logic. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_v3_api.py` | Image_Tagger | tests | main v3 API and RBAC test suite. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_validation_attribute_fk_schema.py` | Image_Tagger | tests | validates DB/schema constraints for attribute foreign keys. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_vlm_safe_json_loads.py` | Image_Tagger | tests | tests safe JSON parsing for VLM outputs. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/tests/test_workbench_smoke.py` | Image_Tagger | tests | smoke test for workbench behavior. | working | active test coverage |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/v3_governance.yml` | Image_Tagger | config | governance rules for protected scopes and release discipline. | working | central policy file |

## Summary

| project | apparent_state | notes |
| --- | --- | --- |
| `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full` | mostly working with explicit prototype/broken subsystems | current active app; affordance ML is the clearest known broken area, and VLM/segmentation paths are optional or disabled by default |
| `TRS_v1.1` | working | smaller turnkey wrapper around bundled contracts, API, and Streamlit UI |
| `biophilia-index-main` | working research package | standalone ML package with heavier external model/dependency requirements |
