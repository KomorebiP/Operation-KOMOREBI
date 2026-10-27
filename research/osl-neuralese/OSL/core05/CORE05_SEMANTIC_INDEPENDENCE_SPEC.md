# OSL-Core 0.5 Semantic Independence Specification

Status: executable finite specification for OSL-Core 0.5

Runtime version: `0.5`

Receipt schema: `osl.core.receipt.v2`

Aggregate report schema: `osl.core05.semantic-independence-suite.v1`

## 1. Purpose

Core 0.5 reduces dependence on replaying the reference interpreter when
checking several previously delegated semantic domains. A verifier receives:

1. the exact source string;
2. the native receipt-v2 sequence;
3. the optional complete final runtime snapshot.

It then reconstructs bounded domain state and compares source statements,
effect-span receipts, domain transitions, and final projections. Component
verifiers do not import or invoke `OSLRuntime`. Their aggregate does not turn
same-runtime replay into an independent result.

The specification is executable assurance for the implemented finite grammar.
It is not a proof-assistant semantics or a universal interpreter-correctness
theorem.

## 2. Verification architecture

| Layer | Responsibility | Frontend relationship |
|---|---|---|
| Receipt-hardened base kernel | Source/lifecycle, hash chain, statement spans, packets, proofs, memories, capabilities, actions, protected rollback | Uses primary parser and static checker |
| Numeric verifier | Spaces, vectors, operators, application, transport, projector/intertwiner predicates, numerical rejection cases | Parses its bounded source fragment separately |
| Contract verifier | Five contract templates, deadline obligations, checks, finalization, contract rollback | Parses its bounded source fragment separately |
| Session verifier | Declarations, transitions, finite graph report, start/advance/history/terminal state, session rollback | Parses its bounded source fragment separately |
| Metadata verifier | Secret commitments, metadata records, assertion accounting, `show` binding, metadata rollback | Does not invoke the runtime, but uses the primary parser |
| Intrinsic verifier | Report emitted by each `verify_receipts` statement | Does not invoke the runtime, but uses the primary parser |
| Aggregate | Runs all five semantic components fail closed and preserves their separate reports | No interpreter replay |
| Supplementary replay | Exact runtime receipt and final-state comparison | Same implementation family, therefore not independent |

The aggregate passes only when every component returns a mapping whose
`all_checks_pass` value is exactly `true`. Component exceptions are converted
to failing reports.

## 3. Common evidence obligations

Within each component's scope, verification requires the following as
applicable:

- source statements are bound to their enclosing statement boundary and exact
  effect span;
- tracked receipts use the declared receipt kind and exact payload schema;
- tracked receipt values correspond to source operands and reconstructed prior
  state;
- transitions are applied in source order with the recorded statement step;
- explicit and automatic rollback restore the component's checkpointed state;
- reconstructed terminal and final-state fields match in both directions;
- malformed inputs fail closed rather than receiving a partial success claim.

The surrounding base kernel remains responsible for the complete receipt
envelope, global chain, terminal lifecycle, and protected-state categories.

## 4. Numerical semantics

The numeric component independently reconstructs:

- positive-dimensional spaces;
- finite one-dimensional vectors with exact declared dimension;
- finite rectangular operator matrices with exact source/target shape;
- the allowed operator kinds `linear`, `projector`, `transport`, and
  `external`;
- matrix-vector application;
- same-space similarity transport `T A T^-1`;
- projector declaration idempotence and explicit projector residual checks;
- intertwiner residual checks;
- numerical state restoration on explicit and automatic rollback;
- source-authorized numerical rejections covered by its finite predicates.

Tracked numerical receipts must use exact schemas. Rehashing a forged result,
residual, operator, vector, or extra payload field does not make it valid.
Numerical conventions and trusted assumptions are specified in
`CORE05_NUMERIC_PROFILE.md`.

## 5. Contract semantics

The contract component reconstructs these implemented templates:

- `no_foreign_observed`;
- `no_simulated_observed`;
- `quarantine_blocks_endorsement`;
- `capability_confinement`;
- `feedback_deadline`.

For a feedback deadline, an `execute` event creates a due step equal to the
current statement step plus `within`. Matching feedback removes the pending
obligation. An ordinary check rejects only after the due step; finalization
rejects any obligation still pending. Contract violations are recorded before
the associated rejection. The verifier reconstructs declaration state,
pending obligations, explicit checks, finalization outcomes, and per-domain
transaction restoration.

