# Komorebi moving exact spaces — v0.32.0

**Komorebi P.** Focused continuation of the robustness and quantitative-descent branches.

## Results

The actual orthogonal exact-space projectors obey a two-sided bound
`||q-q'|| <= max(C,C') * epsilon`, without assuming equality or inclusion of
kernels. This gives a Lipschitz map on uniformly certified model classes.

For a split-surjective reference defect and `a*epsilon < 1`, a Neumann inverse
constructs the perturbed right inverse, residual certificate, and a continuous
linear equivalence between the moving exact spaces. A separate interface derives
the old splitting from Hilbert geometry and surjectivity.

The theorem compares the existing v0.30 two-stage descent repairs. An all-real
Euclidean example computes the exact projector-motion norm and distinguishes
orthogonal repair from splitting-dependent transport between kernels.

See `docs/MOVING_EXACT_SPACES.md` and `docs/THEOREM_INDEX.md`.

## Contents and scope

11 production modules and the root. Six inherited modules are hash-identical to
the recorded v0.26/v0.30 sources. Five additions contain 61 named theorems and 28
constructions; the full source closure contains 151 and 47. These include helper
lemmas, not claimed discoveries. This is not the full historical repository.

## Reproduce

Use the external pinned portable runtime: Lean 4.34.0-rc2, mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```bash
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --build-name local_check --audit-dir audit/local_check --timeout 180
python3 scripts/run_exact_audit.py --output-dir audit/local_computation
```

Each verification needs a new build-name and compiles the entire supplied source
closure. It runs all explicit declaration axiom requests and six negative
controls. The custom-axiom control intentionally compiles, then its printed
unapproved axiom must be detected. The other five controls must fail.

`lakefile.toml` pins the same dependencies for conventional Lake installation.
The archive does not contain the compiler or the multi-gigabyte dependency cache.

## Scientific boundary

Norm closeness alone does not preserve exact spaces. The general comparison needs
both residual-gain certificates; the one-certificate theorem requires a
surjective/split reference and the strict radius. No nonlinear, changed-norm,
arbitrary-stack-metric, optimal general constant, or unverified-noise-radius
claim is made. The finite Python checker is supplementary and is not itself
proved correct in Lean. See the external delivery receipt for completed checks.
