# OSL-Core 0.4 Compatibility Contract

## Frozen upstream baseline

The canonical upstream baseline is **Operator Symbolic AI Language v0.5**, whose executable language is **OSL-Core 0.3**. That release is frozen. Its source files, examples, reports, PDF, manifest, checksums, and stated claim boundary are historical artifacts and must not be silently edited or relabeled.

This package is a separate **OSL-Core 0.4 receipt-hardening release**. It strengthens the runtime and independent receipt verifier. It does not retroactively turn the v0.5 paper into an OSL-Core 0.4 specification, and it does not invalidate the v0.3 results within the checks those results actually performed.

The frozen v0.3 baseline reported:

- 66 packaged source programs
- 42 accepted programs
- 24 expected safe rejections
- 1,149 deterministically regenerated receipts
- 70 proof terms
- 61 focused tests

These numbers describe the v0.3 corpus. Native v0.4 receipt totals may differ because hardening can add envelope, declaration, lifecycle, or rejection evidence. A v0.4 release must report the measured native totals rather than copying the v0.3 receipt count.

## Two compatibility profiles

### `v0.4-native`

A native artifact is produced by the OSL-Core 0.4 runtime and checked under the complete v0.4 receipt rules. Native certification requires a versioned program envelope that binds:

- the canonical `H(source)` commitment to the exact source string and the
  normalized AST digest
- the source language and runtime version
- parsing and static-check disposition
- execution phase and stable outcome code
- the receipt count and chain tip
- exactly one terminal disposition
- the final semantic-state digest
- the verifier and kernel schema versions

The native verifier must fail closed on an unknown schema, unknown receipt kind, missing terminal disposition, conflicting terminal dispositions, a terminal receipt followed by more receipts, or an envelope/trace/state disagreement.

Native status additionally applies the v0.4 capability ledger, proof-constructor, provenance, action-lifecycle, transaction, source-boundary, and final-state checks. Passing a v0.3 compatibility check is not a substitute for native certification.

### `v0.3-legacy`

A legacy artifact is frozen v0.3 source or a deterministically regenerated v0.3 trace checked under an explicitly versioned compatibility profile. The compatibility verifier may bind the old receipt chain in a sidecar envelope and may apply stronger checks when the old receipts contain enough evidence. It must not claim that missing v0.4 evidence was present in the old trace.

The permitted result label is `LEGACY_COMPATIBLE`, not `V04_NATIVE_VERIFIED`. Any limitation discovered while replaying an old trace must remain visible in the per-program compatibility record.

## Corpus outcome matrix

The v0.4 conformance target preserves the complete 66-program outcome split.

| Corpus class | Programs | Count | Frozen v0.3 receipts | v0.4 target |
|---|---|---:|---:|---|
| Accepted completion | `01` through `42` | 42 | 796 | Accept |
| Statement-time rejection | `91`, `92`, `93`, `94`, `95`, `96`, `97`, `99`, `100`, `101`, `104`, `105`, `106`, `107`, `108`, `110`, `111`, `112`, `113`, `114` | 20 | 325 | Reject with stable code |
| Completion-time rejection | `98`, `109` | 2 | 28 | Reject with completion-phase envelope |
| Static rejection | `102`, `103` | 2 | 0 | Reject with static-phase envelope |
| **Total** |  | **66** | **1,149** | **42 accepted, 24 rejected** |

Correct rejection is part of conformance. A run that accepts any negative fixture, rejects any positive fixture, or merely changes an error string without preserving the intended stable error class does not satisfy the target.

### Required legacy envelopes

All 66 compatibility records should have an outcome envelope. Four programs require one to express a strict terminal result because their v0.3 receipt evidence alone is incomplete for the v0.4 schema:

- `98_feedback_contract_violation.osl` is rejected during final contract discharge. Its v0.3 `program_reject` does not contain statement-level failure metadata.
- `109_linear_proof_unconsumed.osl` is rejected during final linear-resource discharge. Its v0.3 `program_reject` does not contain statement-level failure metadata.
- `102_unknown_proof_static.osl` fails static checking before any receipt is emitted.
- `103_nested_transaction.osl` fails static checking before any receipt is emitted.

For the two completion failures, the envelope records `phase = completion`. For the two zero-receipt failures, it records `phase = static`, an empty receipt sequence, and the static result bound to the source digest. An envelope authenticates neither a principal nor the truth of the error. It makes the artifact and claimed disposition internally bindable.

