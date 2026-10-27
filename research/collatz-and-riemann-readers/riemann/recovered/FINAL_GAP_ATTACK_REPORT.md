# Komorebi RH final-gap attack — v0.13.0

## Executive result

This tranche closes several downstream analytic and algebraic gaps, but it
does not prove the Riemann hypothesis.

New completed work:

1. a concrete polynomial-growth bound for the archimedean digamma kernel,
   giving an `O(1)` pole-free unit-band energy;
2. a proof that the pole-annihilated zero packet has exactly the same
   exponential heat front as the original zero packet;
3. a justified differentiated completed explicit formula on every positive
   heat-time strip;
4. kernel-checked physical-metric leakage bookkeeping with a visible-defect
   channel;
5. a kernel-checked no-go theorem for commuting diagonal scale filters;
6. a kernel-checked proof that exact high-pass reconstruction cancels its local
   Euler factor and therefore does not damp an eigenmode;
7. a kernel-checked proof that generalized `beta` filters share the same
   normalized zero mode;
8. a continuum computation showing that an apparently strong mixed-cycle
   profile approximation does not accumulate a vanishing contraction.

The arithmetic obstruction remains the first-prime/Möbius coherence channel.

## Closed implication chain

Let
\[
 \widetilde E_J
 =\int_{t_0}^T\int_J^{J+1}
 |\widetilde\Theta_t(u)|^2\,du\,dt.
\]
The analytic work proves
\[
 RH\iff \widetilde E_J=e^{o(J)}.
\]
The certified Gaussian-tail theorem and the concrete archimedean estimate
remove the discarded-prime and gamma channels at subexponential cost.
The stable Hermite compression represents the remaining packet in `O(J)`
orthogonal physical modes with exponentially small reconstruction error.

Hence a single estimate remains sufficient:
\[
 \sum_p\sum_{r\le R_J}
 \|D_pB_{r,J}\|_{L^2(t)}^2
 \ge
 \delta_J\sum_{r\le R_J}\|B_{r,J}\|_{L^2(t)}^2-B_J,
\]
with
\[
 \delta_J^{-1}=e^{o(J)},
 \qquad
 B_J=e^{o(J)},
\]
together with a sublinear historical upper bound on the detail energy.
The existing variable-gap record theorem would then imply RH.

## Failed closure mechanisms

### Raw positive fourth moment

The diagonal collision contribution already equals the square of the quadratic
energy. A strict moment saving is impossible without a signed or quotient
transformation.

### Raw integer Gaussian frame

Adjacent logarithmic translates have condition number at least
`8 t n^2`, exponential at scale `n≈e^J`. Hermite compression fixes this but
retains the RH-bearing ground channel.

### Multiple generalized scale filters

All `K_beta` are diagonal functions of the same logarithmic Hamiltonian. Their
normalized zero modes coincide after natural-scale substitution. They cannot
create hypocoercive mixing.

### Global Hardy norms

On squarefree support, multiplication by the Möbius sign is the prime-torus
rotation `z_p -> -z_p`.  Haar-invariant `H^p` norms are therefore exactly
sign-blind.  Critical-line local embedding can transfer a Hardy estimate but
cannot manufacture the missing Möbius cancellation.

### Exact prime high-pass reconstruction

A zero/power mode receives a local factor `1-p^{-rho}` from the high-pass
operation and the reciprocal factor from the coprime reconstruction. Exact
reconstruction preserves the mode.

### Iterated prime transport

It controls composite channels and leaves a nested coprime sector. The chain
ends at the primitive first-prime layer, which is exactly the known analytic
obstruction.

## What would actually finish RH

At least one of the following must be proved for the concrete compressed
packet:

1. **physical prime leakage**
   \[
   \sum_p \operatorname{Inf}^{\rm phys}_p(F_J)
   \ge \delta_J E_J-B_J;
   \]
2. **signed collision saving**
   \[
   \mathcal O_{4,J}
   \le -\eta_J E_{2,J}^2+e^{o(J)};
   \]
3. **near-L2 projected-vector saving**
   \[
   \|G_J\|_{\mathscr H^{2+\varepsilon}}^{2+\varepsilon}
   \le e^{o(J)}(1+M_{J-1})^{1+\varepsilon/2-\eta_J};
   \]
4. **direct first-prime heat bound**
   \[
   \int_{t_0}^T\int_J^{J+1}
   |\text{centered first-prime layer}|^2\,du\,dt=e^{o(J)}.
   \]

Each formulation excludes an off-critical zero and is therefore genuinely
RH-level. No current Komorebi theorem proves one of them.

## Lean verification

Four focused modules were checked using the pinned offline Lean
`4.34.0-rc2` / Mathlib environment:

- `PhysicalMetricLeakage.lean`;
- `DiagonalHypocoercivityNoGo.lean`;
- `HighpassReconstructionNoGo.lean`;
- `NaturalScaleModeNoGo.lean`.

The combined `#print axioms` audit reports only the ordinary Mathlib logical
foundations where needed. Two false controls were rejected:

- strict contraction on a diagonal neutral axis;
- the squared-energy estimate without nonnegativity of the total.

The latter exposed and repaired a real missing hypothesis in the v0.12 draft.

## Computation boundary

The profile computation verifies closed-form integrals against independent
quadrature. It does not calculate the missing Möbius cancellation and is not
numerical evidence for RH.

## Final status

\[
 \boxed{\text{RH remains unproved.}}
\]

The remaining gap has not been hidden. It is the same-scale cancellation of
the primitive first-prime/Möbius channel after all stable analytic,
completion, transport, and compression layers have been removed.
