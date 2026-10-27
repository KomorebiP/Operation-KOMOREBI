import KomorebiSpace.RegularizationNoiseLimits

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- Deliberately invalid use of unscaled data-error decay as the required
-- propagated-noise decay. Vanishing δ alone does not control δ/√α.
example {H Y I : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y) (s : I → Y) (aMin : H)
    (l : Filter I) (α δ : I → ℝ) (hα : ∀ᶠ i in l, 0 < α i)
    (hdata : ∀ᶠ i in l, ‖s i-r‖ ≤ δ i)
    (hnoise : Tendsto δ l (𝓝 0))
    (hbias : Tendsto (fun i => RegularizationLimits.path T r (α i)) l (𝓝 aMin)) :
    Tendsto (fun i => RegularizationLimits.path T (s i) (α i)) l (𝓝 aMin) := by
  exact RegularizationNoiseLimits.noisy_tendsto_of_exact_tendsto T r s aMin α δ
    hα hdata hnoise hbias
