import Komorebi.SufficientResolution.DiscrepancyResidual

/-!
# Normal-equation residuals and reliable discrepancy measurements

The source correction costs 1/lambda; its image costs only 1/(2 sqrt lambda).
All residuals below are formed from the actual bounded Hilbert operator.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.InexactResidual

open TikhonovConstruction TikhonovBounds DiscrepancyResidual

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- Actual normal-equation residual of a possibly inexact source. -/
def normalResidual (lam : ℝ) (v : V) (x : G) : G :=
  normal A lam x - A.adjoint v

 theorem correction_identity (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    x - regularized A lam hl v = resolvent A lam hl (normalResidual A lam v x) :=
  approximate_solver_identity A lam hl v x

 theorem correction_bound (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    ‖x - regularized A lam hl v‖ ≤ ‖normalResidual A lam v x‖ / lam :=
  approximate_solver_bound A lam hl v x

 theorem correction_zero_iff (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    normalResidual A lam v x = 0 ↔ x = regularized A lam hl v := by
  rw [normalResidual, sub_eq_zero, normal_equation_iff A lam hl]

 theorem image_resolvent_bound_squared (lam : ℝ) (hl : 0 < lam) (r : G) :
    4 * lam * ‖A (resolvent A lam hl r)‖^2 ≤ ‖r‖^2 := by
  have he := normal_energy A lam (resolvent A lam hl r)
  rw [normal_resolvent] at he
  have hc := real_inner_le_norm r (resolvent A lam hl r)
  have hh : ‖A (resolvent A lam hl r)‖^2 +
      lam * ‖resolvent A lam hl r‖^2 ≤ ‖r‖ * ‖resolvent A lam hl r‖ := by
    linarith
  have hp := mul_le_mul_of_nonneg_left hh hl.le
  nlinarith [sq_nonneg (2 * lam * ‖resolvent A lam hl r‖ - ‖r‖)]

 theorem image_resolvent_bound (lam : ℝ) (hl : 0 < lam) (r : G) :
    ‖A (resolvent A lam hl r)‖ ≤ ‖r‖ / (2 * Real.sqrt lam) := by
  have hs := Real.sq_sqrt hl.le
  have hp : 0 < 2 * Real.sqrt lam := by positivity
  apply (le_div_iff₀ hp).mpr
  apply (sq_le_sq₀ (mul_nonneg (norm_nonneg _) hp.le) (norm_nonneg _)).mp
  calc
    (‖A (resolvent A lam hl r)‖ * (2 * Real.sqrt lam))^2 =
        4 * lam * ‖A (resolvent A lam hl r)‖^2 := by
      rw [mul_pow, mul_pow, hs]; ring
    _ ≤ ‖r‖^2 := image_resolvent_bound_squared A lam hl r

 theorem image_correction_identity (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    A x - A (regularized A lam hl v) =
      A (resolvent A lam hl (normalResidual A lam v x)) := by
  rw [← map_sub, correction_identity]

 theorem image_correction_bound (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    ‖A x - A (regularized A lam hl v)‖ ≤
      ‖normalResidual A lam v x‖ / (2 * Real.sqrt lam) := by
  rw [image_correction_identity]
  exact image_resolvent_bound A lam hl _

 theorem fitting_residual_difference (lam : ℝ) (hl : 0 < lam) (v : V) (x : G) :
    |‖A x - v‖ - residual A v lam| ≤
      ‖normalResidual A lam v x‖ / (2 * Real.sqrt lam) := by
  rw [DiscrepancyResidual.residual, recoveryAt_pos A lam hl]
  calc
    _ ≤ ‖(A x - v) - (A (regularized A lam hl v) - v)‖ := abs_norm_sub_norm_le _ _
    _ = ‖A x - A (regularized A lam hl v)‖ := by congr 1; abel
    _ ≤ _ := image_correction_bound A lam hl v x

 theorem certified_correction (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (kappa : ℝ) (hr : ‖normalResidual A lam v x‖ ≤ lam * kappa) :
    ‖x - regularized A lam hl v‖ ≤ kappa := by
  exact (correction_bound A lam hl v x).trans ((div_le_iff₀ hl).mpr (by nlinarith))

 theorem certified_image_correction (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (xi : ℝ) (hr : ‖normalResidual A lam v x‖ ≤ 2 * Real.sqrt lam * xi) :
    ‖A x - A (regularized A lam hl v)‖ ≤ xi := by
  have hp : 0 < 2 * Real.sqrt lam := by positivity
  exact (image_correction_bound A lam hl v x).trans ((div_le_iff₀ hp).mpr (by nlinarith))

 theorem certified_fitting_difference (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (xi : ℝ) (hr : ‖normalResidual A lam v x‖ ≤ 2 * Real.sqrt lam * xi) :
    |‖A x - v‖ - residual A v lam| ≤ xi := by
  have hp : 0 < 2 * Real.sqrt lam := by positivity
  exact (fitting_residual_difference A lam hl v x).trans
    ((div_le_iff₀ hp).mpr (by nlinarith))

 theorem measured_residual_difference (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (measured omega xi : ℝ)
    (hmeas : |measured - ‖A x - v‖| ≤ omega)
    (hr : ‖normalResidual A lam v x‖ ≤ 2 * Real.sqrt lam * xi) :
    |measured - residual A v lam| ≤ omega + xi := by
  calc
    _ = |(measured - ‖A x - v‖) + (‖A x - v‖ - residual A v lam)| := by congr 1; ring
    _ ≤ |measured - ‖A x - v‖| + |‖A x - v‖ - residual A v lam| := abs_add_le _ _
    _ ≤ omega + xi := add_le_add hmeas (certified_fitting_difference A lam hl v x xi hr)

 theorem measured_band_transfer (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (eta tau measured omega xi : ℝ)
    (hmeas : |measured - ‖A x - v‖| ≤ omega)
    (hr : ‖normalResidual A lam v x‖ ≤ 2 * Real.sqrt lam * xi)
    (hlo : eta + omega + xi ≤ measured)
    (hhi : measured ≤ tau * eta - omega - xi) :
    eta ≤ residual A v lam ∧ residual A v lam ≤ tau * eta := by
  obtain ⟨h1,h2⟩ := abs_le.mp (measured_residual_difference A lam hl v x measured omega xi hmeas hr)
  constructor <;> linarith

end Komorebi.SufficientResolution.InexactResidual
