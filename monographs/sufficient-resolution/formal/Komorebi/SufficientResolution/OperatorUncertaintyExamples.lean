import Komorebi.SufficientResolution.OperatorCertificates
import Komorebi.SufficientResolution.OperatorResidualTransport
import Komorebi.SufficientResolution.InexactExamples

/-!
# Actual certificates and sharp uncertainty boundaries

Examples use the constructed Tikhonov solution and actual Hilbert norms.
A biased model can pass exact discrepancy tests while approaching the wrong
source. This does not satisfy the vanishing operator-uncertainty hypothesis.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.OperatorUncertaintyExamples

open OperatorUncertainty OperatorCertificates InexactToleranceCertificates
open TikhonovConstruction TikhonovExamples InexactExamples DiscrepancyRule
open DiscrepancyResidual
open Filter Topology

 theorem scalar_difference (a c : ℝ) : scalar c-scalar a = scalar (c-a) := by
  apply ContinuousLinearMap.ext
  intro x
  simp only [sub_apply, scalar_apply]
  ring

 theorem scalar_operator_norm (c : ℝ) : ‖scalar c‖ = |c| := by
  simp [scalar, norm_smul, Real.norm_eq_abs]

 theorem scalar_operator_error (a c : ℝ) : ‖scalar c-scalar a‖ = |c-a| := by
  rw [scalar_difference, scalar_operator_norm]

 theorem inflated_noise_sharp (eta delta M : ℝ)
    (he : 0 ≤ eta) (hd : 0 ≤ delta) (hM : 0 ≤ M) :
    ‖scalar (1+delta) M-(M-eta)‖ = effectiveNoise eta delta M := by
  rw [scalar_apply]
  have h : (1+delta)*M-(M-eta) = effectiveNoise eta delta M := by
    simp only [effectiveNoise]; ring
  rw [h, Real.norm_eq_abs, abs_of_nonneg (effective_nonneg eta delta M he hd hM)]

 theorem operator_error_needs_source_size (delta bound : ℝ) (hd : 0 < delta) :
    ∃ g : ℝ, ‖scalar (1+delta) g-scalar 1 g‖ > bound := by
  refine ⟨(|bound|+1)/delta, ?_⟩
  have he : scalar (1+delta) ((|bound|+1)/delta)-scalar 1 ((|bound|+1)/delta) =
      |bound|+1 := by rw [scalar_apply, scalar_apply]; field_simp; ring
  rw [he, Real.norm_eq_abs, abs_of_pos (by positivity)]
  linarith [le_abs_self bound]

/-- Nonzero model uncertainty and a genuinely nonexact source, checked with squares. -/
def modelCertificate : PositiveCertificate (scalar 1) (22/5) (1/2) 3 (1/25) (331/100) where
  lam := 1/3
  positive := by norm_num
  rho := 1/75
  xi := 1/50
  measured := 11/10
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

 theorem actual_uncertain_certificate :
    Certified (scalar 1) (22/5) (1/10) (1/10) 4 3 (1/25) (331/100) := by
  apply Or.inr
  convert Nonempty.intro modelCertificate using 1
  norm_num [effectiveNoise]

 theorem example_true_allowances :
    ‖scalar 1-scalar (11/10)‖ ≤ (1/10:ℝ) ∧
    ‖scalar (11/10) 4-(22/5:ℝ)‖ ≤ (1/10:ℝ) ∧ ‖(4:ℝ)‖ ≤ 4 := by
  norm_num [scalar_operator_error, scalar_apply, Real.norm_eq_abs]

 theorem example_not_exact :
    (331/100:ℝ) ≠ regularized (scalar 1) (1/3) (by norm_num) (22/5) := by
  rw [scalar_regularized]; norm_num

 theorem biased_model_accepted (s : ℝ) (hs : 0 < s) (hu : s < 1) :
    Accepted (scalar 2) 1 s 2 ((1-s)/2) := by
  have hl : 0 < 4*s/(1-s) := div_pos (by positivity) (by linarith)
  have hx : regularized (scalar 2) (4*s/(1-s)) hl 1 = (1-s)/2 := by
    rw [scalar_regularized]
    have hden : 1-s ≠ 0 := by linarith
    field_simp
    ring
  apply Or.inr
  refine ⟨4*s/(1-s), hl, hx.symm, ?_, ?_⟩
  all_goals
    rw [DiscrepancyResidual.residual, recoveryAt_pos _ _ hl, hx, scalar_apply]
    have he : (2:ℝ)*((1-s)/2)-1 = -s := by ring
    simp only [he, norm_neg, Real.norm_eq_abs, abs_of_pos hs]
    linarith

 theorem biased_model_wrong_limit {ι : Type*} (f : Filter ι) [NeBot f]
    (s : ι → ℝ) (hs : ∀ i, 0 < s i) (hu : ∀ i, s i < 1)
    (hlim : Tendsto s f (𝓝 0)) :
    (∀ i, Accepted (scalar 2) 1 (s i) 2 ((1-s i)/2)) ∧
      Tendsto (fun i => (1-s i)/2) f (𝓝 (1/2:ℝ)) ∧
      ¬ Tendsto (fun i => (1-s i)/2) f (𝓝 (1:ℝ)) := by
  have h : Tendsto (fun i => (1-s i)/2) f (𝓝 (1/2:ℝ)) := by
    simpa only [sub_zero] using ((tendsto_const_nhds (x := (1:ℝ))).sub hlim).div_const 2
  refine ⟨fun i => biased_model_accepted (s i) (hs i) (hu i), h, ?_⟩
  intro hbad
  have he := tendsto_nhds_unique h hbad
  norm_num at he

 theorem zero_data_rule_with_changing_kernel (s : ℝ) (hs : s ≠ 0) :
    (scalar s).ker = ⊥ ∧ (scalar 0).ker = ⊤ ∧
      Accepted (scalar s) 0 1 2 0 := by
  refine ⟨?_, ?_, Or.inl ⟨by norm_num, rfl⟩⟩
  · ext x
    simp [LinearMap.mem_ker, scalar_apply, mul_eq_zero, hs]
  · ext x
    simp [LinearMap.mem_ker, scalar_apply]

end Komorebi.SufficientResolution.OperatorUncertaintyExamples
