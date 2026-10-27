# Revision Log — v0.3.2

**Author:** Komorebi P.

## v0.3.1 scientific freeze

- Froze the entry, finite observed-cone, repeated-relation, and matched-control
  scientific profile.
- Froze two learned checkpoints, sixteen coordinate episodes, relation repeat
  grids through 64 inserted tokens, and a 12-reference plus 48-control bank.
- The first execution attempt did not begin scientifically: its bootstrap read
  checkpoint raw bytes for SHA-256 authentication, then aborted before the
  run-start ledger, checkpoint deserialization, or endpoint evaluation.
- Recorded the failed attempt immutably as `results/V031_INVALID_ATTEMPT.json`.

## v0.3.2 execution correction

- Preserved the v0.3.1 scientific profile and all inherited frozen inputs.
- Tightened isolated execution, exact-path source loading, snapshot handling,
  durable artifact creation, execution locking, and lineage validation.
- Added an explicit abort disclosure and correction freeze.
- Passed 15 / 15 checkpoint-free structural tests before execution.
- Executed the learned endpoint once under the registered wrapper.
- Produced `results/V032_RUN_STARTED.json` and
  `results/V032_ENTRY_CONE_HOLONOMY_RESULTS.json`.
- Produced no `V032_INVALID_ATTEMPT.json`.

## Registered outcome

- Seven of seven integrity and eligibility gates passed.
- Eight of eight preregistered composites are true.
- Scientific outcomes `H0`, `X0`, and `X4` are false under the registered
  no-all-pass semantics.
- Result SHA-256:
  `134135524c0b7017c4611ce385b3853fc33d8d883d1716e60f3f6aa1c9ffba5c`.

## Post-hoc release layer

- Added a deterministic compact JSON summary and CSV tables.
- Added Python-only figures, including checkpoint-faceted relation exits and
  checkpoint-specific lexicographic matched-control comparisons.
- Added the present README, result summary, claim boundary, next-block design,
  release manifest, and verifier.
- These release-layer files do not alter frozen bytes or registered outcomes;
  they provide an explicitly post-hoc deterministic derivation and
  interpretation, hash-pinned by the release manifest.
