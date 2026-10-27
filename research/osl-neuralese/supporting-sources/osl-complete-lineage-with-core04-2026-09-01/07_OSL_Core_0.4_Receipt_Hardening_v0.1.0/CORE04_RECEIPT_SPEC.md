# OSL-Core 0.4 Receipt Protocol

Status: executable receipt specification for OSL-Core 0.4

Receipt schema: `osl.core.receipt.v2`

This document specifies the receipt lifecycle emitted by the packaged OSL-Core
0.4 runtime. It distinguishes a valid rejected program from an invalid trace.
A parse, static, runtime, or finalization rejection is a valid execution result
only when its complete receipt trace satisfies this specification.

## 1. Canonical hashing

Let `H(x)` be SHA-256 of the UTF-8 encoding of canonical JSON for `x`.
Canonical JSON sorts mapping keys, uses compact separators, and rejects NaN.

Every receipt has this common envelope:

| Field | Required value |
|---|---|
| `schema` | `osl.core.receipt.v2` |
| `core_version` | `0.4` |
| `index` | Zero-based global audit index |
| `state_index` | Zero-based state receipt index |
| `step` | Monotone runtime statement clock |
| `kind` | A recognized receipt kind |
| `transaction` | Active transaction name or `null` |
| `previous_digest` | Previous receipt digest, or 64 zeroes at index zero |
| kind-specific fields | Payload defined below or by the corresponding operator |
| `digest` | `H(receipt without digest)` |

For a conforming native 0.4 trace, `index` is contiguous, the hash chain is
valid, and `state_index == index`. Source-boundary spans always use the global
`index`, never a restored checkpoint-local offset.

The runtime emits one program attempt per `OSLRuntime` instance. A second call
to `run_text` or `run_file` on the same instance is rejected before another
attempt can be appended.

## 2. Program lifecycle

There is no receipt whose literal kind is `terminal`. A program terminal is
exactly one of:

- `program_complete`
- `program_reject`

The legal phase shapes are:

```text
program_open
  parse_reject
  program_reject(phase=parse)
```

```text
program_open
  parse_accept
  static_reject
  program_reject(phase=static)
```

```text
program_open
  parse_accept
  static_check
  statement frames
  program_complete(phase=complete)
```

```text
program_open
  parse_accept
  static_check
  committed statement frames
  rejected statement frame
  program_reject(phase=statement)
```

```text
program_open
  parse_accept
  static_check
  all statement frames committed
  program_reject(phase=finalization)
```

The trace must be nonempty. `program_open` must be first. Exactly one program
terminal must exist and it must be the final receipt. A receipt after a
terminal, two terminals, or a trace truncated before its terminal is invalid.
An empty source program is permitted, but it still emits `program_open`,
`parse_accept`, `static_check`, and `program_complete`. An empty receipt list is
never a valid empty program.

Unknown receipt kinds are invalid under strict v2 verification.

## 3. Opening and parse receipts

### `program_open`

The first receipt contains:

| Field | Meaning |
|---|---|
| `filename` | Diagnostic filename supplied to the runtime |
| `source_digest` | `H(source)`, where `source` is the exact input string |
| `source_bytes` | Length of `source.encode("utf-8")` |
| `source_lines` | `len(source.splitlines())` |

`filename` is diagnostic. It does not replace source binding.

### `parse_accept`

On successful parsing, the runtime emits:

| Field | Meaning |
|---|---|
| `ast_digest` | Digest of the ordered statement manifest |
| `statement_count` | Number of parsed nonblank, noncomment statements |

For statement `i`, the manifest is:

```json
{
  "ordinal": "i",
  "line_number": "original one-based source line",
  "kind": "parsed statement kind",
  "source": "stripped statement source",
  "args": "parsed argument mapping",
  "node_digest": "H(the five fields above)"
}
```

The actual values of `ordinal` and `line_number` are integers. They are shown as
descriptions above for readability. The AST digest is `H` of the ordered list
of complete manifests, including each `node_digest`.

### `parse_reject`

On parse failure, the runtime emits `parse_reject` with `error`, followed
immediately by `program_reject` with:

- `phase = "parse"`
- `reason_code = "E_PARSE"`
- `ast_digest = null`
- `statement_count = 0`
- `committed_count = 0`

No partial AST or statement boundary is admitted after parse rejection.

## 4. Static receipts

### `static_check`

Successful static validation emits:

