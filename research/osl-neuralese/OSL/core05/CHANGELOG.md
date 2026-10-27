# Changelog

## OSL-Core 0.5 Semantic Independence v0.1.0 — 2026-09-01

- Added separate numerical, contract, finite-session, metadata-facing, and
  audit-intrinsic semantic verifiers that do not import or invoke `OSLRuntime`.
- Added the fail-closed `osl.core05.semantic-independence-suite.v1` aggregate
  without treating same-runtime replay as independent evidence.
- Independently reconstructed spaces, vectors, operators, application,
  transport, projector checks, and intertwiner checks.
- Independently reconstructed all five implemented contract templates,
  feedback deadlines, finite session graphs, session lifecycle, secret
  commitments, metadata records, assertion accounting, `show` bindings, and
  embedded receipt-prefix reports within their declared scopes.
- Added component-local explicit and automatic rollback verification for the
  new semantic domains.
- Rejected unknown operator kinds, duplicate transport results, duplicate
  secret and metadata names, invalid inference confidence, malformed or
  nonfinite numerical input, incompatible projectors, and invalid numerical
  tolerances.
- Preserved receipt schema `osl.core.receipt.v2` with native
  `core_version = 0.5` evidence.
- Preserved the packaged 66-source 42-accept / 24-reject outcome matrix and
  generated 1,825 native receipts.
- Passed 168/168 full tests and the fixed 75/75 focused Core 0.5 gate.
- Passed all three Discovery Bridge programs with 71 native receipts.
- Kept the remaining gaps explicit: general truth of all assertion forms,
  exact complete cross-domain transaction projection reconstruction,
  out-of-domain rejection causality, diagnostic `event_count`, and shared
  primary frontend components in some verification paths.

The Python and NumPy implementation remains a finite executable trusted
computing base, not a mechanized proof. The evidence is a finite corpus;
SHA-256 is not identity authentication; symbolic capabilities are not an OS
sandbox; and neural origin/relevance attestations remain trust roots. Core 0.5
does not alter or relabel the frozen OSL v0.5 / Core 0.3 package or the separate
Core 0.4 release.

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
