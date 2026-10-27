# Block 39 proof guide — Euclidean transported levels and strong projection convergence

## Hilbert transport

1. Reuse the Block 38 isometric pullback `U` from cube `L²` to octree `L²`.
2. Define `U†` using `ContinuousLinearMap.adjoint`.
3. Apply `LinearIsometry.adjoint_comp_self` to prove `U†U=I`.
4. Use equality of adjoint and original operator norms to prove `‖U†g‖≤‖g‖`.

## Euclidean levels

1. Let `M_n` be the Block 36 octree finite-prefix submodule.
2. Define the raw Euclidean image `U†(M_n)` as a mapped submodule.
3. Define `V_n` as its topological closure.
4. Transport `M_n⊆M_m` through `Submodule.map_mono` and closure monotonicity.
5. Approximate `Uf` by `h∈M_n`; then use contractivity of `U†` and `U†Uf=f`.
6. Deduce density of `⨆n,V_n` from the metric characterization of density.

## Orthogonal projection

1. Install the complete-space instance for each closed `V_n`.
2. Define `P_n=V_n.starProjection`.
3. Use the standard projection theorems for fixed points, range membership, idempotence, and contraction.
4. Use `starProjection_minimal` for the best-approximation inequality.
5. Use nesting to prove `P_m(P_nf)=P_nf` for `n≤m`.

## Strong convergence

1. Fix `f` and `ε>0`.
2. Choose `g∈V_N` with `dist g f<ε` by density.
3. For `n≥N`, transport membership to `g∈V_n`.
4. Apply best approximation to bound `‖f-P_nf‖` by `‖f-g‖`.
5. Conclude `P_nf→f` with `Metric.tendsto_atTop`.
