# Komorebi Model-Theory Normalization v0.1

A first normalized, Lean-checked observational-logic bridge from Representation
Calculus v0.4. This does not supersede that calculus or the p-adic checkpoints.

Read `NORMALIZED_CORE.md`, then `FORMALIZATION_COVERAGE.md` and `RESULTS.md`.
The core contribution is precise scope: path normalization, observational type
agreement, quantified preservation under surjective transports, finite definable
codes when certified, and counterexamples to unqualified stronger claims.

## Reproduce

Requires Python 3.10+ and Lean `leanprover/lean4:v4.34.0-rc2` with its standard
library. No Mathlib package, external Python dependency, or network call is
required to run the included audit once the compiler is available.

```sh
python tools/verify_integrity.py
python tools/audit_all.py --lean /absolute/path/to/lean
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

On Windows, pass the path to lean.exe. The historical Linux runtime is not bundled.
The audit creates a fresh temporary build directory and has a 45-second cap per
subprocess. A complete audit can take longer than that total. Slow machines may
need an explicitly adjusted cap; a timeout is never a proof success.

For the finite reference experiment alone:

```sh
python tests/audit.py
```

`observational_logic.py` contains documented immutable finite systems and tuple
syntax, a path normalizer, a first-order-fragment evaluator, a quotient reference,
and a local finite-code checker. It is tested, not a Lean-extracted executable.

Distribution integrity should be checked before running audits because audits
intentionally replace execution logs and results. Preserve the original ZIP.

The complete v0.4 predecessor archive is retained under `history/`. Only its
RepresentationCore and FiniteCertificates modules were rebuilt here. No full
historical v0.4 or p-adic replay is claimed.
