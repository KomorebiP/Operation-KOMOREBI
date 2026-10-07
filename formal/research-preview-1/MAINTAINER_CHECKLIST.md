# Release and repository checklist

This is a checklist for Research Preview 1, not a new research roadmap. The
mathematical checkpoint is fixed at Block 34. No later block is required for launch.

## Private staging

- [x] Prepare a sanitized source tree, source-identity checks, and separate evidence labels.
- [x] Add read-only CI definitions, review templates, and a private-only upload helper.
- [x] Retain pseudonymous public identity and no-reply commit metadata.
- [ ] Create or select the intended private remote and verify its owner and visibility.
- [ ] Upload only the sanitized history and verify the remote main commit.
- [ ] Run the artifact and reference workflows on the remote; inspect their receipts.

## Proof reproduction

- [x] Run the complete local clean proof replay on unchanged release inputs using the restored exact runtime/cache.
- [x] Validate all fresh command/log records, axiom coverage, negative controls, and before/after proof-input hashes.

- [ ] Run the manual pinned Lean workflow on the final candidate commit.
- [ ] Inspect its public bootstrap, source hashes, build, axiom inventory, and negative controls.
- [ ] Retain the fresh receipt independently of historical evidence and finite experiments.

A skipped, missing, or timed-out proof job does not satisfy this gate. A passing
artifact/reference workflow is not a substitute. Stable-version migration is not
required, but the exact working pinned toolchain must be obtainable and reproducible.

## Publication decision

- [ ] Approve project-specific distribution terms and required third-party notices.
- [ ] Complete owner review of all public files, metadata, and selected evidence.
- [ ] Review claims, attribution, correction policy, and the Future Research boundary.
- [ ] Set the real repository and citation location only after it exists.
- [ ] Approve publication explicitly, produce the final tagged archive, and verify its hashes.

No workflow or helper here changes visibility, chooses a license, or publishes a
GitHub Release. Repository protections and private reporting must be configured
in the actual GitHub settings where supported; a CODEOWNERS file is not itself
branch protection. Do not describe these settings as active until verified.