| Field | Meaning |
|---|---|
| `ast_digest` | The digest from `parse_accept` |
| `report` | Canonical successful `StaticReport` |

`report` contains `ok`, `statement_count`, `symbol_counts`, `warnings`, and
`report_digest`. There is no receipt named `static_accept`; `static_check` is
the successful static-phase receipt.

### `static_reject`

Static rejection emits:

| Field | Meaning |
|---|---|
| `ast_digest` | The digest from `parse_accept` |
| `statement_count` | Parsed statement count |
| `error` | Deterministic diagnostic text |

It is followed immediately by `program_reject` with `phase = "static"` and
`reason_code = "E_STATIC"`. No statement is executed and no statement boundary
is emitted.

## 5. Statement boundaries

Every executed statement has exactly one trailing boundary:

- `statement_commit` for a successful statement
- `statement_reject` for the first rejected statement

Both kinds contain:

| Field | Required interpretation |
|---|---|
| `statement_ordinal` | Zero-based position in the AST |
| `line_number` | Original one-based line number |
| `statement_kind` | Parsed AST kind |
| `source_digest` | `H(statement.source)` |
| `node_digest` | Digest of the matching AST manifest |
| `before_semantic_digest` | State digest before the statement clock advances |
| `after_semantic_digest` | State digest after execution or rejection handling |
| `emitted_receipt_indices` | Exact ordered indices emitted by the statement |
| `effect_span` | Half-open global audit range `[start, end)` for those receipts |

In Python memory, the two range fields are tuples. Their JSON representation is
an array. If a boundary is at audit index `q`, its `effect_span` ends at `q`, so
the boundary does not include itself. The required equality is:

```text
emitted_receipt_indices == range(effect_span[0], effect_span[1])
effect_span[1] == boundary.index
```

The first span begins immediately after `static_check`. Every later span begins
immediately after the preceding statement boundary. Consequently, the spans
partition all operational receipts between `static_check` and the terminal.
Empty spans are legal for statements that emit no separate operational receipt.

Executed statement ordinals form a prefix of the AST:

```text
0, 1, ..., committed_count - 1
```

A statement rejection, if present, has ordinal `committed_count`. There can be
no later statement boundary. Boundary line, kind, line digest, and node digest
must match the independently parsed source statement.

Semantic continuity requires:

- the first `before_semantic_digest` equals the post-static initial semantic
  state digest;
- each committed boundary's `after_semantic_digest` equals the next boundary's
  `before_semantic_digest`;
- the final boundary's `after_semantic_digest` equals the terminal semantic
  digest;
- on a transactional rejection, the rejected boundary is measured after the
  automatic rollback receipt has restored the transaction projection.

`statement_reject` additionally contains `rolled_back` and `error`. Its effect
span includes `transaction_rollback` when automatic rollback occurred. It is
followed by `program_reject` with `phase = "statement"`,
`reason_code = "E_RUNTIME"`, and matching failed-statement fields.

A finalization rejection is different: every source statement already has a
commit boundary, and the terminal has `phase = "finalization"` and
`reason_code = "E_FINALIZATION"`. It has no rejected statement boundary.

## 6. Program terminal schema

Both `program_complete` and `program_reject` contain the same terminal shape:

| Field | Meaning |
|---|---|
| `outcome` | `accepted` or `rejected` |
| `phase` | `complete`, `parse`, `static`, `statement`, or `finalization` |
| `source_digest` | Must match `program_open` |
| `ast_digest` | Must match `parse_accept`, or be `null` on parse rejection |
| `statement_count` | Total parsed statements, or zero on parse rejection |
| `committed_count` | Number of committed statement boundaries |
| `failed_ordinal` | Failed AST ordinal for statement rejection, otherwise `null` |
| `failed_line` | Failed source line for statement rejection, otherwise `null` |
| `failed_statement_kind` | Failed AST kind for statement rejection, otherwise `null` |
| `reason_code` | Rejection code, or `null` on completion |
| `error` | Rejection diagnostic, or `null` on completion |
| `final_semantic_state` | Canonical receipt-facing semantic snapshot |
| `semantic_digest` | Digest embedded in `final_semantic_state` |
| `preterminal_chain_tip` | Digest of the receipt immediately before the terminal |
| `audit_receipt_count` | Total receipt count including the terminal |

The following equations are mandatory:

