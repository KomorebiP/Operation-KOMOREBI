# Smith chart and cyclic packets: Lean companion

This companion formalizes selected mathematical claims in the public Smith
chart laboratory, bound to Operation-KOMOREBI revision
`ae02554bc86f30626fd9fad8d64b60854e307a80`. It is a separate proof artifact:
the source manuscripts and browser implementation have not been changed.
The later ChatGPT conversation “Continue Smith Chart Work” was located, but
its assistant messages were unavailable to this session; its contents have
therefore not been reconciled with this companion.

## Mathematical contract

Let `N > 0`, `0 ≤ j < N`, `t ∈ ℂ`, and `‖t‖ < 1`. Put
`z(t) = (1+t)/(1-t)`, `y(t) = (1-t)/(1+t)`, and
`ω = exp(2πi/N)`. The coefficient packet is defined by an actual convergent
series, not by its intended closed form:

```
P[N,0]z(t) = 1 + ∑ m≥0, 2 t^((m+1)N)
P[N,j]z(t) =     ∑ m≥0, 2 t^(j+mN)          (j > 0).
```

The Lean proofs establish their respective closed forms, reconstruction of
`z`, and the dyadic split into lanes `j` and `j+N` at order `2N`. They identify
each packet with the ordinary normalized `ω`-phase average of `z`. The
canonical exponential root is proved to have exact order `N`, rather than
being assumed primitive. For admittance the proofs establish `y(t)=z(-t)`,
`y(t)=z(t)⁻¹` under Lean's totalized division convention, the even-order
parity formula, and the distinct odd-order formulas.

The finite phase-orbit Parseval identity is proved for arbitrary complex
samples and for these impedance packets: the sum of squared packet magnitudes
equals the average squared magnitude around the orbit.

The geometry includes finite passive normalized impedances: away from the
singular denominator `z+1=0`, `Re z ≥ 0` is equivalent to a reflection
coefficient in the closed unit disk. Strict inequalities give the open-disk
bijection. The ideal open is the missing projective point at `t=1`; it is not
a finite complex impedance. Lean totalizes division by zero, so evaluations
at that pole must not be interpreted as physical values.

The coefficient projectors are idempotent and orthogonal; coprime factor
projectors compose to the product-order projector. A finite convolution of
lanes `r` and `s` has no coefficients outside lane `r+s`. The sampling module
proves the angular rational formula for the symmetric sensitivity weight and the
abstract average lower bound that equal interval masses attain. The energy
module proves the corresponding infinite squared-coefficient sums.

## Files

| File | Scope |
| --- | --- |
| [SmithPackets.lean](SmithPackets.lean) | Convergent lane series, impedance/admittance formulas, reconstruction, dyadic refinement |
| [SmithFourier.lean](SmithFourier.lean) | Exact-order character filter and finite phase averages |
| [SmithAnalyticFourier.lean](SmithAnalyticFourier.lean) | Phase-average identity for the actual analytic impedance |
| [SmithParseval.lean](SmithParseval.lean) | Finite phase-orbit Parseval, including the impedance specialization |
| [SmithCanonicalRoot.lean](SmithCanonicalRoot.lean) | Exact order of `exp(2πi/N)` and specialization to it |
| [SmithGeometry.lean](SmithGeometry.lean) | Cayley inverses and open/closed passive domains |
| [SmithAlgebra.lean](SmithAlgebra.lean) | Projector, coprime, and finite convolution support identities |
| [SmithSampling.lean](SmithSampling.lean) | Angular sensitivity formula and the abstract equal-mass bound |
| [SmithEnergy.lean](SmithEnergy.lean) | Convergent squared-coefficient energy formulas |
| [SmithResults.lean](SmithResults.lean) and [SmithExamples.lean](SmithExamples.lean) | Positive-real zero lane and explicit boundary/counterexample fixtures |
| [AxiomAudit.lean](AxiomAudit.lean) | Named declarations audited for Lean axioms |

The exact mappings, exclusions, and self-review are in [AUDIT.md](AUDIT.md).
The mathematical sampling argument is in [SAMPLING_DERIVATION.md](SAMPLING_DERIVATION.md);
its integration and inverse-CDF steps are self-reviewed prose, not Lean results.
The corresponding angular-energy argument is in [ENERGY_DERIVATION.md](ENERGY_DERIVATION.md).
The current continuation point is [STATUS.md](STATUS.md).

## Replay

`replay.py` checks source objects at the pinned repository revision, the
compiler, Mathlib and package revisions, input hashes, and the hashes of
directly imported cached Mathlib objects. It copies the companion into a new
build directory, compiles with warnings as errors, and checks the declared
axiom report. It requires the pinned Windows Lean compiler and a Mathlib
checkout with built caches; it does not build or install those dependencies.

```powershell
python replay.py --lean <absolute-lean.exe> --mathlib <absolute-mathlib> `
  --git <absolute-git.exe> --repo <absolute-Operation-KOMOREBI-checkout> `
  --output <new-output-directory>
```

The toolchain and dependency identities are recorded in
[dependency-lock.json](dependency-lock.json); source-object hashes are in
[source-bindings.json](source-bindings.json). The replay reuses compiled
dependencies and does not rebuild or hash every transitive cache object.

## Remaining scope

The results do not constitute a proof of the JavaScript implementation or its
floating-point behavior. A bounded independent-oracle check of the pinned
browser math is recorded in [computations/runtime-001/manifest.json](computations/runtime-001/manifest.json),
with its assertion and tested range in [computations/runtime-contract.json](computations/runtime-contract.json).
An independent high-precision quadrature check at 44 quantiles, including
values near the half-turn, is in [computations/quadrature-001/manifest.json](computations/quadrature-001/manifest.json).
The local chart correction is tested separately in
[computations/runtime-003/manifest.json](computations/runtime-003/manifest.json)
and [computations/quadrature-004/manifest.json](computations/quadrature-004/manifest.json).
The angular Parseval/H² interpretation, the
normalization and inverse-CDF derivation for the Poisson sampling density, and
the existence of its equal-mass partition are not formalized here. The
equal-mass theorem assumes the equal-mass candidate and bounds interval mass,
not universal interpolation error. Novelty and an advantage on measured or
noisy RF data remain separate research questions. No completion claim is made
about the unavailable later ChatGPT continuation.
