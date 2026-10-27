# Block 49 Proof Guide

## Namespace

`KomorebiPhysics.Relativistic3DWeightedDomain`

## Construction order

1. Define the exact mode energy `modeEnergySq` from the checked Dirac symbol.
2. Use the Clifford square identity and mode symmetry to prove
   `‖H_m(n) ψ‖² = E_m(n)² ‖ψ‖²`.
3. Convert maximal-domain membership into summability of the exact weighted modal energies.
4. Split the energy into the square-summable mass term and pure momentum term.
5. Identify the maximal domain with the inhomogeneous first-order Fourier condition
   `Σ (1 + |k_n|²) ‖f_n‖² < ∞`.
6. Deduce that the maximal domain is independent of the mass parameter.
7. Pull the domain back through `torusFourierEquiv` and conjugate the coefficient `LinearPMap`.
8. Prove density and symmetry of the physical operator.
9. Transport adjoint-domain vectors to coefficient space, apply the checked coefficient adjoint theorem, and transport back.
10. Conclude physical-space self-adjointness and closedness.
11. Prove exact coefficient-space and physical-space energy-sum identities.

## Load-bearing declarations

- `continuumHilbertModeOperator_sq`
- `norm_continuumHilbertModeOperator_sq`
- `mem_continuumDiracDomain_iff_summable_weighted`
- `mem_continuumDiracDomain_iff_summable_h1`
- `mem_continuumDiracDomain_iff_mass`
- `physicalDiracPMap`
- `mem_physicalDiracDomain_iff_summable_h1`
- `physicalDiracAdjoint_domain_le`
- `physicalDiracPMap_selfAdjoint`
- `physicalDiracPMap_isClosed`
- `norm_physicalDiracPMap_sq_eq_tsum_weighted`

## Interpretation

The coefficient maximal domain is exactly the first-order Fourier-Sobolev domain. The physical torus Hamiltonian is an unbounded `LinearPMap`, not a bounded continuous endomorphism. Its self-adjointness is proved by unitary Fourier conjugation at the level of domains and Hilbert adjoints.
