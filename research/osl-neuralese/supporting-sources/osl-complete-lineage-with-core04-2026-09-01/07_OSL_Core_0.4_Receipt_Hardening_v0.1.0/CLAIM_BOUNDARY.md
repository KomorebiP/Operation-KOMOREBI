# OSL-Core 0.4 Claim Boundary

## Strongest justified claim

If every required release gate passes, the justified statement is:

> For the packaged finite OSL corpus, the OSL-Core 0.4 reference runtime and independent dictionary-based verifier agree on the declared accepted and rejected outcomes, and the generated evidence satisfies the implemented v0.4 receipt, capability, proof, provenance, action-lifecycle, transaction, source-boundary, and final-state checks. Frozen OSL-Core 0.3 artifacts are separately identified and retain their original legacy assurance; this release does not claim a newly executed full legacy-profile certification.

This is a finite, executable conformance and adversarial-testing result. It is stronger than checking receipt hashes alone and weaker than a machine-checked proof of the interpreter or a universal security theorem.

## What a passing release may claim

A passing report may claim only the properties actually recorded by its generated evidence. Depending on the completed gates, those can include:

- the packaged corpus preserves its 42 accepted and 24 expected-rejection outcomes
- native traces have a versioned source/outcome envelope and exactly one terminal disposition
- legacy and native evidence are not conflated
- the tested execute receipts are bound to an available capability for the correct agent and effect, with the encoded use, expiry, and revocation rules applied
- the tested proof receipts satisfy the implemented constructor-specific and resource-usage rules
- the tested memory writes preserve the encoded provenance restrictions
- the tested plans, executions, and feedback events follow the implemented lifecycle rules
- the tested explicit and automatic rollbacks restore the declared transactional state while retaining an audit trail
- the tested statement boundaries and terminal receipts correspond to the packaged source and final semantic state
- the independent verifier rejects the packaged adversarial mutations for the properties named in the mutation report
- deterministic replay holds for the packaged programs in the declared software environment
- the finite abstract models reach the reported fixpoints and have no counterexample within their enumerated state spaces, if those models are rerun and included in this release

Counts must come from generated reports. A planned count is not an observed result. A skipped test, unavailable dependency, unexecuted GPU experiment, or missing artifact must be reported as such rather than counted as passing.

## What this release does not prove

### Interpreter correctness

The Python runtime is not verified in Lean, Coq, Agda, Isabelle, or another proof assistant. Agreement between two Python implementations reduces some shared-implementation risk but does not eliminate specification errors, shared assumptions, interpreter bugs, dependency bugs, or platform defects.

The term `independent kernel` means that receipt validation is implemented separately from the runtime's authorization helpers. It does not mean independent authorship, independent hardware, a formally verified computing base, or freedom from shared serialization and hashing code.

### Generality

The evidence does not prove correctness or safety for every syntactically valid OSL program. It covers the packaged programs, explicit adversarial mutations, and any precisely declared finite state models. It does not establish results for unbounded recursion, arbitrary extensions, unknown receipt schemas, dynamically loaded code, or features outside the encoded verifier.

### Real-world authority and effects

An OSL capability is a symbolic capability ledger. Unless an external host separately enforces it, it is not an operating-system sandbox, process boundary, network policy, hardware security mechanism, access-control system, or guarantee that a real tool call was authorized or performed correctly.

The verifier checks recorded identities and digests. It does not authenticate human or machine principals. SHA-256 provides tamper evidence for the serialized artifact under standard assumptions. It does not provide a signature, authorship, consent, nonrepudiation, or protection against a party that can generate an entirely new internally consistent trace.

### Semantic truth and neural evidence

Trusted origin and relevance attestations remain trusted boundary inputs. Receipt verification can check their structure, binding, lifecycle, and declared issuer. It cannot establish that a neural proposal is true, relevant, conscious, self-aware, intentional, or causally grounded in the world.

The Discovery Bridge can certify exhaustive claims only in its explicitly finite enumerated worlds. It does not establish open-world operator discovery, general intelligence, semantic understanding, or universal algebraic laws outside those worlds.

### Information flow

Passing provenance and explicit-flow checks does not prove universal noninterference. Unless separately modeled, the analysis excludes timing, resource-use, termination, latent-representation, probabilistic, cache, model-weight, prompt, filesystem, network, tool, and other covert or implicit channels.

Public projections show only what the declared projection exposes. They are not a proof that an embedding, external process, log, or host application reveals no additional information.

### Sessions and distributed liveness

Session verification covers the declared finite synchronous protocol graph. It does not prove liveness or fairness for asynchronous networks, lossy channels, recursive protocols, dynamic participants, Byzantine behavior, scheduler behavior, or unbounded multiparty systems.

Legacy order monitors without declared terminal states and explicit graph verification are not liveness certificates. They may receive `LEGACY_COMPATIBLE` status but not native graph-verification status.

### Transactions

Transaction claims apply only to state explicitly included in the checkpoint and tested rollback semantics. They do not imply database durability, atomicity across external tools, distributed commit, crash consistency, secure erasure, or rollback of effects that occurred outside the runtime.

Audit retention can intentionally preserve digests or metadata about rolled-back activity. It must not be described as erasing the historical fact that an attempted transaction occurred.

### Numerical and empirical extensions

Finite floating-point examples do not establish exact real-number algebra beyond their stated tolerance. Geometry, representation-probe, Hugging Face, and micro-emergence experiments are separate empirical packages. Their version numbers and results do not supersede the canonical language version, and their findings are not evidence for receipt-kernel security unless an explicit integration test says so.

## Legacy evidence boundary

The original OSL v0.5 / OSL-Core 0.3 reports remain evidence for the checks they declared. Hardening the verifier does not make those reports fraudulent, but it reveals properties they did not test.

A legacy sidecar envelope can bind an old source, replay, outcome, and receipt chain. It cannot add an event that the old trace never recorded or establish a semantic invariant that cannot be reconstructed from old evidence. In particular, a zero-receipt static rejection requires source-bound outcome evidence, and a completion-time rejection requires an explicit completion-phase disposition in the envelope.

No legacy artifact should be described as `V04_NATIVE_VERIFIED`. Native status requires native execution and the complete native evidence schema.

## Reporting discipline

Every release-level conclusion should identify:

1. the runtime and verifier versions
2. the evidence profile, `v0.4-native` or `v0.3-legacy`
3. the exact corpus or finite model checked
4. passed, failed, skipped, and not-run counts
5. the relevant report and manifest digests
6. trusted assumptions and unsupported features

Use `verified` only with a named finite verifier and scope. Use `exhaustive` only when the entire declared finite state space was enumerated. Use `secure`, `safe`, `authenticated`, `causal`, `emergent`, or `formally proved` only when a separate result actually establishes that stronger property.

If a report is stale, partially regenerated, missing a dependency, or inconsistent with the manifest, the release status is not passing. The correct result is a visible failure or `NOT_RUN`, not an inferred success.
