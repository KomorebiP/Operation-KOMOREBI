# Block 25 proof guide

## 1. Corrected local phase type

The repaired position-space transport uses Mathlib's `Circle`, the subgroup of complex numbers with unit modulus. This corrects the earlier candidate's use of `ℂˣ`, which contains every nonzero complex number and does not preserve Hilbert norm in general.

For each spatial Clifford involution `A`, the complementary channels are

`P⁺ = (I + A)/2`,

`P⁻ = (I - A)/2`.

The source proves idempotence, complementarity, and cross annihilation. The concrete `α_x`, `α_y`, `α_z`, and `β` actions satisfy the required involution and anticommutation identities.

## 2. Gauge-covariant directional transport

For a site equivalence `τ` and unit-circle link `u`, the directional shift is

`S_{A,τ,u} ψ(x) = u(τ⁻¹x) P⁺ψ(τ⁻¹x) + u(x)⁻¹ P⁻ψ(τx)`.

An explicit inverse is defined and both compositions are proved equal to the identity. For a site gauge `g`, the transformed link is

`u^g(x) = g(τx) u(x) g(x)⁻¹`.

The exact covariance theorem is

`S_{A,τ,u^g}(G_g ψ) = G_g(S_{A,τ,u} ψ)`.

The same relation is proved for the complete `M-X-Y-Z-Y-X-M` walk.

## 3. Finite four-spinor Hilbert structure

The spinor inner product is

`ip(ψ,φ) = Σ_j conj(ψ_j) φ_j`.

The source proves:

- sesquilinearity
- `ip(ψ,ψ) = Σ_j normSq(ψ_j)`
- nonnegativity of the real part of `ip(ψ,ψ)`
- `ip(ψ,ψ)=0 ↔ ψ=0`
- self-adjointness of the three spatial Clifford involutions and `β`
- orthogonality of the positive and negative spectral channels
- invariance under every `Circle` phase

For a finite site type, summing `ip` over sites gives `stateIP`. Reindexing the positive and negative channels through the site equivalence proves exact directional preservation:

`stateIP(Sψ,Sφ) = stateIP(ψ,φ)`.

A spectral `β` phase step is proved Hilbert preserving. Composition yields exact preservation for the seven-factor walk.

## 4. One-step dyadic refinement

A fine site is `Site × Fin 2`. The embedding replicates the coarse spinor into both children. Translations, links, and gauges are pulled back through the first coordinate.

The exact intertwining theorem is

`W_fine(replicate ψ) = replicate(W_coarse ψ)`.

Raw counting measure doubles:

`stateIP(replicate ψ, replicate φ) = 2 stateIP(ψ,φ)`.

After assigning each child half the coarse cell measure, replication is exactly Hilbert-isometric.

## 5. Recursive exact tower

The recursive site hierarchy is

`DyadicSite Base 0 = Base`,

`DyadicSite Base (n+1) = DyadicSite Base n × Fin 2`.

Translations, links, gauges, states, and walks are lifted recursively. Lean proves adjacent exact compatibility at every level. These data define a concrete `ExactRefinementTower` from Block 24.

The weighted inner product at depth `n` is

`2^{-n} stateIP`.

Every adjacent embedding is an isometry for these weights, and every levelwise walk preserves the weighted inner product.

## 6. Exact reconstruction instance

A reconstruction follows the zero-child branch back to the base lattice. It is exactly compatible with replication. Therefore the Block 24 reconstruction sequence has zero adjacent defect. Lean proves that the canonical global state and global evolution of this exact cylinder realization are the base state and base walk.

This is a concrete theorem about the exact tower. It is not yet an identification with a continuum field space.

## 7. Trust boundary

The new extension was rebuilt from source in an independent clean project against the pinned dependency cache. The Lean compiler and imported Mathlib cache were not rebuilt from compiler source. The 121 parent modules were not all recompiled from scratch in the independent extension run. Instead, they are inherited from the checked v0.22 release and verified byte-identical.
