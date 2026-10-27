import Komorebi.GeneratedRichardsonScalar

set_option autoImplicit false
set_option maxRecDepth 16384
namespace Komorebi.ExactPosterior.RichardsonBoundaryChecks
open Komorebi.ExactPosterior Komorebi.GainSolver Komorebi.PacketEnergy
open GeneratedRichardsonScalar

/-- The exact fixed point is recognized without taking an update. -/
theorem initially_exact_returns :
    solveGain model outputs inputs (1/20) !![1/2] =
      some (exactCandidate model outputs inputs !![1/2]) := by decide +kernel

/-- Zero tolerance is not covered by the finite positive-tolerance theorem. -/
theorem zero_tolerance_no_spurious_success :
    solveGain model outputs inputs 0 initial = none := by decide +kernel

/-- Invalid positive-floor data cannot acquire a posterior certificate. -/
theorem zero_floor_rejected :
    solveGain {model with noiseFloor := 0} outputs inputs (1/20) initial = none := by decide +kernel

/-- An arbitrary oversized step can increase energy: step certification is necessary. -/
theorem oversized_step_counterexample :
    rationalEnergy ((!![1] : Matrix (Fin 1) (Fin 1) ℚ) -
      gainStep !![1] !![2] 2 !![0] * !![2]) = 9 := by decide +kernel

/-- The collapsed spectral interval (rho=0) gives exact zero residual after one step. -/
theorem collapsed_spectrum_one_step {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq κ]
    (S : Matrix κ κ ℝ) (hS : S.IsHermitian) (σ : ℝ) (hs : 0 < σ)
    (hl : ∀ i, σ ≤ hS.eigenvalues i) (hu : ∀ i, hS.eigenvalues i ≤ σ)
    (F : Matrix ι κ ℝ) : F*(1-σ⁻¹ • S) = 0 := by
  apply (matrixEnergy_eq_zero_iff _).mp
  have h := richardson_matrix_energy_contract S hS σ σ hs hl hu F
  have hn := matrixEnergy_nonneg (F*(1-σ⁻¹ • S))
  have hz : (1-σ/σ)^2 * matrixEnergy F = 0 := by
    rw [div_self (ne_of_gt hs)]
    ring
  rw [hz] at h
  exact le_antisymm h hn
end Komorebi.ExactPosterior.RichardsonBoundaryChecks