## 6. Session semantics

The session component reconstructs finite synchronous protocols consisting of
participants, an initial state, keyed communication transitions, declared
terminal states, an optional finite verification report, execution history,
current state, and active status.

It independently recomputes:

- the declared finite state set;
- reachable and unreachable states;
- reachable nonterminal deadlocks;
- terminal states with outgoing transitions;
- reachable states without a terminal path;
- the report digest and aggregate graph-check result.

A session-bound `communicate` must advance from the exact current state using
the exact sender and receiver. The `session_advance` receipt precedes the
packet-level `communicate` receipt. Entering a declared terminal deactivates
the session. A failed `verify_session` still stores and emits the failing graph
report before the statement rejects, matching the language semantics.

These checks concern finite synchronous graphs. They do not prove fairness,
asynchronous delivery, Byzantine safety, or external distributed liveness.

## 7. Metadata-facing semantics

The metadata component reconstructs:

- source-bound raw secret values inside the verifier and their public
  commitments;
- literal and secret-derived metadata records of the form
  `{value, source, step, digest}`;
- assertion receipt bodies and monotone successful assertion count;
- the binding between a `show` receipt and its enclosing boundary digest;
- per-domain restoration of secrets, metadata, and assertion count.

This verifies assertion accounting, not the general semantic truth of all
fourteen assertion forms. Some assertion predicates are covered indirectly by
other reconstructed domains, but no universal assertion-truth claim attaches.

Source-bound verification can require access to secret literals. Hashes of
low-entropy values are commitments, not confidentiality guarantees.

## 8. Audit intrinsic

For every `verify_receipts` statement, the intrinsic component recomputes the
receipt-chain report over the exact prefix preceding the
`receipt_chain_verify` receipt. It verifies index continuity, previous-digest
linkage, individual receipt digests, prefix count, prefix chain tip, failure
list, aggregate result, and report digest.

This is an integrity check. It does not establish the semantic truth of
unrelated receipt payloads.

## 9. Transaction boundary

Numeric, contract, session, and metadata-facing components independently test
rollback of their own reconstructed tables. The base kernel also reconstructs
its protected tables and private-secret commitments.

Core 0.5 does not yet combine every domain into a second complete semantic
state and independently recompute every `checkpoint_digest`,
`final_state_digest`, `pre_restore_digest`, and `restored_state_digest` over the
exact complete cross-domain transaction projection. These digests remain
bound by the primary runtime, receipt lifecycle, component-local checks, and
supplementary replay. They must not be described as completely independently
reconstructed.

## 10. Rejection boundary

The numerical, contract, and session components independently decide the
bounded rejection predicates they implement. Parse/static envelopes and the
protected-state kernel cover other named checks. Core 0.5 does not provide an
independent second interpreter for every possible runtime rejection cause.

Accordingly, out-of-domain rejection causality remains delegated. Stable broad
terminal codes such as `E_RUNTIME` identify phase, not a complete independent
proof of the exact underlying predicate.

## 11. Evidence gates

The packaged release records:

| Gate | Observed result |
|---|---:|
| Full tests | 168/168 |
| Focused semantic-independence tests | 75/75 |
| Packaged corpus | 66/66 |
| Native receipts | 1,825 |
| Discovery Bridge | 3/3 programs, 71 receipts |

The 66-program matrix remains 42 accepted programs and 24 expected
rejections. The focused gate includes positive reconstruction, malformed
input, fully rehashed semantic mutations, rollback cases, aggregate
integration, and language hardening. These are finite observed results, not an
exhaustive theorem over all valid OSL programs.

## 12. Remaining trusted assumptions and exclusions

- Python, NumPy, canonical JSON, SHA-256 implementations, and the host platform
  remain in the trusted computing base.
- Some verification paths share the primary parser and static checker.
- Diagnostic `event_count` is not independently reconstructed.
- SHA-256 authenticates no human, agent, process, or machine identity.
- Symbolic OSL capabilities are not an operating-system sandbox or external
  enforcement mechanism.
- Trusted neural origin and relevance attestations remain trust roots. Their
  presence does not prove truth, awareness, intent, or world grounding.
- The Discovery Bridge result is restricted to its explicitly finite worlds
  and does not establish open-world operator discovery.
- No mechanized proof or universal noninterference, liveness, security, or
  semantic-truth theorem is claimed.
