# OSL-Core 0.3 Language Reference

OSL-Core is a deterministic, line-oriented operator-symbolic research language. Each source statement occupies one line. Programs are parsed into an explicit AST, statically checked, and then executed by a provenance- and effect-aware runtime.

## 1. Execution model

The execution pipeline is:

```text
source
  → AST
  → static symbol and reference checks
  → deterministic small-step execution
  → proof, capability, contract, and session checks
  → canonical receipts
  → private snapshot and public projection
```

Static rejection occurs before runtime state is installed. Runtime rejection is explicit and safe; if rejection occurs inside a transaction, the transaction restores its checkpoint.

## 2. Core declarations

```text
module diagnosis
lineage L_A
lineage L_B extends L_A
agent A lineage L_A
agent B lineage L_B
```

A lineage is a named temporal or causal provenance root. The finite core stores parent relations but does not automatically prove biological, legal, or philosophical identity.

## 3. Numerical spaces and operators

```text
space X dim 3
vector x in X values [1,2,3]

operator P : X -> X
    kind projector
    matrix [[1,0,0],[0,1,0],[0,0,0]]

check_projector P tolerance 1e-10
apply self_part = P(x)
```

Coordinate transport is explicit:

```text
operator T : X -> X
    kind transport
    matrix [[0,1,0],[1,0,0],[0,0,1]]

transport P via T as P_new
check_projector P_new tolerance 1e-10
```

Semantic intertwiners are checked with:

```text
check_intertwiner T between Aop and Bop tolerance 1e-10
```

The runtime supports finite matrices and vectors only. Nonlinear maps, tensors, manifolds, and neural operators remain manuscript-level extensions.

## 4. Provenance-aware packets

### Direct observation

```text
observe obstacle by B
    content "route three is blocked"
    confidence 0.94
```

A direct observation creates an observed packet, origin lineage, access for the observer, and a direct-observation basis for a later ownership proof.

### Inference

```text
infer hazard by B from obstacle
    content "route three is unsafe"
    confidence 0.87
```

### Simulation

```text
simulate imagined_failure by A
    content "the sensor fails"
    confidence 0.63
```

Simulation remains simulation. It cannot be written as a direct observation.

### Activation injection

```text
inject implanted_claim to A
    content "route three is safe"
    confidence 0.99
```

Injected packets are quarantined by default.

### Communication

```text
communicate obstacle from B to A as obstacle_at_A
```

The receiver gains access, while the source agent and source lineage remain B and `L_B`.

## 5. Workspace operations

```text
bind obstacle_at_A to A
quarantine obstacle_at_A by A
endorse obstacle_at_A by A threshold 0.80
authorize obstacle_at_A by A for planning
```

The finite runtime distinguishes:

- access
- workspace binding
- quarantine status
- epistemic endorsement
- scope-specific authorization

These are not interchangeable.

## 6. First-class proofs

Primitive proofs include:

```text
proof p_access access obstacle_at_A by A
proof p_origin origin obstacle_at_A source B lineage L_B
proof p_clear clear obstacle_at_A for A
proof p_endorse endorsement obstacle_at_A by A
proof p_auth authorization obstacle_at_A by A for planning
proof p_obs observation local_event by A
proof p_cap capability externalAct by A
```

Composite use proof:

```text
proof p_use use obstacle_at_A by A for planning
    from ["p_access","p_origin","p_clear","p_endorse","p_auth"]
```

Composite ownership proof:

```text
proof p_own ownership local_event by A as observed
    from ["p_access","p_origin","p_clear","p_obs"]
```

Proofs carry digests of their premises and the relevant packet state. A packet mutation can therefore make an earlier composite proof stale.

### Proof resource modes

Proof declarations may end in one of:

```text
mode persistent
mode affine
mode linear
```

- `persistent` proofs may be reused while semantically fresh.
- `affine` proofs may be consumed at most once.
- `linear` proofs must be consumed exactly once before successful program completion.

Example:

```text
proof p_use use evidence by A for planning
    from ["p_access","p_origin","p_clear","p_endorse","p_auth"]
    mode linear
```

A second use is rejected. An unused linear proof causes safe terminal rejection.

## 7. Proof-gated memory

```text
write_memory local_event by A as observed requires p_own
```

Communicated content must be written as communicated:

```text
write_memory obstacle_at_A by A as communicated
```

The following is rejected:

```text
write_memory obstacle_at_A by A as observed
```

because communication does not create A's direct-observation token.

## 8. Plans, effects, and capabilities

```text
grant A effect externalAct uses 2 until 100

plan alternate_route by A
    using obstacle_at_A
    effect externalAct
    expected 1.0
    requires p_use

execute alternate_route by A
feedback alternate_route by A observed 0.96
```

Capabilities may be:

- unbounded or use-bounded
- expiring by runtime step
- revoked
- represented by a capability proof

```text
revoke A effect externalAct
```

A planning proof does not itself grant an external-action capability.

## 9. Temporal contracts

Always-on templates:

```text
contract c1 always no_foreign_observed
contract c2 always no_simulated_observed
contract c3 always quarantine_blocks_endorsement
contract c4 always capability_confinement
```

