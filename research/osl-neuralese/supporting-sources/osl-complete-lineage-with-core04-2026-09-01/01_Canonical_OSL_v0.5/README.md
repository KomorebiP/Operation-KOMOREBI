# Operator-Symbolic Languages for Artificial Intelligence

## Finite Metatheory and Independent-Kernel Draft v0.5

This release consolidates the executable language as **OSL-Core 0.3**. It extends the v0.2 mechanized control layer with resource-sensitive proof terms, an append-only audit ledger, source-statement semantic boundaries, deterministic replay certificates, finite session-graph verification, static explicit information-flow analysis, an independent receipt/proof kernel, and two exhaustive finite transition-model layers.

The release contains a mathematical manuscript and a deterministic finite reference implementation. It is an executable research specification, not a hardened production language or a general proof assistant.

## Principal artifacts

- `operator_symbolic_ai_language_v0.5.pdf` - compiled manuscript
- `main.tex` and `sections/` - complete LaTeX source
- `reference/osl_core.ebnf` - OSL-Core 0.3 grammar
- `reference/osl_parser.py` - AST parser and static checker
- `reference/osl_model.py` - typed runtime data model
- `reference/osl_core.py` - deterministic interpreter
- `reference/osl_kernel.py` - independent receipt/proof verifier
- `reference/osl_formal_kernel.py` - integrated finite abstract kernel
- `reference/osl_metacore.py` - five decomposed exhaustive models
- `reference/verify_trace.py` - deterministic source-to-receipt verification
- `reference/verify_osl_core_v03.py` - unified finite verification
- `examples/` - 66 accepted and expected-rejection programs
- `tests/` - 61 focused tests
- `V03_UNIFIED_VERIFICATION.json` - combined certificate
- `LANGUAGE_REFERENCE.md` - implementation-oriented language guide
- `MECHANIZED_CORE_NOTES.md` - theorem and trust-boundary notes

## What OSL-Core 0.3 adds

1. Persistent, affine, and linear proof resources
2. Exactly-once completion checks for linear proofs
3. Append-only audit receipts that survive transaction rollback
4. Per-statement source, before-state, and after-state semantic receipts
5. Deterministic source-to-trace replay verification
6. A separate kernel for packet, proof, provenance, action, session, and transaction receipts
7. Graph verification of finite session terminals and deadlocks
8. Static explicit secret-to-metadata dependency analysis
9. An integrated complete finite abstract kernel
10. Five independent decomposed finite transition models
11. Adversarial raw-tamper and fully rehashed semantic-forgery tests
12. A unified machine-readable verification certificate

## Quick verification

Linux or macOS:

```bash
./VERIFY_RELEASE.sh
```

Windows PowerShell:

```powershell
.\VERIFY_RELEASE.ps1
```

The default verifier checks the immutable manifest, reruns all 61 focused tests, validates Python syntax, and rebuilds the 88-page PDF. To regenerate the full finite certificate stack as well, run:

```bash
FULL_REPLAY=1 ./VERIFY_RELEASE.sh
```

or on Windows:

```powershell
.\VERIFY_RELEASE.ps1 -FullReplay
```

Run the language and finite certificates directly:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference \
  python reference/verify_osl_core_v03.py \
  --output V03_UNIFIED_VERIFICATION.json
```

## Verified status

- **66 of 66** source programs match their declared acceptance or rejection
- **42** accepted programs
- **24** expected safe rejections
- **2 of 2** paired public-projection audits match expectation
- **61** focused tests pass
- **66** deterministic source-to-trace certificates pass
- **66** programs pass the independent receipt kernel
- **1,149** receipts and **70** proof terms are independently checked
- **740** reachable states and **19,240** transitions are exhaustively checked in the integrated abstract kernel
- **1,590** reachable states and **28,718** transition attempts are exhaustively checked in the decomposed metacore
- **2,330** total abstract states and **47,958** total finite transition checks

## Claim boundary

OSL-Core 0.3 establishes a finite executable and computer-assisted research core for typed numerical operators, provenance-aware packets, proof-gated memory and planning, resource-sensitive proofs, bounded authority, temporal monitors, rollback, session protocols, neural-boundary quarantine, receipt reconstruction, and declared information-flow checks.

It does **not** establish:

- proof-assistant correctness of the complete Python interpreter
- cryptographic authentication or a production sandbox
- universal information-flow noninterference
- asynchronous recursive session liveness
- nonlinear or tensor execution in the finite runtime
- adversarially grounded neural attestations
- autonomous open-world symbol discovery
- causal identification of this language inside contemporary neural models

The finite certificates cover their declared models and packaged executions. They should not be read as universal security or awareness claims.


See [`OSL_CORE_0_3_BLOCK_SUMMARY.md`](OSL_CORE_0_3_BLOCK_SUMMARY.md) for the consolidated result, certificate stack, and exact claim boundary.

