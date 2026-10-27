# Abstract Stochastic Projector Refinement v0.1.0 — Lean Checked

This block generalizes the earlier coordinate/residue stochastic polyphase theorem to arbitrary finite orthogonal bounded-projector refinements and then specializes the result to Hilbert-space covariance/Lyapunov forcing.

## Verification

Checked with warnings promoted to errors under:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

Final source:

- 22 theorem declarations
- 6 definitions
- 2 structures
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

The final warning-as-error compiler check and separate `#print axioms` audit both return exit code `0`. Representative central theorems depend only on ordinary Lean/Mathlib foundations: `propext`, `Classical.choice`, `Quot.sound`.

## 1. Abstract orthogonal refinement

For coarse bounded projectors `C a`, fine bounded projectors `F c`, and a refinement map `ρ`, the structured theorem assumes exact fiber refinement

`C a = Σ_{ρ c = a} F c`

with the fine projectors idempotent and mutually orthogonal.

For any bounded operator `T`, define the source-target corner

`C a ∘ T ∘ C b`.

Lean proves exact refinement:

`C a ∘ T ∘ C b = Σ_{ρ c=a, ρ d=b} F c ∘ T ∘ F d`.

It also proves the no-cancellation equivalence

`C a ∘ T ∘ C b = 0`
iff every descendant `F c ∘ T ∘ F d = 0`,

and the adaptive trigger

`C a ∘ T ∘ C b ≠ 0`
iff some fine descendant corner is nonzero.

## 2. Minimal-hypothesis theorem

A second version removes completeness assumptions entirely. It takes arbitrary coarse maps `C`, fine maps `F`, and assumes only:

1. `F c ∘ F c = F c`;
2. `F c ∘ F d = 0` for `c ≠ d`;
3. `C a = Σ_{ρ c=a} F c`.

No coarse completeness and no fine completeness are assumed.

Under precisely those hypotheses Lean proves:

- exact block refinement;
- left and right descendant absorption;
- zero coarse block iff all descendants are zero;
- nonzero coarse block iff some descendant is nonzero;
- operator-norm bound

  `‖C a ∘ T ∘ C b‖ ≤ Σ_{ρ c=a,ρ d=b} ‖F c ∘ T ∘ F d‖`.

This identifies the actual algebraic source of the no-cancellation property: orthogonal idempotent descendant blocks with exact fiber-sum refinement.

## 3. Hilbert-space stochastic covariance theorem

On a real Hilbert space, let coarse projectors be self-adjoint and let the exactly aligned baseline operators `A0`, `P`, and `Q0` commute with every coarse projector.

Define the covariance/Lyapunov forcing

`L(A,P,Q) = A ∘ P + P ∘ A† + Q`.

For perturbations `RA`, `RQ`, Lean first proves the exact residual split

`L(A0+RA,P,Q0+RQ) = L(A0,P,Q0) + L(RA,P,RQ)`.

The baseline forcing commutes with the coarse projectors, so every off-coarse baseline corner is zero. Hence for `a ≠ b`:

`C a ∘ L(A0+RA,P,Q0+RQ) ∘ C b
 = C a ∘ L(RA,P,RQ) ∘ C b`.

Combining this with abstract refinement gives the coordinate-free stochastic theorem:

`C a ∘ L(A0+RA,P,Q0+RQ) ∘ C b
 = Σ_{ρ c=a,ρ d=b} F c ∘ L(RA,P,RQ) ∘ F d`.

Lean additionally proves:

- off-coarse covariance forcing is zero iff every fine residual descendant is zero;
- off-coarse covariance forcing is nonzero iff some fine residual descendant is nonzero;
- quantitative leakage budget

  `‖coarse off-block‖ ≤ Σ descendant ‖fine residual block‖`.

## Boundary

This theorem is coordinate-free with respect to the projector system, but the Hilbert stochastic specialization assumes self-adjoint coarse projectors and exact commutation of the baseline `A0`, `P`, `Q0` with them. It is an instantaneous covariance-forcing theorem, not by itself a finite-time Grönwall bound for the full covariance error process.

The earlier residue/dyadic theorem remains useful as a concrete polyphase realization; this block supplies the abstract orthogonal-projector theorem explaining why that realization has no hidden cancellation.
