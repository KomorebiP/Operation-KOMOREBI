# OSL-Core 0.3 Reference Implementation

The reference directory implements the finite executable subset described in the v0.5 manuscript. Version 0.3 retains the v0.2 AST, provenance, proof, effect, contract, transaction, session, and neural-boundary layers and adds resource-sensitive proofs, append-only receipts, semantic statement boundaries, finite protocol verification, static explicit-flow analysis, independent receipt reconstruction, and exhaustive finite metatheory certificates.

## Principal modules

- `osl_model.py` - typed data structures, canonical digests, proof resources, and runtime state
- `osl_parser.py` - line-oriented AST parser and pre-execution static checker
- `osl_core.py` - deterministic interpreter and semantic validators
- `osl_check.py` - static-check CLI
- `osl_invariants.py` - runtime and append-only-ledger invariant checker
- `verify_trace.py` - deterministic replay and source-to-receipt correspondence
- `osl_kernel.py` - independent receipt/proof/trace verifier
- `osl_formal_kernel.py` - complete integrated finite abstract-state explorer
- `osl_metacore.py` - five decomposed exhaustive finite models
- `verify_osl_core_v03.py` - unified certificate generator
- `osl_session_verify.py` - finite protocol-graph verifier
- `osl_information_flow.py` - static explicit secret-to-metadata dependency analysis
- `audit_noninterference.py` - paired-run public-projection audit
- `run_examples.py` - source conformance and paired-audit driver
- `osl_core.ebnf` - complete finite grammar

## Run one program

```bash
PYTHONPATH=reference python reference/osl_check.py examples/17_proof_planning.osl
PYTHONPATH=reference python reference/osl_core.py examples/17_proof_planning.osl --json
```

## Run the finite verification stack

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference   python reference/verify_osl_core_v03.py   --output V03_UNIFIED_VERIFICATION.json
```

## Conformance and tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference   python reference/run_examples.py examples --json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference   python -m pytest -q -p no:cacheprovider tests
```

The current suite contains 42 accepted programs and 24 expected safe rejections. Correct rejection is part of the specification.

## Implemented in 0.3

- explicit AST and static reference validation
- finite vectors, matrices, projectors, transport, and intertwiners
- agents and lineage declarations
- typed packet provenance
- access, binding, quarantine, endorsement, and authorization
- primitive and composite proofs with persistent, affine, and linear modes
- proof freshness, resource consumption, and completion checks
- proof-gated planning and autobiographical writes
- bounded, expiring, and revocable effects
- temporal contracts and feedback deadlines
- transaction checkpoint, commit, manual rollback, and automatic rollback
- append-only audit history that survives rollback
- semantic statement-boundary receipts and deterministic trace replay
- finite-state session order plus graph-level terminal/deadlock checks
- neural proposal quarantine, attestation, admission, and rejection
- secret digests, trusted/agent metadata, public projection, and static explicit-flow analysis
- paired-trace noninterference audit
- independent receipt/proof reconstruction
- two exhaustive finite transition-model layers

## Verified finite counts

- 66 source programs match their specification
- 2 paired public-projection audits match their expected result
- 61 focused tests pass
- 66 deterministic source-to-trace certificates pass
- 66 programs and 1,149 receipts pass the independent receipt kernel
- 740 states and 19,240 transitions are checked in the integrated abstract kernel
- 1,590 states and 28,718 transition attempts are checked in the decomposed metacore

## Claim boundary

The implementation is a deterministic research reference, not a hardened runtime. The finite certificates do not constitute a Lean, Coq, Agda, or Isabelle proof of the complete Python interpreter. They do not authenticate principals, establish universal information-flow security, prove liveness for unbounded asynchronous protocols, validate untrusted neural attestations, or cover nonlinear/tensor execution backends.
