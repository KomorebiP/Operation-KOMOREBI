# OSL-Core 0.5 Semantic Independence v0.1.0

OSL-Core 0.5 extends the Core 0.4 receipt-hardened runtime with separately
implemented semantic verifiers for the finite numerical, contract, session,
metadata-facing, and audit-intrinsic fragments. These verifiers operate on
supplied source, receipts, and final state without importing or invoking
`OSLRuntime`. Same-runtime replay remains supplementary and is not counted as
independent semantic evidence.

This is a separate executable development release. It does not rewrite the
frozen Operator Symbolic AI Language v0.5 / OSL-Core 0.3 package or relabel
Core 0.4 evidence.

## What changed

- added independent reconstruction of spaces, vectors, operators,
  applications, transport, and finite projector/intertwiner checks;
- added independent reconstruction of all five implemented temporal-contract
  templates and feedback-deadline obligations;
- added independent finite-session declaration, graph-verification, start,
  advancement, history, terminal, and per-domain rollback checks;
- added reconstruction of secret commitments, metadata values, assertion
  accounting, `show` bindings, and their per-domain rollback behavior;
- added independent recomputation of reports embedded by `verify_receipts`;
- added a fail-closed aggregate semantic report that keeps component results
  separate;
- rejected unknown operator kinds, duplicate transport results, duplicate
  secret or metadata names, invalid inference confidence, nonfinite numerical
  input, dimension-incompatible projectors, and invalid check tolerances;
- retained the versioned `osl.core.receipt.v2` lifecycle while changing the
  receipt `core_version` to `0.5`.

## Verified release facts

| Gate | Result |
|---|---:|
| Packaged source corpus | 66/66 |
| Accepted / expected rejection | 42 / 24 |
| Native Core 0.5 receipts | 1,825 |
| Independent semantic aggregate | 66/66 |
| Full test suite | 168/168 |
| Focused Core 0.5 suite | 75/75 |
| Discovery Bridge | 3/3 programs, 71 receipts |

The focused suite contains positive reconstruction, malformed-input,
fully-rehashed semantic-mutation, rollback, integration, and language-hardening
cases. It is a fixed finite gate, not exhaustive adversarial testing.

## Independent coverage

The aggregate in `reference/osl_semantic_kernel.py` combines five bounded
components:

| Component | Independently reconstructed surface |
|---|---|
| Numeric | Spaces, vectors, operators, application, transport, projector and intertwiner checks |
| Contracts | Five templates, feedback deadlines, explicit checks, finalization, per-domain rollback |
| Sessions | Finite graphs, reports, lifecycle, history, terminal transitions, per-domain rollback |
| Metadata | Secret commitments, metadata records, assertion counts, `show` bindings, per-domain rollback |
| Intrinsics | The receipt-prefix report emitted by `verify_receipts` |

The receipt-hardened protected-state kernel inherited from Core 0.4 remains
responsible for source/lifecycle, packets, proofs, memories, capabilities,
actions, and protected rollback checks. Exact same-runtime replay is retained
as a separate compatibility and determinism signal.

## Important limits

Core 0.5 does not yet independently establish:

- the general truth of all fourteen assertion forms;
- the exact complete cross-domain transaction projection and every associated
  projection digest;
- rejection causality outside the predicates reconstructed by the component
  verifiers;
- diagnostic `event_count` reconstruction;
- independent parsing and static checking in every path. The base, metadata,
  and intrinsic paths still share primary frontend components.

The implementation and numerical profile remain within the Python and NumPy
trusted computing base. Evidence is finite-corpus executable assurance, not a
mechanized proof. SHA-256 binds bytes but authenticates no identity. OSL
capabilities are symbolic and are not an operating-system sandbox. Trusted
neural origin and relevance attestations remain trust roots rather than proofs
of semantic truth.

Read [CORE05_SEMANTIC_INDEPENDENCE_SPEC.md](CORE05_SEMANTIC_INDEPENDENCE_SPEC.md),
[CORE05_NUMERIC_PROFILE.md](CORE05_NUMERIC_PROFILE.md),
[CORE05_COMPATIBILITY.md](CORE05_COMPATIBILITY.md), and
[CLAIM_BOUNDARY.md](CLAIM_BOUNDARY.md) before making release claims. The native
trace bundle is `CORE05_TRACE_BUNDLE.jsonl`; generated summaries are
`CORE05_CONFORMANCE_REPORT.json`, `CORE05_SEMANTIC_REPORT.json`,
`CORE05_FOCUSED_REPORT.json`, and `CORE05_DISCOVERY_BRIDGE_REPORT.json`.

## Offline verification

Install the dependency ranges from `requirements.txt`, then run the packaged
Core 0.5 entry point with `./verify_core05.sh` on Bash or
`.\verify_core05.ps1` on PowerShell. Successful verification requires no
network after dependencies are installed.
