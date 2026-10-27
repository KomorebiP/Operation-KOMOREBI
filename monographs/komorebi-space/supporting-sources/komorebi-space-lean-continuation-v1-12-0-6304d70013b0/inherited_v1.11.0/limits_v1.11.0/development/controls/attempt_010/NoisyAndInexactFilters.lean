import KomorebiSpace.RegularizationNoiseLimits

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

section
variable {H Y I : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable (T : H →L[ℝ] Y) (r : Y) (s : I → Y) (a : I → H) (aMin : H)
variable (l : Filter I) (α δ ε : I → ℝ)

-- The transfer theorem works along arbitrary filters, including nets. Both
-- data and solver budgets refer to the same measured datum and fixed operator.
example
    (hα : ∀ᶠ i in l, 0 < α i)
    (hdata : ∀ᶠ i in l, ‖s i-r‖ ≤ δ i)
    (hsolver : ∀ᶠ i in l, ‖RegularizedHilbertRepair.gradient T (α i) (s i) (a i)‖ ≤ ε i)
    (hnoise : Tendsto (fun i => δ i / Real.sqrt (α i)) l (𝓝 0))
    (hsolve : Tendsto (fun i => ε i / α i) l (𝓝 0))
    (hbias : Tendsto (fun i => RegularizationLimits.path T r (α i)) l (𝓝 aMin)) :
    Tendsto (fun i => RegularizationLimits.path T (s i) (α i)) l (𝓝 aMin) ∧
    Tendsto a l (𝓝 aMin) := by
  exact ⟨RegularizationNoiseLimits.noisy_tendsto_of_exact_tendsto T r s aMin α δ
      hα hdata hnoise hbias,
    RegularizationNoiseLimits.inexact_tendsto_of_exact_tendsto T r s a aMin α δ ε
      hα hdata hsolver hnoise hsolve hbias⟩
end

-- The finite-index certificate explicitly retains all three contributions.
example {H Y : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r s : Y) (a aMin : H) (α δ ε : ℝ)
    (hα : 0 < α) (hdata : ‖s-r‖ ≤ δ)
    (hsolver : ‖RegularizedHilbertRepair.gradient T α s a‖ ≤ ε) :
    ‖a-aMin‖ ≤ ε/α + δ/(2*Real.sqrt α) +
      ‖RegularizationLimits.path T r α-aMin‖ := by
  exact RegularizationNoiseLimits.stopping_three_term_bound T r s a aMin hα hdata hsolver
