# Komorebi H12 — Signed Unit Transport, Lean v0.2.0

Start with **PROOF.md**. **FORMALIZATION_SCOPE.md** separates compiled algebra from ordinary analytic arguments and the still missing arithmetic comparison.

This package contains 83 compiled Lean theorem constants, 33 new, together with exact and numerical reproducibility checks. It does not claim U_Gamma=U_alg, any power equality with U_alg, or a general Hilbert-12 theorem.

## Reproduce

Use Python with the pinned versions in requirements.txt and the user's external portable Lean kit. The compiler/runtime is not included in this source package.

```bash
python -m pip install -r requirements.txt
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/numerical_checks.py --digits 40
python checks/numerical_checks.py --digits 70
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 1
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 2
```

Validate shipped hashes **before rerunning**. The scripts overwrite their own evidence outputs and timings, so a rerun does not preserve shipped output hashes. The two Lean stages are synchronous. Stage 1 starts a clean build; stage 2 verifies source and inherited compiled-object hashes before continuing and auditing all theorem constants. The compiler uses one worker and warnings as errors. Each subprocess has an explicit timeout and process-group cleanup.

The source files are ordinary Lean modules under formalization/. Any local .lean-check directory or compiler object cache is disposable and excluded from the ZIP.

## Check domains

Exact checker: integer/rational arithmetic and formal polynomial identities. Its arbitrary-iterate interpretation is proved separately in Lean.

Numerical checker: 40/70 requested decimal digits plus 25 guards; direct theta products and the inherited guarded gamma series. Floating-point rounding is not interval-certified. The asymptotic coefficient check has its own declared 1e-6 tolerance, separate from equality tolerances. No arithmetic candidate is fitted or compared.

## Provenance

See MANIFEST.json, evidence/lean_results.json, evidence/runtime_restore.json, evidence/FAILURES.md, and evidence/replay_receipt.json. The manifest uses the documented legacy v1 schema and a visibly adapted validator; it authenticates file hashes and stated run metadata, not mathematical truth. No Git revision is available for this isolated generated release.
