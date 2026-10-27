# OSL-Core 0.5 semantic-independence reference

OSL-Core 0.5 preserves the packaged 66-program Core 0.4 outcome matrix while
adding separately implemented finite semantic verifiers for numerical
operators, contracts, sessions, metadata-facing state, and audit intrinsics.
The runtime continues to emit `osl.core.receipt.v2`, now with
`core_version = 0.5` in every native receipt.

This is a research interpreter and executable verifier. It is not an
operating-system sandbox, a principal-authentication system, or a mechanized
proof of the Python implementation.

## Main runtime and verification modules

- `osl_model.py` — typed runtime state and canonical digests;
- `osl_parser.py` — line-oriented primary parser and static checker;
- `osl_core.py` — deterministic Core 0.5 reference interpreter;
- `osl_kernel.py` — receipt-hardened source/lifecycle and protected-state
  verifier, with same-runtime replay reported separately;
- `osl_semantic_numeric.py` — bounded independent numerical/operator parser
  and semantic reconstructor;
- `osl_semantic_contracts.py` — bounded independent temporal-contract parser
  and semantic reconstructor;
- `osl_semantic_sessions.py` — bounded independent finite-session parser and
  semantic reconstructor;
- `osl_semantic_meta.py` — metadata, secret commitment, assertion-accounting,
  and `show` verifier using the primary parser but not `OSLRuntime`;
- `osl_semantic_intrinsics.py` — independent recomputation of embedded
  `verify_receipts` prefix reports, using the primary parser but not
  `OSLRuntime`;
- `osl_semantic_kernel.py` — fail-closed aggregate for the five Core 0.5
  semantic components.

The numeric, contract, and session components parse their declared finite
source fragments independently from the primary parser. All five semantic
components avoid importing or invoking `OSLRuntime`. The base, metadata, and
intrinsic paths still share primary frontend components, so this release does
not claim a wholly independent second frontend or interpreter.

## Evidence and packaging modules

- `generate_core05_evidence.py` — 66-program conformance, semantic aggregate,
  and raw trace-bundle generation;
- `generate_core05_bridge_report.py` — three-program Discovery Bridge gate;
- `generate_core05_focused_report.py` — fixed 75-case Core 0.5 focused gate;
- `generate_test_report.py` — deterministic 168-test full-suite report;
- `verify_core05_package.py` — offline package-integrity and evidence checks;
- `build_core05_manifest.py` and `build_core05_archive.py` — deterministic
  integrity metadata and distributable archive;
- `osl_formal_kernel.py` and `osl_metacore.py` — bounded Core 0.3 abstract
  models retained as complementary legacy evidence, not upgraded proofs.

## Run one program

PowerShell:

```powershell
$env:PYTHONPATH="reference"; python reference/osl_core.py examples/17_proof_planning.osl --json
```

Bash:

```bash
PYTHONPATH=reference python reference/osl_core.py examples/17_proof_planning.osl --json
```

## Verify and regenerate finite evidence

PowerShell:

```powershell
.\verify_core05.ps1
```

Bash:

```bash
./verify_core05.sh
```

After dependencies are installed, the verification workflow is offline. It
checks package integrity, regenerates the declared reports, runs the full and
focused tests, and rechecks the package.

## Observed Core 0.5 gates

| Gate | Result |
|---|---:|
| Full test suite | 168/168 |
| Focused Core 0.5 gate | 75/75 |
| Packaged corpus | 66/66 |
| Accepted / expected rejection | 42 / 24 |
| Native Core 0.5 receipts | 1,825 |
| Semantic aggregate | 66/66 |
| Discovery Bridge | 3/3 programs, 71 receipts |

Generated release evidence is stored in `CORE05_TRACE_BUNDLE.jsonl`,
`CORE05_CONFORMANCE_REPORT.json`, `CORE05_SEMANTIC_REPORT.json`,
`CORE05_FOCUSED_REPORT.json`, and `CORE05_DISCOVERY_BRIDGE_REPORT.json`.
Same-runtime replay is retained as a compatibility and determinism signal but
is not counted as independent semantic evidence.

## Boundary of the result

Core 0.5 does not independently establish the general truth of every
assertion form, exact complete cross-domain transaction projection digests,
out-of-domain rejection causality, or diagnostic `event_count`. Python and
NumPy remain in the trusted computing base, and the evidence covers finite
packaged programs and tests rather than every valid OSL source. SHA-256 binds
bytes but authenticates no identity; symbolic capabilities do not create an
OS sandbox; and neural origin/relevance attestations remain trust roots.

Read `CORE05_SEMANTIC_INDEPENDENCE_SPEC.md`, `CORE05_NUMERIC_PROFILE.md`,
`PROVENANCE_AND_PROOF_RULES.md`, and `CLAIM_BOUNDARY.md` before making release
or security claims. The frozen Core 0.3 evidence and the separate Core 0.4
release retain only their original assurance and are not relabeled as Core
0.5.
