# Changelog

## v0.3.2

Reporting-only hardening; the v0.3.0 scientific protocol, source lock, task profiles, frozen thresholds, and all scientific gates remain unchanged.

- Fixed `summarize_result.py` for terminal smoke results where covariance calibration is intentionally disabled and recorded as `null`.
- Added explicit terminal-status interpretation and robust handling of unavailable optional fields.
- Added regression tests for `LATENT_UNUSED` and disabled covariance calibration.
- No checkpoint result, pre-audit seal, intervention, donor plan, or acceptance criterion is changed.

## v0.3.1

Infrastructure-only hardening; the v0.3.0 scientific protocol and all frozen gates remain unchanged.

- Added `download_external_assets.py` with exact checkpoint and base-model revision pins.
- Confirmed the primary raw checkpoint filename as `checkpoint_37`.
- Restricted GPT-2 acquisition to the seven files required by this adapter instead of the full multi-framework repository.
- Added automatic standard HTTP/LFS retry when Hugging Face Xet transfer is unavailable.
- Added explicit `DisableXet`/`LocalFilesOnly` setup modes and automatic compatible-Python discovery.
- Added a complete asset receipt with checkpoint SHA-256, checkpoint size, base-model tree SHA-256, revisions, and transfer mode.
- Added asset-plan and allowlisted-payload hash tests and raised the validated suite to 27 tests across 18 modules.
- Preserved `EXTERNAL_EXECUTION_NOT_RUN`: no third-party checkpoint metric is introduced by this patch.

## v0.3.0

- Reframed PrOntoQA's maximum causal claim as content/proof-instance specificity.
- Added an explicit `specificity_claim` configuration field.
- Added group-disjoint covariance-calibration support.
- Prevented semantic final traces from being captured before quotient sealing.
- Moved gold explicit-CoT evaluation to a post-seal witness stage.
- Added a v2 external source lock covering upstream code, requirements, PrOntoQA, ProsQA, checkpoint revisions, and GPT-2 revision.
- Added full checkpoint and local base-model tree fingerprints to real staging.
- Added `verify-source` and `stage-fake` commands.
- Strengthened the engineered pre-audit seal.
- Added source-lock, chronology, calibration-isolation, and claim-scope tests.
- Added a separate ProsQA procedure-specific follow-up protocol.

## v0.2.0

- Added semantic escalation and causal subspace patching.
- Added source-faithful recurrence parity test and capture cache.

## v0.1.0

- Initial replay, necessity, order, noise, donor, twin, and truncation protocol.
