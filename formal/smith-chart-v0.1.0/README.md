# Smith chart and cyclic packets: Lean companion

This companion formalizes selected mathematical claims in the public Smith
chart laboratory, bound to Operation-KOMOREBI revision
`ae02554bc86f30626fd9fad8d64b60854e307a80`. The proofs are a separate artifact;
the accompanying browser update is tested separately and is not certified by
the Lean results.
The later 172-file research archive was recovered on 11 November 2026; see the
[complete reading](https://komorebip.github.io/Operation-KOMOREBI/read/smith-chart/research.html)
and [source record](../../research/smith-chart/README.md). Its later circuit
claims are not generally covered by this companion. A separate
[first-order RL formalization](../../research/smith-chart/formal/README.md)
checks the limiting one-inductor realization. The historical run15 receipt
predates these documentation updates; it records the earlier input hashes.

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

For a nonzero starting reflection coefficient, a target belongs to the
finite canonical phase orbit exactly when their ratio has Nth power one.
The zero-start case, an order-two versus order-four quarter-turn example,
a noncoprime projector counterexample, and the equalities and positive-real
bound for a two-sample witness are also proved. For any finite set of
samples inside the disk, Lean also constructs two entire functions with
positive real part on the disk that agree at the samples and differ at
another point in the disk.

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
abstract average lower bound that equal interval masses attain. A further Lean
module proves that the chart's sampling density is normalized, its CDF is
continuous and strictly increasing, with a unique noncomputable inverse. A
piecewise real arctangent formula is proved to equal that inverse on `[0,1]`,
including its branch points. An ordered equal-mass partition exists for every `N > 0` and `0 ≤ ρ < 1`. The
energy modules prove the infinite squared-coefficient sums and identify them
with the actual packets' angular mean-square integrals for `0 ≤ ρ < 1`. This is separate from the
finite phase-orbit Parseval identity and does not assert a finite boundary norm.

## Files

| File | Scope |
| --- | --- |
| [SmithPackets.lean](SmithPackets.lean) | Convergent lane series, impedance/admittance formulas, reconstruction, dyadic refinement |
| [SmithFourier.lean](SmithFourier.lean) | Exact-order character filter and finite phase averages |
| [SmithAnalyticFourier.lean](SmithAnalyticFourier.lean) | Phase-average identity for the actual analytic impedance |
| [SmithParseval.lean](SmithParseval.lean) | Finite phase-orbit Parseval, including the impedance specialization |
| [SmithCanonicalRoot.lean](SmithCanonicalRoot.lean) | Exact order of `exp(2πi/N)` and specialization to it |
| [SmithBoundaries.lean](SmithBoundaries.lean) | Discrete orbit reachability, boundary examples, and a positive-real two-sample witness |
| [SmithFiniteSamples.lean](SmithFiniteSamples.lean) | Finite-sample nonuniqueness for positive-real analytic coordinate functions |
| [SmithGeometry.lean](SmithGeometry.lean) | Cayley inverses and open/closed passive domains |
| [SmithAlgebra.lean](SmithAlgebra.lean) | Projector, coprime, and finite convolution support identities |
| [SmithSampling.lean](SmithSampling.lean) | Angular sensitivity formula and the abstract equal-mass bound |
| [SmithSamplingIntegral.lean](SmithSamplingIntegral.lean) | Density normalization, CDF, and existence of equal-mass partitions |
| [SmithSamplingInverse.lean](SmithSamplingInverse.lean) | Unique noncomputable inverse CDF and its monotonicity |
| [SmithExplicitInverse.lean](SmithExplicitInverse.lean) | Piecewise real inverse on all of `[0,1]`, including branch points |
| [SmithEnergy.lean](SmithEnergy.lean) | Convergent squared-coefficient energy formulas |
| [SmithEnergyIntegral.lean](SmithEnergyIntegral.lean) | Finite-radius angular means of actual packets equal their coefficient energies |
| [SmithResults.lean](SmithResults.lean) and [SmithExamples.lean](SmithExamples.lean) | Positive-real zero lane and explicit boundary/counterexample fixtures |
| [AxiomAudit.lean](AxiomAudit.lean) | Named declarations audited for Lean axioms |

The exact mappings, exclusions, and self-review are in [AUDIT.md](AUDIT.md).
The mathematical sampling argument is in [SAMPLING_DERIVATION.md](SAMPLING_DERIVATION.md);
its complex-lift presentation remains self-reviewed prose. Normalization and
partition existence are proved in [SmithSamplingIntegral.lean](SmithSamplingIntegral.lean);
a separate real inverse formula is proved in [SmithExplicitInverse.lean](SmithExplicitInverse.lean).
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
The correspondence between the proved real inverse and the browser's complex
branch-lift and floating-point operations is not formalized here. The equal-mass
partition concerns integrated sampling density; the minimax bound
concerns interval mass, not universal interpolation error. Novelty and an advantage on measured or
noisy RF data remain separate research questions. No completion claim is made
about the full later research archive or its circuit-synthesis claims.