```text
terminal.previous_digest == terminal.preterminal_chain_tip
terminal.audit_receipt_count == terminal.index + 1 == len(trace)
terminal.semantic_digest == terminal.final_semantic_state.semantic_digest
terminal.semantic_digest == H(final_semantic_state without semantic_digest)
```

For `program_complete`:

```text
outcome == "accepted"
phase == "complete"
committed_count == statement_count
failed_ordinal == failed_line == failed_statement_kind == null
reason_code == error == null
```

For `program_reject`, `outcome == "rejected"` and its phase, reason code,
counts, and failed-statement fields must match the lifecycle path described
above. A valid rejection is a successful verification of a rejected execution;
it is not a successful program outcome.

The terminal semantic snapshot must equal the supplied final runtime projection
in both directions. The kernel additionally reconstructs the security-critical
module, identity, packet, proof, memory, capability, and action tables, plus
transaction lifecycle and protected rollback projections, and compares those
fields independently. Numerical and complete session refinement are not part
of that independent reconstruction: same-runtime replay binds the interpreter
output, and a dedicated finite result applies only where its check is explicitly
invoked and present. Rehashing a
terminal after changing its semantic digest, counts, source digest, or outcome
does not make it valid.

## 7. Transactions and rollback

OSL-Core 0.4 permits at most one active transaction. Nested transactions are
invalid even when their names differ. `execute` is forbidden inside a
rollbackable transaction because the finite runtime cannot undo an external
effect.

The transaction projection is:

```text
state.semantic_snapshot
  minus semantic_digest
  minus step
  plus private_secret_commitments = {
    secret_name: H(raw_secret_value)
  }
```

It deliberately excludes the monotone statement clock and audit evidence. It
includes the application state and commitments to the private secret store.

### `transaction_begin`

The receipt contains:

| Field | Meaning |
|---|---|
| `transaction` | Transaction name |
| `begin_audit_index` | Index of this `transaction_begin` receipt |
| `checkpoint_digest` | Digest of the transaction projection at entry |

The runtime deep-copies both `RuntimeState` and the raw private-secret mapping.

### `transaction_commit`

The receipt contains:

| Field | Meaning |
|---|---|
| `transaction` | Transaction name |
| `begin_audit_index` | Matching begin index |
| `begin_step` | Step at transaction entry |
| `body_effect_span` | Receipts after `transaction_begin` and before commit |
| `final_state_digest` | Digest of the committed transaction projection |

The span begins at `begin_audit_index + 1`. It includes the source boundary for
the `begin_transaction` statement because that boundary is emitted after the
`transaction_begin` receipt.

### `transaction_rollback`

Explicit and automatic rollback use the same receipt shape:

| Field | Meaning |
|---|---|
| `transaction` | Transaction name |
| `automatic` | Whether a runtime failure triggered rollback |
| `reason` | Rollback reason |
| `begin_audit_index` | Matching begin index |
| `begin_step` | Step at transaction entry |
| `checkpoint_digest` | Entry transaction-projection digest |
| `body_effect_span` | Half-open range after begin and before rollback |
| `pre_restore_digest` | Attempted transaction projection before restoration |
| `discarded_chain_tip` | Audit tip immediately before rollback |
| `discarded_receipt_count` | Length of `body_effect_span` |
| `restored_state_digest` | Restored transaction-projection digest |

The exact rollback invariants are:

```text
rollback.begin_audit_index == matching_begin.index
rollback.checkpoint_digest == matching_begin.checkpoint_digest
rollback.body_effect_span == [begin.index + 1, rollback.index)
rollback.discarded_receipt_count == rollback.index - begin.index - 1
rollback.discarded_chain_tip == trace[rollback.index - 1].digest
rollback.restored_state_digest == rollback.checkpoint_digest
```

Rollback restores all application objects and the raw private-secret mapping.
It does not restore `step`, the append-only audit, or diagnostic events. The
word `discarded` is semantic: attempted receipts remain in the audit chain.
After restoration, `state.receipts` mirrors the append-only audit rather than a
checkpoint-local receipt list.

For automatic rollback the order is:

```text
attempt receipts
transaction_rollback
statement_reject(rolled_back=true)
program_reject(phase=statement)
```

For explicit rollback, `transaction_rollback` lies inside the
`rollback_transaction` statement's effect span, followed by that statement's
`statement_commit`.

## 8. Operation receipt kinds

The strict v2 vocabulary additionally includes these implemented operation
kinds:

