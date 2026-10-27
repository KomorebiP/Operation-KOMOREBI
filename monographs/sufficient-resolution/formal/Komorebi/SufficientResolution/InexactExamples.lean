import Komorebi.SufficientResolution.InexactToleranceCertificates
import Komorebi.SufficientResolution.TikhonovExamples

/-!
# Sharp tolerances, actual nonexact certificates, and false-success controls

The fixed zero operator shows why a vanishing raw normal residual cannot replace
its source-correction scale. Scalar identity examples attain the data correction
bound and show the need for solver and measurement margins separately.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.InexactExamples

open TikhonovConstruction TikhonovExamples InexactResidual InexactDiscrepancy
open InexactToleranceCertificates DiscrepancyResidual
open Filter Topology

 theorem scalar_normal_residual (c lam v x : ℝ) :
    normalResidual (scalar c) lam v x = (c^2+lam)*x-c*v := by
  rw [normalResidual, normal_apply, scalar_adjoint_apply, scalar_apply,
    scalar_adjoint_apply]
  simp only [smul_eq_mul]
  ring

 theorem identity_image_bound_sharp (v x : ℝ) :
    ‖scalar 1 x-scalar 1 (regularized (scalar 1) 1 (by norm_num) v)‖ =
      ‖normalResidual (scalar 1) 1 v x‖/(2*Real.sqrt 1) := by
  rw [scalar_regularized, scalar_normal_residual, scalar_apply, scalar_apply]
  norm_num only [one_pow, one_mul, Real.sqrt_one, mul_one]
  have he : 2*x-v = 2*(x-v/2) := by ring
  rw [he, Real.norm_eq_abs, Real.norm_eq_abs, abs_mul]
  norm_num

 theorem zero_source_bound_sharp (lam : ℝ) (hl : 0 < lam) (v x : ℝ) :
    ‖x-regularized (scalar 0) lam hl v‖ =
      ‖normalResidual (scalar 0) lam v x‖/lam := by
  rw [zero_forward_regularized, scalar_normal_residual]
  simp only [zero_pow (by decide : (2:ℕ) ≠ 0), zero_add, zero_mul, sub_zero,
    Real.norm_eq_abs, abs_mul, abs_of_pos hl]
  field_simp

 theorem zero_bad_source (s : ℝ) (hs : 0 < s) :
    ‖normalResidual (scalar 0) s s 1‖ = s ∧
    ‖scalar 0 1-s‖ = s ∧
    ‖scalar 0 0-s‖ = s ∧
    regularized (scalar 0) s hs s = 0 ∧
    ‖(1:ℝ)-regularized (scalar 0) s hs s‖ = 1 := by
  rw [scalar_normal_residual, zero_forward_regularized]
  norm_num [scalar_apply, Real.norm_eq_abs, abs_of_pos hs, abs_of_neg (neg_neg_of_pos hs)]

 theorem arbitrarily_small_uncertified_residuals (tol : ℝ) (ht : 0 < tol) :
    ∃ s : ℝ, ∃ hs : 0 < s,
      ‖normalResidual (scalar 0) s s 1‖ < tol ∧
      ‖scalar 0 1-s‖ = s ∧ ‖scalar 0 0-s‖ = s ∧
      ‖(1:ℝ)-regularized (scalar 0) s hs s‖ = 1 := by
  have hs : 0 < tol/2 := by positivity
  obtain ⟨hn,hf,he,_,hx⟩ := zero_bad_source (tol/2) hs
  exact ⟨tol/2,hs,by rw [hn]; linarith,hf,he,hx⟩

 theorem small_raw_residuals_do_not_force_convergence {ι : Type*}
    (f : Filter ι) [NeBot f] (s : ι → ℝ) (hs : ∀ i, 0 < s i)
    (hlim : Tendsto s f (𝓝 0)) :
    Tendsto (fun i => ‖normalResidual (scalar 0) (s i) (s i) 1‖) f (𝓝 0) ∧
    Tendsto (fun i => ‖scalar 0 1-s i‖) f (𝓝 0) ∧
    ¬ Tendsto (fun _ : ι => (1:ℝ)) f (𝓝 0) := by
  refine ⟨?_,?_,?_⟩
  · simpa only [(zero_bad_source _ (hs _)).1] using hlim
  · simpa only [(zero_bad_source _ (hs _)).2.1] using hlim
  · intro h
    have he : (1:ℝ) = 0 := tendsto_nhds_unique (tendsto_const_nhds (x := (1:ℝ))) h
    norm_num at he

/-- A concrete certificate for a source that is NOT the exact minimizer. -/
def scalarCertificate : PositiveCertificate (scalar 1) 4 1 3 (1/50) (201/100) where
  lam := 1
  positive := by norm_num
  rho := 1/50
  xi := 1/100
  measured := 2
  omega := 1/100
  rho_nonneg := by norm_num
  xi_nonneg := by norm_num
  kappa_nonneg := by norm_num
  measured_nonneg := by norm_num
  omega_nonneg := by norm_num
  normal_squared := by norm_num [scalar_normal_residual, Real.norm_eq_abs]
  source_squared := by norm_num
  image_squared := by norm_num
  measured_lower_squared := by norm_num [scalar_apply, Real.norm_eq_abs]
  measured_upper_squared := by norm_num [scalar_apply, Real.norm_eq_abs]
  protected_lower := by norm_num
  protected_upper := by norm_num

 theorem certified_nonexact_source :
    NearAccepted (scalar 1) 4 1 3 (1/50) (201/100) ∧
      (201/100:ℝ) ≠ regularized (scalar 1) 1 (by norm_num) 4 := by
  refine ⟨certificate_sound (scalar 1) 4 1 3 (1/50) (201/100) scalarCertificate, ?_⟩
  rw [scalar_regularized]
  norm_num

 theorem solver_margin_cannot_be_dropped :
    (1/4:ℝ) ≤ ‖scalar 1 (3/2)-2‖ ∧
    ‖scalar 1 (3/2)-2‖ ≤ 3*(1/4:ℝ) ∧
    3*(1/4:ℝ) < residual (scalar 1) 2 1 := by
  rw [DiscrepancyResidual.residual, recoveryAt_pos (scalar 1) 1 (by norm_num),
    scalar_regularized]
  norm_num [scalar_apply, Real.norm_eq_abs]

 theorem measurement_margin_cannot_be_dropped :
    |(1/2:ℝ)-residual (scalar 1) 2 1| ≤ (1/2:ℝ) ∧
    (1/4:ℝ) ≤ (1/2:ℝ) ∧ (1/2:ℝ) ≤ 3*(1/4:ℝ) ∧
    3*(1/4:ℝ) < residual (scalar 1) 2 1 := by
  rw [DiscrepancyResidual.residual, recoveryAt_pos (scalar 1) 1 (by norm_num),
    scalar_regularized]
  norm_num [scalar_apply, Real.norm_eq_abs]

 theorem excessive_budget_has_no_protected_measurement :
    ¬ ∃ m : ℝ, 1+(2/5:ℝ)+1/5 ≤ m ∧ m ≤ 2*1-(2/5:ℝ)-1/5 := by
  rw [protected_window_exists_iff]
  norm_num

end Komorebi.SufficientResolution.InexactExamples
