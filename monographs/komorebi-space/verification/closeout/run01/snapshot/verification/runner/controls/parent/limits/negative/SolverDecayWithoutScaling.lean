import KomorebiSpace.RegularizationNoiseLimits

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- Deliberately invalid use of unscaled normal-residual decay as the required
-- correction-error decay. Vanishing ε alone does not control ε/α.
example {H Y I : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y) (s : I → Y) (a : I → H) (aMin : H)
    (l : Filter I) (α δ ε : I → ℝ) (hα : ∀ᶠ i in l, 0 < α i)
    (hdata : ∀ᶠ i in l, ‖s i-r‖ ≤ δ i)
    (hsolver : ∀ᶠ i in l, ‖RegularizedHilbertRepair.gradient T (α i) (s i) (a i)‖ ≤ ε i)
    (hnoise : Tendsto (fun i => δ i / Real.sqrt (α i)) l (𝓝 0))
    (hsolve : Tendsto ε l (𝓝 0))
    (hbias : Tendsto (fun i => RegularizationLimits.path T r (α i)) l (𝓝 aMin)) :
    Tendsto a l (𝓝 aMin) := by
  exact RegularizationNoiseLimits.inexact_tendsto_of_exact_tendsto T r s a aMin α δ ε
    hα hdata hsolver hnoise hsolve hbias