```text
module_declare lineage_declare agent_declare
capability_grant capability_revoke
space_declare vector_declare operator operator_apply transport
projector_check intertwiner_check
observe infer simulate inject neural_proposal communicate
bind quarantine endorse authorize neural_admission neural_rejection
trusted_attestation proof_construct proof_use proof_consume
memory_write plan execute feedback
contract_declare contract_check receipt_chain_verify
transaction_begin transaction_commit transaction_rollback
session_declare session_transition_declare session_terminal_declare
session_verify session_start session_advance
secret_register metadata_publish assert_pass show
```

Their kind-specific payloads are emitted before the enclosing statement
boundary and are covered by that boundary's exact effect span. Protected
authority and provenance transitions are replayed by the receipt kernel.
Same-runtime replay binds delegated interpreter semantics. Dedicated numerical
or complete protocol-graph results apply only where the corresponding finite
check is explicitly invoked and present; otherwise no such refinement claim
attaches. No internally rehashable receipt is authorization by itself.

## 9. Final-state correspondence

Strict verification has four separate obligations:

1. Reparse the supplied source and reproduce its source digest, AST manifest,
   AST digest, and static result.
2. Replay the recognized security-critical operation receipts and statement
   boundaries, including packets, memories, capability consumption, proof
   resources, protected actions, and transaction restore.
3. Compare that reconstructed protected state with the corresponding supplied
   final-state fields by canonical structural equality, not subset membership.
4. Recompute the complete terminal/final snapshot binding. The receipt kernel
   does not independently replay numerical algebra or the full session graph;
   a separately reported same-runtime replay binds those interpreter outputs,
   while a named finite-verifier result applies only when explicitly invoked
   and present in the package evidence.

The terminal binds `RuntimeState.semantic_snapshot()`. That receipt-facing
projection contains all modeled semantic collections, assertions, and `step`.
It commits to metadata using `source`, `step`, and `digest` while omitting the
raw metadata value. Raw secrets are absent and appear only through digests or
private transaction commitments.

The ordinary final snapshot separately contains full local metadata, the
successful static report, `receipt_count`, `receipt_chain_tip`, `event_count`,
and `snapshot_digest`. A strict verifier must recompute the snapshot digest and
require:

```text
final_state.receipt_count == len(trace)
final_state.receipt_chain_tip == trace[-1].digest
```

Every independently reconstructed protected category is checked in both
directions. In particular, the verifier must reject a final state that drops a
committed memory or action just as it rejects
one that invents an extra memory or action.

## 10. Explicit limits

- SHA-256 receipts provide integrity and tamper evidence, not principal
  authentication, signatures, freshness, or trusted timestamping.
- Source correspondence requires the exact source string. A receipt-only check
  cannot establish source correspondence and must not claim that guarantee.
- The AST and transition rules cover the packaged finite line-oriented grammar,
  not arbitrary Python, unbounded recursion, or an external language frontend.
- `final_semantic_state` is a redacted semantic projection. It does not disclose
  raw secrets or raw metadata values. Equality of hidden values is established
  only inside a trusted local execution or through their declared commitments.
- Rollback is an in-memory application-state guarantee. It does not reverse an
  effect that escaped the model. This is why `execute` is rejected while a
  rollbackable transaction is active.
- Only the transaction projection is restored. The statement clock, audit
  evidence, and diagnostic events remain monotone.
- A nontransactional `statement_reject` records the actual post-rejection
  semantic state. Core 0.4 does not make a blanket claim that every failed
  nontransactional statement is automatically rolled back.
- Floating numerical checks retain their declared tolerances and depend on the
  finite NumPy execution model. They are not exact real-arithmetic proofs.
- Session verification covers declared finite synchronous transition graphs. It
  does not prove asynchronous delivery, fairness, distributed consensus, or
  liveness of an external environment.
- Neural origin and relevance attestations remain explicit trust roots.
- The receipt verifier is executable assurance, not a proof-assistant theorem
  that the Python implementation is correct.

## 11. Legacy traces

OSL-Core 0.3 receipts use the older unversioned/v1 lifecycle and do not satisfy
this specification. In particular, old parse/static failures may have no
receipts, old source-boundary spans may use checkpoint-local indices, and old
receipts do not contain enough information for full-state reconstruction.

A legacy verifier may preserve their historical partial checks, but it must
label that assurance as legacy. Native v2 certification requires replaying the
original source under OSL-Core 0.4; a v1 receipt list cannot be upgraded into a
strict v2 proof by rehashing or field synthesis alone.
