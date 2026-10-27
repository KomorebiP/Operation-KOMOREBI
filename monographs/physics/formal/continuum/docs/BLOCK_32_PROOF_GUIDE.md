# Block 32 proof guide

## 1. Directional shifts on the finite Hilbert space

- `directionalShiftHilbertLinear` conjugates the existing position-space
  Clifford shift through `stateHilbertEquiv`.
- `directionalShiftHilbertCLM` packages it as a continuous linear map.
- `directionalShiftHilbertCLM_norm_eq` proves exact norm preservation for a
  Hermitian Clifford involution and a `Circle`-valued link.
- `directionalShiftHilbertCLM_opNorm_le_one` records contractivity.

The operator norm is the actual finite Euclidean `ℓ²` norm introduced in Block
31.

## 2. Sharp local edge estimate

`intertwiningDefectOp_directionalShiftHilbert_id` identifies the local
intertwining defect with the directional link-difference operator. The Block 31
constant-one estimate then gives

\[
\|S_v-S_u\|
\le
\operatorname{edgeRatioSup}(v,u).
\]

This is exposed as
`directionalShiftHilbertDefect_opNorm_le_ratioSup`.

## 3. Full palindromic walk

`hilbertSevenFactorPairs` records the ordered fine/coarse pairs

\[
M_0,X,Y,Z,Y,X,M_1.
\]

`hilbertEdgeBudget` is

\[
2\delta_x+2\delta_y+\delta_z.
\]

The mass pairs are identical on the two sides, so their local defects vanish.
Every shift and each assumed mass factor is contractive. Applying the checked
finite-product telescoping theorem yields

\[
\boxed{
\|D_W\|
\le
2\delta_x+2\delta_y+\delta_z.
}
\]

This is `norm_hilbertSevenFactorDefect_le_edgeBudget`.

`quarterX_hilbertEdgeBudget` is a concrete multiplicity witness: an `x`-link
mismatch of size two contributes four because `X` occurs twice.

## 4. Cubical path-swap operators

`hilbertPhaseOp z` is uniform multiplication by a unit-circle phase on the full
finite Hilbert state. It has operator norm one.

For parallel paths with phases `p` and `q`, `hilbertPhaseDefectOp p q` is their
operator difference. If `p = Ω q`, then

\[
\boxed{
\|P_p-P_q\|=|\Omega-1|.
}
\]

The theorem is `norm_hilbertPhaseDefectOp_eq_curvature`.

The five independent adjacent corner-path swaps are packaged in
`hilbertCubeSwapSevenPairs`. Applying the product telescoping theorem gives

\[
\|D_\Omega\|\le\operatorname{curvatureBudget}(L).
\]

Flat cubical data makes this operator exactly zero.

## 5. Combined two-stage theorem

`combinedHilbertDefect` first compares the two full seven-factor walks and then
compares the cubical path-reordering stages. Contractivity of the outer and
inner composites permits the checked two-stage defect theorem to be applied:

\[
\boxed{
\|D_{\mathrm{total}}\|
\le
\operatorname{hilbertEdgeBudget}
+
\operatorname{curvatureBudget}.
}
\]

Expanded, this is

\[
\boxed{
\|D_{\mathrm{total}}\|
\le
2\delta_x+2\delta_y+\delta_z
+
\sum_{f\in\mathcal F_5}|\Omega_f-1|.
}
\]

`combinedHilbertDefect_eq_zero_of_exact_flat` proves the exact zero sector when
the reconstructed links equal the prescribed links and the cube is flat.

## 6. Why the budgets remain independent

The straight budget compares two ordered half-edge products with their intended
coarse links. The curvature budget compares alternative paths with the same
endpoints. Previous checked witnesses prove neither condition implies the
other. Block 32 composes the two channels without identifying them.

## Boundary

The block proves a finite-volume operator theorem. It does not derive any mesh
rate for the edge ratios or plaquettes, does not construct a continuum
`L²(ℝ³,ℂ⁴)` reconstruction, and does not prove continuum Dirac or dynamical
gauge-field equations.
