# Changelog

## OSL-Core 0.4 Receipt Hardening v0.1.0 — 2026-09-01

- Added the versioned `osl.core.receipt.v2` envelope and single-attempt runtime.
- Added source, AST, parse/static, statement-span, terminal, and final-state
  bindings.
- Removed empty fail-open traces for parse/static rejection.
- Added immutable capability grant epochs and exact before/after execution
  transitions.
- Rejected duplicate plan, execute, feedback, proof, and attestation identities.
- Bound capability proofs to the exact current grant rather than effect name.
- Made proof-gated write/plan/authorization checks atomic on failure.
- Fixed bounded-premise transfer and composite premise agent/scope alignment.
- Added exact packet constructor and memory/proof/action reconstruction.
- Added a separately labeled exact same-runtime replay for semantic categories
  outside the independent protected-state reconstruction.
- Blocked quarantine and rejected-status laundering.
- Fixed rollback of the runtime-private secret store and global audit spans.
- Hardened numeric parsing to reject malformed real literals explicitly.
- Preserved the frozen 66-source 42/24 behavioral outcome matrix.
- Added 32 Core 0.4 hardening tests, for 93 total passing tests.
- Added 24 fixed adversarial witnesses and raw traces for all 66 programs.
- Verified all three Discovery Bridge programs under Core 0.4 (71 receipts).

The frozen OSL v0.5 / Core 0.3 artifacts remain unchanged and retain only their
originally stated assurance.
