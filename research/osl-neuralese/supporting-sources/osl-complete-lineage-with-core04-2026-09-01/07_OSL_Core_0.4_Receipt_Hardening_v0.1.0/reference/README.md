# OSL-Core 0.4 receipt-hardening reference

OSL-Core 0.4 preserves the finite Core 0.3 source grammar and the frozen
66-program outcome matrix, while replacing the receipt layer with
`osl.core.receipt.v2`. Every attempt now has an exact-source opening receipt,
audited parse/static outcome, globally indexed statement frames, and one final
terminal receipt that binds the semantic projection.

This is a research interpreter and verifier. It is not an OS sandbox, principal
authentication system, or mechanized proof of the Python implementation.

## Main modules

- `osl_model.py` — typed runtime state and canonical digests
- `osl_parser.py` — line-oriented parser and static checker
- `osl_core.py` — deterministic Core 0.4 interpreter
- `osl_kernel.py` — source-bound dictionary verifier with separately labeled
  same-runtime replay for delegated semantics
- `generate_core04_evidence.py` — 66-program reports and raw trace bundle
- `generate_core04_bridge_report.py` — three-program Discovery Bridge gate
- `generate_core04_adversarial_report.py` — fixed 24-witness attack gate
- `generate_test_report.py` — deterministic 93-test report
- `verify_core04_unified.py` — Core 0.4 conformance plus explicitly inherited
  finite-model evidence
- `build_core04_manifest.py` and `build_core04_archive.py` — deterministic
  integrity metadata and distributable archive
- `osl_formal_kernel.py` and `osl_metacore.py` — unchanged bounded Core 0.3
  abstract models, retained as complementary legacy evidence

## Run one program

PowerShell:

```powershell
$env:PYTHONPATH="reference"; python reference/osl_core.py examples/17_proof_planning.osl --json
```

Bash:

```bash
PYTHONPATH=reference python reference/osl_core.py examples/17_proof_planning.osl --json
```

## Verify and regenerate evidence

PowerShell:

```powershell
.\verify_core04.ps1
```

Bash:

```bash
./verify_core04.sh
```

## Native Core 0.4 gates

- 66/66 packaged sources conform
- 42 accepted and 24 safely rejected, unchanged from the frozen baseline
- 66/66 terminal traces pass the independent protected-state/lifecycle layer
- 66/66 traces match the separately labeled exact same-runtime replay
- 1,825 v2 receipts are archived in `CORE04_TRACE_BUNDLE.jsonl`
- 3/3 Discovery Bridge programs pass with 71 source-bound receipts
- 24/24 fixed adversarial witnesses are rejected or safely contained
- 93/93 tests pass with no skips or expected failures

The larger receipt count is intentional: parse/static failures, declarations,
default capabilities, numeric declarations/applications, assertions, exact
statement spans, and program terminals are now explicit evidence.

Read `CORE04_RECEIPT_SPEC.md`, `PROVENANCE_AND_PROOF_RULES.md`, and
`CLAIM_BOUNDARY.md` before making security or formal claims. Frozen Core 0.3
reports live under `legacy/v03_evidence/` and are not relabeled as Core 0.4.
