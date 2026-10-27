import KomorebiVerification.PaperII.ReleaseCycleParameter
import Mathlib.Analysis.Complex.Liouville

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseCycleDecay
open Set Filter
open scoped Topology
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleParameter

theorem norm_gt_mem_cocompact (R : ℝ) :
    {w : ℂ | R < ‖w‖} ∈ Filter.cocompact ℂ :=
  Filter.mem_cocompact.mpr ⟨Metric.closedBall 0 R, isCompact_closedBall 0 R,
    fun _ hw => by simpa using hw⟩

/-- A reciprocal norm bound implies convergence to zero in a normed target. -/
theorem tendsto_zero_of_norm_bound
    {E : Type*} [NormedAddCommGroup E] {g : ℂ → E} {R C : ℝ}
    (hbound : ∀ w, R < ‖w‖ → ‖g w‖ ≤ C / (‖w‖ - R)) :
    Tendsto g (Filter.cocompact ℂ) (𝓝 0) := by
  rw [Metric.tendsto_nhds]
  intro ε hε
  simp only [dist_zero_right]
  filter_upwards [norm_gt_mem_cocompact (max R (R + C / ε))] with w hw
  have hRw : R < ‖w‖ := lt_of_le_of_lt (le_max_left _ _) hw
  calc
    ‖g w‖ ≤ C / (‖w‖ - R) := hbound w hRw
    _ < ε := by
      rw [div_lt_iff₀ (sub_pos.mpr hRw)]
      have h2 : C / ε < ‖w‖ - R := by
        linarith [lt_of_le_of_lt (le_max_right _ _) hw]
      rw [div_lt_iff₀ hε] at h2
      linarith [mul_comm ε (‖w‖ - R)]

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
  [NormedSpace ℝ E]

/-- The concrete reciprocal estimate for the actual finite-cycle transform. -/
theorem norm_cauchyTransform_le (Γ : IntegralCycle) {f : ℂ → E} (R M : ℝ)
    (_hM : 0 ≤ M) (hR : ∀ z ∈ Γ.trace, ‖z‖ ≤ R)
    (hf : ∀ z ∈ Γ.trace, ‖f z‖ ≤ M) {w : ℂ} (hw : R < ‖w‖) :
    ‖Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)‖ ≤
      Γ.length * ((‖w‖-R)⁻¹ * M) := by
  apply Γ.norm_lineIntegral_le
  intro z hz
  rw [norm_smul, norm_inv]
  apply mul_le_mul
  · apply inv_anti₀ (sub_pos.mpr hw)
    have htri := norm_sub_norm_le w z
    rw [norm_sub_rev] at htri
    linarith [hR z hz]
  · exact hf z hz
  · exact norm_nonneg _
  · positivity

/-- Decay of the Banach-valued Cauchy transform of a finite cycle. -/
theorem dixonH2_tendsto_zero_of_bounds (Γ : IntegralCycle) {f : ℂ → E}
    {R M : ℝ} (hM : 0 ≤ M) (hR : ∀ z ∈ Γ.trace, ‖z‖ ≤ R)
    (hf : ∀ z ∈ Γ.trace, ‖f z‖ ≤ M) :
    Tendsto (fun w => Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)) (Filter.cocompact ℂ) (𝓝 0) := by
  apply tendsto_zero_of_norm_bound (R := R) (C := Γ.length * M)
  intro w hw
  calc
    ‖Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)‖ ≤ Γ.length * ((‖w‖ - R)⁻¹ * M) :=
      norm_cauchyTransform_le Γ R M hM hR hf hw
    _ = Γ.length * M / (‖w‖ - R) := by ring

/-- Continuous densities need no additional bound hypotheses: compactness of the
actual cycle trace supplies both bounds used in the decay estimate. -/
theorem dixonH2_tendsto_zero (Γ : IntegralCycle) {f : ℂ → E}
    (hf : ContinuousOn f Γ.trace) :
    Tendsto (fun w => Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)) (Filter.cocompact ℂ) (𝓝 0) := by
  obtain ⟨R, hR⟩ := (isCompact_trace Γ).bddAbove_image continuousOn_id.norm
  obtain ⟨M, hM⟩ := (isCompact_trace Γ).bddAbove_image hf.norm
  exact dixonH2_tendsto_zero_of_bounds Γ (R := R) (M := max M 0)
    (le_max_right _ _) (fun z hz => hR (mem_image_of_mem _ hz))
    (fun z hz => le_max_of_le_left (hM (mem_image_of_mem _ hz)))

end Komorebi.PaperII.ReleaseCycleDecay
