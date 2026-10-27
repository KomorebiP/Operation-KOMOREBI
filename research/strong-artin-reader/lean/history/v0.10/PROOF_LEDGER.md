# v0.10 proof ledger

## Final new theorem

`Komorebi.StrongArtin.QuotientRestriction.semisimple_residual_collapse_cp`

**Input:** prime `p`; finite group `G`; normal `H`; `G/H ≃ C_p`; finite-dimensional
semisimple `F_p` representations `rho`, `sigma`; equivalence of restrictions to `H`.

**Output:** `Nonempty (rho.Equiv sigma)`.

**Status:** compiler checked, warnings as errors, no custom axioms.

## New durable intermediate results

- `repEquivOfAsModuleLinearEquiv`
- `intertwiningMapOfAsModuleLinearMap`
- `semisimple_subrepresentation_retraction`
- `irreducible_equiv_of_common_restricted_constituent`
- `exists_nonzero_ambient_intertwiner_of_nonzero_restriction_intertwiner`
- `exists_injective_ambient_intertwiner_of_irreducible_source`
- `isotypic_equiv_of_finrank_eq`
- `isotypicComponent_complement_eq_bot`
- `restrictIntertwiningMap`
- `subrepresentationAsModuleEquiv`
- `restriction_equiv_maps_isotypicComponent`
- `restriction_equiv_isotypic_finrank_eq`
- `restriction_equiv_isotypicComponent_equiv`
- `simpleTypeOfComponent_simple`
- `component_eq_isotypic_simpleType`
- `transportedIsotypicComponent_mem`
- `transportedComponentMap_injective`
- `transportedComponentMap_bijective`
- `semisimple_equiv_of_restriction_equiv_cp`

## Mathematical mechanism

The defining-characteristic quotient `C_p` has nonzero fixed vectors on every nonzero
finite-dimensional representation. Apply this to the Hom representation of restricted
intertwiners. This lifts nonzero `H`-maps to nonzero `G`-maps. Distinct simple ambient
`G`-types therefore cannot mix under a restricted equivalence. Consequently the
restricted equivalence preserves ambient isotypic blocks. Applying it and its inverse
makes corresponding blocks equidimensional. Semisimple isotypic classification then
gives a `K[G]`-equivalence on each block. The nonzero block sets are bijective and their
internal direct sums reconstruct the entire semisimple modules.

## Consequence for the v0.9 boundary

v0.9 reduced the residual step to `SemisimpleCharpolyRigidityFp` after proving
characteristic-polynomial propagation. v0.10 bypasses that general interface for the
actual prime-cyclic quotient problem: restriction equivalence itself suffices.

This does **not** establish the general finite-field Brauer–Nesbitt property for arbitrary
pairs of semisimple finite-group representations from elementwise characteristic
polynomials alone. That broader interface remains an independent possible theorem.
