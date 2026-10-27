# Komorebi Representation Calculus v0.4

Torsion-safe optimality for certificate-derived representations over Z/(p^r).
This is the representation-calculus branch, not p-adic Block 16.

## Read first

- `FORMAL_NOTE.md`: exact contract, proof and nonlinear-encoding boundary.
- `FORMALIZATION_COVERAGE.md`: universal and instance-level proof scope.
- `RESULTS.md`: retained completed execution results, not intended targets.
- `DEVELOPMENT_FAILURES.md`: failed drafts, interrupted runs and their replacements.
- `EXTERNAL_INPUTS.md`: pinned upstream and reused project proofs.

A certified encoding with t nonzero principal-ideal factors needs exactly t
residue coordinates when the initial encoding is linear and every initial state
and future word must be handled. The lower bound even permits nonlinear target
operations/observations. A checked example shows that permitting a nonlinear
initial encoding changes the answer. This is not an arbitrary-program memory bound.

## Source layout

`formalization/MatrixLinearBridge.lean`, `FinRingCompatibility.lean`, and
`MatrixPrimeMinimality.lean` prove the generic adapter. `MinimumBatch*.lean`
instantiates it on all 202 frozen matrix certificates. `CertifiedMinima.lean`
imports the batches. `TorsionEncodingBoundary.lean` proves the exact hypothesis
boundary. `LargeLinearMinimum.lean` reuses the general bound for the previous large
example. `examples/FreshMinimum.lean` is a fresh end-to-end exporter example.

The original v0.3 ZIP is preserved under `history/`. Its 213 Lean files have only
module/public-import header changes in the current tree; mathematical bodies and
literal data are unchanged. Three generator-bound modules from p-adic Block 15
are copied unchanged under `formalization/KomorebiPadic/` and rebuilt here. This
is not a new verification of the entire p-adic project.

## Reproduction

Check the distribution before any audit, because rerunning an audit intentionally
replaces current execution records:

```sh
python tools/verify_integrity.py
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/run_python.py
```

The Python code uses the standard library. It rediscovers and checks the frozen
certificates, verifies emitted source contents, and exhausts the small torsion
boundary example. Python/exporter/checker correctness is not proved in Lean.

For Lean, use the saved portable runtime or an equivalent installation with:

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`;
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` and its dependencies.

The audit expects `<runtime>/toolchain/bin/lean` and the matching dependencies
under `<runtime>/workspace/.lake/packages/`. Runtime/cache bytes are not bundled.
Run from this directory, with a new empty build directory outside the release:

```sh
python tools/audit_lean.py --runtime /path/to/portable-runtime --build /tmp/repr04-cold --batch 25 --timeout 120
python tools/audit_lean.py --runtime /path/to/portable-runtime --build /tmp/repr04-cold --batch 25 --timeout 120 --resume
```

Repeat the resume command until the result says PASS. An IN_PROGRESS record or a
timeout is not verification. Resumption refuses changed accepted source hashes.
Use `--batch 1000` for one enclosing invocation. The runner cold-builds local
modules and reuses the pinned upstream compiled cache; it does not rebuild Mathlib.

The inherited v0.3 scripts `verify_lean.py`, `replay_selected_lean.py`, and
`normalize_lean_manifest.py` are historical tools, NOT the v0.4 audit entry point.

## Export a newly discovered certificate

```sh
python tools/export_minimum_lean.py source.json certificate.json --namespace MyCase --output MyCase.lean
```

The exporter runs the unchanged independent checker and writes untrusted Lean
source. Compile that source against the current compiled modules to accept its
all-state/all-word optimum. A successful export message is not a successful proof.

## Trust boundaries

The formal theorem concerns literal matrices under a declared all-state contract.
The JSON parser, proposer/discoverer, Smith engine and exporter are not verified
executables. No trained search policy, independently held-out scientific discovery,
comparative speedup, independent referee review or historical-novelty claim is made.