Bounded feedback obligation:

```text
contract feedback_required
    after execute require feedback within 3
```

Contracts are monitored during execution and checked at program termination. `check_contracts` requests an explicit check before termination.

## 10. Transactions and rollback

```text
begin_transaction repair
observe candidate by A content "candidate" confidence 0.92
write_memory candidate by A as observed
commit_transaction repair
```

Manual rollback:

```text
begin_transaction trial
observe temporary by A content "temporary" confidence 0.9
rollback_transaction trial
```

If a runtime error occurs inside a transaction, the runtime automatically restores the checkpoint and emits a rollback receipt before surfacing the rejection. Nested transactions are rejected in OSL-Core 0.3.

## 11. Shared-workspace sessions

```text
session CooperativeDiagnosis
    participants ["A","B"]
    initial waiting_A

session_transition CooperativeDiagnosis waiting_A
    communicate A B -> waiting_B

session_transition CooperativeDiagnosis waiting_B
    communicate B A -> ready

start_session CooperativeDiagnosis
```

A communication can be session-labeled:

```text
communicate map from A to B as map_at_B in CooperativeDiagnosis
```

Version 0.3 can declare terminals and verify the finite protocol graph before starting it:

```text
session_terminal CooperativeDiagnosis ready
verify_session CooperativeDiagnosis
start_session CooperativeDiagnosis
```

The verifier checks deterministic transition keys, no reachable nonterminal deadlock, no terminal outgoing transition, and a terminal path from every reachable state. It does not prove asynchronous queue safety, fairness, recursive multiparty progress, or delivery by an external environment.

## 12. Neural proposal boundary

A neural decoder may propose content without automatically authorizing it:

```text
neural_propose candidate to A
    feature f441
    content "route blocked"
    confidence 0.82
```

The proposal begins provisional and quarantined, with unresolved obligations.

Trusted attestations:

```text
attest origin candidate by A lineage L_A as p_origin
attest relevance candidate by A for planning as p_relevance
```

Admission:

```text
admit candidate by A using ["p_origin","p_relevance"]
```

Rejection:

```text
reject_candidate candidate by A
```

This boundary separates latent decoding from semantic authorization. The current attestations are trusted runtime primitives; they are not learned causal proofs.

## 13. Secrets and public metadata

```text
secret private_goal value "alpha"
metadata fixed value 7 source trusted
metadata covert from_secret private_goal source agent
```

Secret values are not serialized into the state snapshot or public projection; only digests and names are retained. Agent-controlled metadata can still leak secret-dependent information.

Paired audit:

```bash
PYTHONPATH=reference python reference/audit_noninterference.py \
  examples/28_safe_metadata_left.osl \
  examples/29_safe_metadata_right.osl --json
```

The safe pair has identical public projections. The deliberately leaky pair differs. This is a paired-run audit, not universal noninterference.

A separate static checker covers the supported explicit dependency fragment:

```bash
PYTHONPATH=reference python reference/osl_information_flow.py PROGRAM.osl --json
```

It certifies absence of declared secret-to-public-metadata graph paths. Timing, control-flow, numerical-residue, operator-choice, semantic, and tool channels remain outside that theorem.

## 14. Static checker

```bash
PYTHONPATH=reference python reference/osl_check.py PROGRAM.osl
```

The static checker validates declared names and references for the finite grammar before runtime execution. It is not yet a full type inference engine or mechanized proof of type safety.

## 15. Append-only receipts and trace verification

Every dynamic statement emits a semantic boundary receipt containing:

- source line and statement kind
- source-text digest
- before-state semantic digest
- after-state semantic digest or rejection reason

The audit chain is append only and lies outside transaction checkpoints. Rollback restores semantic state without erasing evidence of the attempted transaction.

Runtime check:

```text
verify_receipts
```

Independent trace suite:

```bash
PYTHONPATH=reference python reference/verify_trace.py examples   --output TRACE_VERIFICATION.json
```

Independent receipt/proof kernel:

```bash
PYTHONPATH=reference python reference/osl_kernel.py examples   --output INDEPENDENT_KERNEL_REPORT.json
```

Unified finite certificate:

```bash
PYTHONPATH=reference python reference/verify_osl_core_v03.py   --output V03_UNIFIED_VERIFICATION.json
```

The unified certificate covers 66 source programs, 1,149 receipts, 70 proof terms, 2,330 exhaustive finite states, and 47,958 finite transition checks in the packaged release.

## 16. Determinism

Given identical source, interpreter, NumPy environment, and inputs, OSL-Core emits identical:

- ASTs
- static reports
- proof digests
- receipts
- snapshots
- public projections

The examples and tests verify replay equality in the release environment.

## 17. Safe rejection

Expected rejection is part of the language definition. Programs may reject because of:

- static unknown references
- incompatible provenance
- missing or stale proofs
- quarantine
- missing, expired, exhausted, or revoked capabilities
- contract violations
- invalid projector laws
- session-order violations
- incomplete neural admission
- transaction restrictions

No rejection is silently converted into authorization.
