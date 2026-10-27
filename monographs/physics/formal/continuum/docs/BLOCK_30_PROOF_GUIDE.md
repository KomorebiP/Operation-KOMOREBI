# Block 30 proof guide

## 1. Continuous-linear finite-lattice realization

- `directionalShiftLinear` and `directionalShiftCLM` package each finite-lattice
  Clifford shift as a complex continuous linear map.
- `frameEmbedLinear` and `frameEmbedCLM` package phase-frame interpolation.
- `twoHalfShiftXCLM`, `twoHalfShiftYCLM`, and `twoHalfShiftZCLM` package the two
  geometric half-step operators used by adjacent-scale refinement.
- `straightDefectOpX/Y/Z` are the actual adjacent-scale operators
  `F_i I_r - I_r C_i`.

Continuity is obtained from finite dimensionality.  The operator norm on these
maps is the ambient Mathlib norm of the finite function space.  The exact
half-cell Hilbert-energy identities below are retained separately and are not
silently identified with that operator norm.

## 2. Exact one-axis defect operator

- `fineEdgeDefectLinear` and `fineEdgeDefectCLM` package the arbitrary half-link
  defect from Block 29 as a continuous linear map.
- `fineEdgeDefectCLM_halfCellIP` identifies its half-cell Hilbert energy with the
  reconstructed coarse-link mismatch energy.
- `fineEdgeDefectCLM_energy` gives the explicit positive/negative Clifford
  channel formula.
- `fineEdgeDefectCLM_eq_zero_of_product` closes the exact compatible sector.

## 3. Seven-factor straight-edge budget

- `straightSevenFactorPairs` lists the two mass factors and the five spatial
  factors in the physical `M-X-Y-Z-Y-X-M` order.
- `straightSpatialBudget` is the sum of the five actual spatial operator norms.
- `norm_straightSevenFactorDefect_le` inserts those factors into the Block 28
  telescoping theorem.
- `straightSevenFactorDefect_eq_zero` proves exact full-walk intertwining from
  the three straight reconstruction contracts.  No plaquette-flatness
  hypothesis appears.

## 4. Multiplicative edge ratios

- `edgeRatioX/Y/Z` define the explicit multiplicative reconstruction ratios.
- `edgeRatio*_eq_one_iff` prove that ratio one is exactly the ordered
  two-half-link reconstruction equation.
- `straightCompatible*_iff_ratios_one` lift that equivalence to the global
  directional contracts.

## 5. Independent curvature/gluing budget

- `curvatureBudget` is the five-face cubical path-swap budget selected in
  Block 28.
- `norm_cubeSwapDefect_le_curvatureBudget` reuses the exact phase-path theorem.
- `norm_twoStageDefect_le` proves the general two-stage identity and norm bound.
- `norm_straightSeven_then_gluing_le` combines the actual state-space straight
  walk with an independently controlled gluing stage.
- `combinedFiberFine`, `combinedFiberCoarse`, and
  `norm_combinedFiberDefect_le` provide a concrete local-fiber realization.
- `combinedFiberDefect_eq_zero` separates the exact edge-compatible and flat
  path-independent sector.

## 6. Summable global bridge

- `combinedScaleBudget` adds scale-dependent edge and curvature budgets.
- `summable_combinedScaleBudget` proves that separate summability implies
  summability of the combined budget.
- `twoBudgetSummableDefect`, `tendsto_twoBudgetLimit`, and
  `dist_twoBudgetLimit_le_tail` instantiate the checked Block 24 metric-limit
  architecture.

## Boundary

Block 30 does not derive a scalar estimate of each straight operator norm from
`sup |E_i-1|`, and it does not prove a geometric scale law.  The summability
hypotheses are explicit inputs.  Continuum Dirac convergence and dynamical
field equations remain open layers.
