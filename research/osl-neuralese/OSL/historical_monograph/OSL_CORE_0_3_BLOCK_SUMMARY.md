# OSL-Core 0.3 Finite Metatheory and Independent Audit Kernel

## Status

- Manuscript release: **Finite Metatheory and Independent-Kernel Draft v0.5**
- Language release: **OSL-Core 0.3**
- Scientific status: `FINITE_COMPUTER_ASSISTED_METATHEORY_PASSED`
- Unified verification: all declared checks passed

OSL-Core 0.3 advances the language from example-driven runtime validation to a three-layer finite evidence system:

1. **Source conformance** - every packaged source program is parsed, statically checked, executed deterministically, and compared against its declared accepted or rejected result.
2. **Independent trace reconstruction** - a separate audit kernel consumes receipts rather than trusting the interpreter's final state and reconstructs packets, proofs, capabilities, memories, sessions, actions, and transaction boundaries.
3. **Exhaustive finite abstraction** - independently implemented abstract transition systems enumerate every reachable state under bounded command alphabets and check declared invariants on every accepted and rejected transition.

These layers are complementary. Source conformance connects the surface language to behavior. Independent replay reduces trust in the interpreter's own report. Exhaustive abstraction checks all behaviors of the declared finite models rather than only sampled source programs.

## Principal results

| Evidence layer | Result |
|---|---:|
| Packaged source programs | 66 |
| Accepted programs | 42 |
| Expected safe rejections | 24 |
| Programs matching specification | 66 of 66 |
| Focused automated tests | 61 passed |
| Independently replayed programs | 66 |
| Independently verified receipts | 1,149 |
| Independently verified proof objects | 70 |
| Compact abstract-kernel states | 740 |
| Compact abstract-kernel transitions | 19,240 |
| Decomposed metacore states | 1,590 |
| Decomposed metacore transition attempts | 28,718 |
| Total finite states explored | 2,330 |
| Total finite transition checks | 47,958 |
| Paired information-flow audits | 2 of 2 passed |
| Manuscript pages | 88 |

## New language mechanisms

### Resource-sensitive proofs

Each proof is now declared as:

- `persistent` - reusable
- `affine` - usable at most once
- `linear` - must be used exactly once on normal completion

The runtime records proof consumption in the audit chain. Reuse of affine or linear proofs is rejected. A normally completing program with an unused linear proof is also rejected.

### Append-only source-bound audit chain

Every runtime statement produces a linked semantic boundary record containing:

- source location
- statement kind
- pre-state semantic digest
- post-state semantic digest
- acceptance or explicit rejection status
- previous receipt digest
- current receipt digest

Transaction rollback restores application state without deleting the audit history. A failed statement ends in an explicit rejection receipt rather than an ambiguous partial trace.

### Independent receipt and proof replay

The independent kernel verifies:

- receipt-chain linkage
- source-statement boundaries
- semantic before/after digests
- proof construction and consumption
- capability use and revocation
- autobiographical writes
- action execution and feedback
- session transitions
- transaction rollback boundaries

It does not trust the interpreter's final snapshot. It reconstructs a second semantic state from the receipt stream.

A rehashed record can therefore pass byte-integrity checks and still fail semantic replay when it is attached to the wrong proof, packet, capability, or source transition.

### Complete finite state exploration

The compact integrated kernel exhaustively checks a bounded model containing provenance, quarantine, binding, endorsement, authorization, proof construction, capabilities, planning, action, feedback, and temporal obligations.

The declared checked properties include:

- preservation
- progress with explicit rejection
- provenance non-forging
- source preservation
- quarantine confinement
- proof freshness
- ownership gating
- effect confinement
- linear capability consumption
- feedback causality
- contract-obligation soundness
- safe rejection

A second decomposed metacore independently verifies five smaller state machines and provides complementary finite coverage.

### Verified finite session graphs

Session declarations can identify terminal states and request graph verification. The verifier checks declared bounded properties such as:

- transition closure over known states
- terminal-state finality
- reachability of declared terminal states
- absence of declared finite dead ends where prohibited
- runtime conformance to the verified transition graph

This is finite graph verification, not a general asynchronous multiparty liveness theorem.

### Stronger information-flow evidence

The release contains both:

- paired dynamic public-projection audits
- static explicit-flow analysis over the finite source language

The safe metadata pair remains publicly identical when its private secret changes. The deliberately leaky pair exposes the expected secret-dependent fields. The analysis does not establish universal noninterference against implicit flow, timing, floating-point residues, semantic operator choices, or arbitrary external effects.

## Certificate stack

The canonical certificate index binds:

- `EXAMPLE_RESULTS.json`
- `TRACE_VERIFICATION.json`
- `INDEPENDENT_KERNEL_REPORT.json`
- `COMPACT_CLOSURE_CERTIFICATE.json`
- `FINITE_METACORE_CERTIFICATE.json`
- `SESSION_VERIFICATION_REPORT.json`
- `INFORMATION_FLOW_REPORT.json`

`V03_UNIFIED_VERIFICATION.json` verifies the conjunction of the principal finite evidence layers and records one top-level verification digest.

## Strongest justified claim

> OSL-Core 0.3 has a deterministic finite reference semantics with source-level conformance evidence, an independently implemented receipt/proof replay kernel, and exhaustive computer-assisted certificates for explicitly bounded abstract models.

This is stronger than a collection of handpicked examples. It supports bounded claims about the packaged finite language and declared abstractions.

## Exact claim boundary

The release does **not** provide:

- a Lean, Coq, Agda, or Isabelle proof of the complete implementation
- a proof for arbitrary or unbounded OSL programs
- a hardened sandbox for real external effects
- authentication of principals or trusted hardware
- universal noninterference or covert-channel absence
- asynchronous distributed deadlock freedom
- semantic truth guarantees for neural attestations
- nonlinear or tensor execution in the finite interpreter
- proof that the Python verifier itself is bug-free

The Python runtime and certificate generators remain part of the trusted computing base. The exhaustive certificates are exact for their declared finite models only.

## Reproduction

From the extracted release directory:

```bash
PYTHON=python ./VERIFY_RELEASE.sh
```

On Windows:

```powershell
.\VERIFY_RELEASE.ps1
```

The verification path regenerates evidence, runs the focused test suite, checks Python syntax, rebuilds and preflights the PDF, regenerates release metadata, and verifies the immutable manifest.
