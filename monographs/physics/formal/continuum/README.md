# Komorebi Physics: centered continuum verification

Formal checkpoint **0.51.0**, PHYS-CENT-51.

This source package completes the centered approximation block for the free
Dirac field on a fixed flat torus. Its centered operators act on the same
infinite Fourier coefficient space as the self-adjoint continuum Hamiltonian.
The checked results cover the full maximal first-order domain, every nonreal
spectral parameter, and quadratic generator and propagator bounds under an
explicit third-order Fourier moment assumption.

The four new modules contain **74 named theorems, 15 definitions and 11
abbreviations**. The fresh gate audited **162 compiled environment
declarations** from those modules, including generated helpers. The unchanged
strong-generator module contributes **37 named theorems and 2 definitions**,
with **47 compiled environment declarations** rechecked in
the same gate. These are scoped counts, not a total for the physics program.

## Main results

- Bounded, self-adjoint centered operators for every nonzero real spacing.
- Graph-domain convergence for every vector in the maximal continuum domain.
- Two-sided strong-resolvent convergence for every nonreal complex parameter
  and every square-summable field, with actual inverse and domain laws.
- Generator error at most `h² M₃(f) / 6` and propagator error at most
  `|t| h² M₃(f) / 6`, with the corresponding uniform bound on `|t| ≤ T`, `T ≥ 0`.
- All these statements transported through the actual Fourier equivalence to
  physical torus fields. The modal perturbation proof does not assume that
  different Dirac matrices commute.

## Evidence and navigation

- [Accepted gate receipt](verification/block51/current/receipt.json):
  26 fresh local compilation targets, 64 recorded commands,
  21 controls (8 positive, 12 elaboration rejections,
  1 axiom-policy rejection).
- [Proof guide](docs/BLOCK_51_PROOF_GUIDE.md) and [source map](docs/SOURCE_MAP.md).
- [Scoped inventory](declaration_inventory.json) and [progress ledger](PROGRESS_LEDGER_v0.51.0.md).
- [Preservation record](BLOCK51_PRESERVATION.json) and [acceptance record](BLOCK51_ACCEPTANCE.json).
- [Predecessor metadata](history/metadata_v0.49.0/PRESERVATION.json), retained unchanged.

The compiler is Lean 4.34.0-rc2 at commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Compiled external dependencies
are reused. The new local import closure was compiled into an empty object
directory. The five root modules received recursive axiom audits and actual
`leanchecker` replay using the same Lean kernel and imported environment.

## Replay

With the documented pinned portable runtime restored, run from this directory:

```sh
python3 verification/block51/current/snapshot/runner/verify_centered.py \
  --project . \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --controls verification/block51/current/snapshot/CONTROL_MANIFEST.json \
  --out-dir /absolute/path/to/a-new-verification-directory
```

The output directory must not already exist. The runtime is external and is not
reconstructed from this source package. Its compiler/source/cache identity is
checked by the supplied runner. Mutable dependency Git indexes are explicitly
excluded from the relevant runtime endpoint comparison and retained in the
provenance records.

## Exact boundaries

The bounded global operator has an explicitly auxiliary zero value at spacing
zero. Its modal evaluation and inverse laws require nonzero spacing, and its
graph limit uses a punctured neighborhood. The centered modal propagator and
resolvent instead use their continuum fill at zero. They are not identified as
the evolution or inverse of the auxiliary zero operator there.

The third-order moment requires actual series summability. The compact-time
bound retains `T ≥ 0`. This checkpoint proves strong resolvent convergence,
not operator-norm resolvent convergence. It does not identify a changing finite
sampled lattice with the fixed Fourier space.

Abstract unbounded spectral-functional-calculus linkage, finite-grid comparison,
interacting gauge evolution, the wider historical evidence audit, and physical
cosmological production remain separate obligations. Earlier cosmological
failures have not been repaired by these free-field theorems.

Original code retains the supplied MIT grant. Original prose and figures retain
the supplied CC BY 4.0 grant and third-party exceptions. See the publication
license and provenance notices supplied alongside this formal package.
