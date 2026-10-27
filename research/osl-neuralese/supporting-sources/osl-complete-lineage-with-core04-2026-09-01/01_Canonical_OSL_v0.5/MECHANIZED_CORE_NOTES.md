# OSL-Core 0.3 Finite Metatheory Notes

## Status

OSL-Core 0.3 has four mechanized evidence layers beyond ordinary example testing:

1. deterministic source-to-receipt trace certificates
2. an independent receipt/proof kernel
3. a complete reachable-state exploration of an integrated finite abstract kernel
4. five complete decomposed finite transition models

"Mechanized" means executable formal objects, exhaustive finite exploration, independent trace reconstruction, and reproducible certificates. It does not mean that the complete interpreter has been verified in Lean, Coq, Agda, or Isabelle.

## Finite theorem analogues

### Resource-sensitive proof use

Persistent proofs may be reused. Affine proofs may be consumed at most once. Linear proofs must be consumed exactly once before successful program completion.

### Append-only rollback visibility

Transaction rollback restores checkpointed semantic state but cannot erase the external audit history. The audit chain records transaction start, attempted operations, rollback, and terminal rejection.

### Provenance non-forging

The direct-observation constructor is `observe`. Communication, inference, simulation, injection, and neural proposals do not create a receiver-owned observation token. The independent kernel rejects an observed-memory forgery even after all affected records and receipt hashes are consistently recomputed.

### Proof freshness

Composite proofs bind premise digests, packet state, agent, scope, memory class, and creation step. Mutation of proof-relevant state invalidates the proof.

### Capability confinement

Execution requires a matching live capability. Remaining uses, expiry, and revocation are checked independently of epistemic proof.

### Temporal contracts

Feedback deadlines create obligations at execution and discharge them only when matching feedback arrives before the deadline.

### Transaction atomicity

A successful commit exposes the new state. Manual or automatic rollback restores the checkpoint. The global audit chain remains append only.

### Session fidelity

Runtime session-labelled communications must match the current protocol transition. The graph verifier additionally proves, for the declared finite graph, deterministic keys, no reachable nonterminal deadlock, no terminal outgoing transition, and terminal reachability from every reachable state.

### Explicit information flow

The static checker proves absence of declared secret-to-public-metadata paths in the supported syntactic fragment. This excludes implicit timing, control-flow, numerical, operator-choice, and tool channels.

### Deterministic trace correspondence

Each executed source statement is linked to a statement-boundary receipt containing the source digest and before/after semantic digests. Two complete replays must agree exactly.

## Exhaustive finite results

### Integrated abstract kernel

- 26 abstract commands
- 740 reachable states
- 19,240 transitions
- 6,464 accepted transitions
- 12,776 explicit safe rejections
- zero counterexamples to the declared property set

### Decomposed metacore

- provenance and ownership: 1,301 states, 26,020 attempts
- bounded capability: 256 states, 2,560 attempts
- feedback deadline: 24 states, 96 attempts
- transaction atomicity: 6 states, 36 attempts
- session fidelity: 3 states, 6 attempts
- total: 1,590 states and 28,718 attempts

### Source and receipt layer

- 66 programs match their specification
- 66 trace certificates pass
- 66 independent receipt-kernel checks pass
- 1,149 receipts and 70 proofs are reconstructed
- 61 focused tests pass

## What still requires proof-assistant mechanization

1. Preservation for the concrete syntax and state model
2. Progress with a typed explicit-rejection outcome
3. Linear proof-resource preservation under every reduction rule
4. Receipt-kernel correspondence to a formal trace semantics
5. Formal transaction rollback equivalence
6. Recursive session fidelity and progress
7. Typed-fragment information-flow noninterference
8. Trust composition for proof translation and neural attestations

## Strongest current claim

The release demonstrates that the central operator-symbolic distinctions are executable, independently auditable at the receipt level, and invariant across two complete finite abstract-model explorations. It does not prove the implementation correct outside those finite models or establish that contemporary neural models internally use OSL.