### Deferred session-source migration

Three accepted v0.3 programs are legacy order monitors rather than graph-level
liveness certificates. Their frozen sources and traces remain valid legacy
fixtures.

This Core 0.4 package deliberately preserves the byte-identical 66-source
corpus and does **not** apply the following optional migration. Its
`V04_NATIVE_VERIFIED` status concerns the native receipt profile; it is not a
new graph-level liveness certificate for these three legacy order monitors. A
future migrated corpus would need these additions before claiming that stronger
session result:

| Program | Native addition |
|---|---|
| `24_session_protocol.osl` | Declare `ready` terminal and run `verify_session CooperativeDiagnosis` |
| `33_session_three_agent.osl` | Declare `complete` terminal and run `verify_session Relay` |
| `36_static_complex.osl` | Declare `done` terminal and run `verify_session S` |

Programs `39_verified_terminal_session.osl` and `42_verified_three_agent_session.osl` already declare terminals and invoke graph verification. A migrated copy is a new v0.4 source artifact. It must not replace the frozen legacy source.

### Rejection classification

The current native envelope exposes stable phase-level identifiers:
`E_PARSE`, `E_STATIC`, `E_RUNTIME`, and `E_FINALIZATION`. Corpus conformance
still matches the deterministic fixture marker within the diagnostic text.
Granular stable identifiers for memory provenance, endorsement, capability,
projector-law, proof, session, feedback, and neural-attestation failures remain
a deferred language-profile improvement; this release does not claim them.

`107_transaction_auto_rollback.osl` should expose a transaction rollback outcome with the projector-law failure retained as its cause. A generic rollback code alone loses useful semantic information.

## Receipts cannot be upgraded in place

A receipt digest commits to the exact receipt payload and the previous digest. Adding a version field, changing a kind, inserting a lifecycle event, adding a terminal field, correcting a capability rule, or changing an index changes that receipt and every later chain digest.

Consequently:

1. A v0.3 receipt chain must remain byte-for-byte v0.3 evidence.
2. A sidecar envelope may bind that chain and identify its limitations, but it does not convert the chain into v0.4 evidence.
3. Rehashing modified v0.3 receipts produces a new derived chain, not an upgraded original.
4. Re-executing frozen source under OSL-Core 0.4 produces a native v0.4 trace with a new identity.
5. No artifact may retain v0.3 receipt bytes while changing only its label to `OSL-Core 0.4`.

The v0.5 package contains receipt-verification summaries rather than a stored raw receipt file for every program. Raw legacy bundles created for this release are therefore new snapshots produced by deterministic replay of frozen sources. Their envelopes must say so and bind the source, replay implementation, generated receipt sequence, and final state.

## Release verification matrix

The achieved native release gate is:

- the 61 inherited regression tests
- 32 focused v0.4 hardening tests
- 93 total passed tests
- zero failed, skipped, or expected-failure tests
- all 66 corpus outcomes preserved
- runtime and independent-kernel outcomes compared for all 66 programs
- every adversarial mutation rejected for its intended property

`TEST_REPORT.json` records the achieved gate: 93 passed, zero syntax failures,
and no skipped or expected-failure cases.

The full `v0.3-legacy` sidecar gate described above—including 64 nonempty
legacy traces and two source-bound zero-receipt envelopes—was not executed for
this package and has status `NOT_RUN`. The byte-identical frozen reports are
retained with their original assurance; they are not relabeled
`LEGACY_COMPATIBLE` or `V04_NATIVE_VERIFIED`.

Integrity verification and semantic verification are separate gates. Manifest and SHA-256 checks establish byte integrity. Live semantic verification reruns tests and source/trace/kernel checks in a clean temporary directory and compares canonical generated reports. Neither gate establishes authorship.

## Compatibility status vocabulary

When a report emits a compatibility status, it should use this unambiguous
vocabulary:

- `V04_NATIVE_VERIFIED`: emitted and checked under all required v0.4 rules
- `LEGACY_COMPATIBLE`: checked under the declared v0.3 compatibility profile
- `SOURCE_OUTCOME_COMPATIBLE`: re-execution preserves the expected accept/reject class
- `MIGRATION_REQUIRED`: the legacy artifact lacks evidence required for native status
- `NOT_RUN`: the relevant check was not executed
- `UNSUPPORTED`: the feature lies outside the verifier's declared model

These statuses must not be collapsed into a single undifferentiated `PASS`.
