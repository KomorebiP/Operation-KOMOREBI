# AVOC v0.21.0 — verification record

## Final result

**PASS:** 112/112 final local compilation targets, 1,070/1,070 exact-name theorem
axiom reports, 47/47 substantive expected negative rejections, 12/12 current-source
live retry cases, and 7,204 exact accounting comparisons. The axiom union is only
`propext`, `Classical.choice`, and `Quot.sound`. No proof placeholder, project axiom,
native evaluation, or unsafe theorem declaration occurs in the scanned positive sources.

The post-build full axiom audit was rerun after the final 112-target compilation.
The final evidence collector independently requires current source/output/log hashes
and current live-test pins. See root `AUDIT.json` for the machine-readable result.

## Scope

This release starts from the mounted latest v0.20.0 ZIP with SHA-256
`985d618d5133b2870a048b2656a5840bdb322d65ebd612aa3c6de50f8438f445`.
Its 3,275 recorded payload hashes and ZIP CRC matched before source claims were
used. The earlier conversation contained more than one v0.20 artifact; this exact
snapshot is the baseline. Its inherited theorem inventory is 1,020.

New modules are AttemptAccounting, AttemptRecovery, AttemptCodec and AttemptExamples.
There are 50 new named theorems/lemmas, for a full inventory of 1,070, including
helpers and examples. All 100 inherited non-audit mathematical modules are unchanged.

## Current checking procedure

The pinned Lean runtime was restored from the seven supplied archive parts. Their
CRC/SHA checks and combined hash passed. Lean is 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d. The nine exact package revisions were checked.
Mathlib remains pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

The local build directory began empty. The inherited graph was rebuilt first for
development, new modules were checked, then every final local target was compiled
again with warnings as errors. External caches were retained. This is not a fresh
source rebuild of mathlib or an independent kernel implementation.

Authoritative final numbers, source/log/output hashes and return codes are in
the root AUDIT.json and final_local_build_summary.json, full_axiom_audit.json,
and final_negative_summary.json under results/v0.21.0. A source-only shortcut scan and
an independent comment-aware theorem count are also required by summarize_v021.py.

## Independent execution evidence

- 7,204 actual Lean accounting-gate requests compared to a separate Python oracle.
- 400 visited states across 16 small credit/count regimes, to event depth four.
- 796 accepted and 6,408 rejected requests, including malformed-invariant states.
- 12 real process/file scenarios, including SIGKILL before publication, a second
  interruption during retry authorization, stale-worker publication, a rollback
  inside retry publication, duplicate keys, input drift, both resource caps,
  administrative abandonment and committed-result reconciliation instead of retry.

The one-failure verification run finishes with 3 confirmed logical fees, 4 attempt
fees, 1 superseded attempt fee, exactly one admitted proof and posterior 1/2.
The interrupted-retry run finishes with 3 confirmed logical fees and 5 attempt
fees. The additional reservation is not refunded even where completed checker
work cannot be established after the crash.

The live tests re-ran in full after the status-reporting repair. Development records
are retained separately and do not count as final evidence. These tests do not
prove every physical execution, universal parser/filesystem refinement, or power-loss
safety. The general mathematical contracts are proved separately in Lean.

The corresponding new false claims have both positive-library obstruction proofs
and failed negative files: a refunded failed attempt, stale-generation publication,
and unbounded zero-fee retries. Import failures do not count as negative evidence.
