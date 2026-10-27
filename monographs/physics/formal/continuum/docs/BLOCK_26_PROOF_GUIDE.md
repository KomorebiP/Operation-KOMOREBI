# Block 26 proof guide — geometric edge refinement

## 1. Purpose

Block 25 proved exact refinement on a cylinder: every coarse site acquired a spectator child while translations and links were pulled back unchanged.  Block 26 makes the first geometry-changing step.  One coarse oriented edge is divided into two actual half-edges, and the fine translation traverses the midpoint before reaching the next coarse endpoint.

The block is deliberately one-axis.  The final plaquette theorems explain why this restriction is mathematically substantive rather than cosmetic.

## 2. Fine geometry

For a coarse site type `Site`, define

`HalfSite Site = Sum Site Site`.

`inl x` denotes the coarse endpoint and `inr x` the midpoint on the edge from `x` to `τ x`.  The half translation satisfies

- `halfShift τ (inl x) = inr x`
- `halfShift τ (inr x) = inl (τ x)`.

Lean proves

`halfShift τ (halfShift τ y) = coarseLift τ y`.

`MeshScale.half` records that the fine edge spacing is half the coarse spacing and proves `2 * a.half.spacing = a.spacing`.  This is scale metadata, not a continuum chart theorem.

## 3. Ordered sublink reconstruction

An `EdgeSubdivision u` contains two `U(1)` links and the ordered reconstruction law

`second x * first x = u x`.

The order matters: transport first crosses `first`, then `second`.  The fine link selects the corresponding factor on the two halves.

Every coarse link admits a subdivision after choosing the first half-link.  A boundary subdivision uses a trivial first half-link and the original coarse link as the second.

## 4. Gauge-covariant interpolation

The embedding is

`I_S ψ (inl x) = ψ x`,

`I_S ψ (inr x) = first x • ψ x`.

The midpoint is therefore not a duplicated spectator value.  It is the value obtained by parallel transport along the first geometric subedge.

Endpoint and midpoint gauges may be chosen independently.  The first and second sublinks transform as

`first^g x = g_mid x * first x * (g x)^-1`,

`second^g x = g (τ x) * second x * (g_mid x)^-1`.

Their product reconstructs the transformed coarse link.  Lean proves both fine-link and interpolation covariance.

## 5. Exact directional intertwining

For every Clifford involution `A`,

`S_fine² (I_S ψ) = I_S (S_coarse ψ)`.

This theorem uses the Clifford projector split in `directionalShift` and the exact ordered sublink product.  It is not a scalar shift shortcut.  The named `intertwiningDefect` is then proved pointwise equal to zero.

## 6. Hilbert normalization and restriction

Raw interpolation contains an endpoint and a transported midpoint, so

`stateIP (I_S ψ) (I_S φ) = 2 * stateIP ψ φ`.

The fine inner product uses half-cell measure:

`halfCellIP Ψ Φ = (1/2) * stateIP Ψ Φ`.

Lean proves exact isometry

`halfCellIP (I_S ψ) (I_S φ) = stateIP ψ φ`.

The reconstruction map averages the endpoint with the back-transported midpoint.  It is proved to be the Hilbert adjoint of interpolation.  The composite `I_S R_S` is idempotent and fixes every interpolated state.

## 7. One-axis massive walk

A symmetric coarse step is

`M-S-M`.

A `LocalStepSubdivision` supplies a local half-step whose square is the coarse local step.  The refined step replaces every coarse factor by two half factors:

`M_half²-S_half²-M_half²`.

Lean proves exact intertwining with `M-S-M`.  Spectral phases of a Hermitian Clifford involution give concrete local square roots.  A Hilbert-certified version proves preservation of the half-cell inner product by the complete refined one-axis walk.

## 8. Plaquette obstruction

For commuting coarse translations, define the two corner path phases

`P_xy(x) = u_y(τ_x x) * u_x(x)`,

`P_yx(x) = u_x(τ_y x) * u_y(x)`

and the plaquette

`Ω_xy(x) = P_xy(x) / P_yx(x)`.

Lean proves:

`Ω_xy(x) = 1 <-> P_xy(x) = P_yx(x)`.

It also proves gauge invariance of `Ω_xy`, and—using a fixed nonzero four-spinor—equivalence between flatness and equality of the two transported spinors.

A Boolean periodic witness has `Ω = -1`, so universal path independence is formally false.  This is the exact point at which gauge curvature enters the refinement program.

## 9. Main declarations

- `halfShift_sq`
- `EdgeSubdivision.embed_gauge_covariant`
- `EdgeSubdivision.two_halfSteps_embed`
- `EdgeSubdivision.intertwiningDefect_eq_zero`
- `embed_halfCellIP_isometry`
- `embed_restrict_adjoint`
- `directionalShift_halfCellIP`
- `refinedOneAxisWalk_embed`
- `refinedOneAxisWalk_gauge_covariant`
- `refinedOneAxisWalk_halfCellIP`
- `plaquette_eq_one_iff_path_independent`
- `plaquette_gauge_invariant`
- `corner_transport_eq_iff_flat`
- `bool_plaquette_nonflat`

## 10. Formal boundary

The block proves exact edge subdivision and exact one-axis factorwise dynamics.  It does not provide a simultaneous cubical interpolation for all three axes, a full fine/coarse seven-factor comparison, a curvature-norm estimate, or continuum convergence.  Those are the next obligations.
