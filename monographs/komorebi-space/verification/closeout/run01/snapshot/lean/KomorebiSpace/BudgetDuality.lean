import KomorebiSpace.BudgetProfile
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.InnerProductSpace.Projection.Minimal
import Mathlib.Topology.MetricSpace.HausdorffDistance
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

set_option autoImplicit false

noncomputable section
universe u v
namespace KomorebiSpace.BudgetDuality
open scoped RealInnerProductSpace
variable {H : Type u} {Y : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Every admissible dual vector bounds every candidate in the fixed correction ball. -/
theorem dualValue_le_residual (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    {a : H} (ha : ‖a‖ ≤ M) {z : Y} (hz : ‖z‖ ≤ 1) :
    ⟪r, z⟫ - M * ‖T.adjoint z‖ ≤ ‖r - T a‖ := by
  have hres : ⟪r - T a, z⟫ ≤ ‖r - T a‖ := calc
    _ ≤ ‖r - T a‖ * ‖z‖ := real_inner_le_norm _ _
    _ ≤ ‖r - T a‖ * 1 := mul_le_mul_of_nonneg_left hz (norm_nonneg _)
    _ = ‖r - T a‖ := mul_one _
  have himage : ⟪T a, z⟫ ≤ M * ‖T.adjoint z‖ := calc
    _ = ⟪a, T.adjoint z⟫ := (ContinuousLinearMap.adjoint_inner_right T a z).symm
    _ ≤ ‖a‖ * ‖T.adjoint z‖ := real_inner_le_norm _ _
    _ ≤ M * ‖T.adjoint z‖ := mul_le_mul_of_nonneg_right ha (norm_nonneg _)
  rw [inner_sub_left] at hres
  linarith

omit [CompleteSpace H] in
/-- If a feasible point maximizes a linear pairing on a ball, it attains its exact support value.
The proof includes zero radius and zero supporting vector. -/
theorem ball_support_eq {M : ℝ} (hM : 0 ≤ M) (g a : H) (ha : ‖a‖ ≤ M)
    (hmax : ∀ b : H, ‖b‖ ≤ M → ⟪b, g⟫ ≤ ⟪a, g⟫) :
    ⟪a, g⟫ = M * ‖g‖ := by
  by_cases hg : g = 0
  · simp [hg]
  have hgpos : 0 < ‖g‖ := norm_pos_iff.mpr hg
  have hgn : ‖g‖ ≠ 0 := ne_of_gt hgpos
  have hn : ‖(M / ‖g‖) • g‖ = M := by
    rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg (div_nonneg hM hgpos.le)]
    exact div_mul_cancel₀ M hgn
  have hi : ⟪(M / ‖g‖) • g, g⟫ = M * ‖g‖ := by
    rw [real_inner_smul_left, real_inner_self_eq_norm_sq]
    field_simp
  apply le_antisymm
  · exact (real_inner_le_norm a g).trans
      (mul_le_mul_of_nonneg_right ha (norm_nonneg _))
  · simpa only [hi] using hmax ((M / ‖g‖) • g) hn.le

/-- A variationally minimizing residual gives an attaining dual vector.
This helper isolates the elementary support calculation from existence of a minimizer. -/
theorem exists_sharp_witness_of_variational (T : H →L[ℝ] Y) (r : Y)
    {M : ℝ} (hM : 0 ≤ M) (a : H) (ha : ‖a‖ ≤ M)
    (hvar : ∀ b : H, ‖b‖ ≤ M → ⟪r - T a, T b - T a⟫ ≤ 0) :
    ∃ z : Y, ‖z‖ ≤ 1 ∧ ⟪r, z⟫ - M * ‖T.adjoint z‖ = ‖r - T a‖ := by
  by_cases hv : r - T a = 0
  · refine ⟨0, by simp, ?_⟩
    simp [hv]
  have hvpos : 0 < ‖r - T a‖ := norm_pos_iff.mpr hv
  have hvn : ‖r - T a‖ ≠ 0 := ne_of_gt hvpos
  let z : Y := ‖r - T a‖⁻¹ • (r - T a)
  have hz : ‖z‖ = 1 := by
    dsimp [z]
    rw [norm_smul, Real.norm_eq_abs, abs_of_pos (inv_pos.mpr hvpos), inv_mul_cancel₀ hvn]
  have hmax : ∀ b : H, ‖b‖ ≤ M → ⟪b, T.adjoint z⟫ ≤ ⟪a, T.adjoint z⟫ := by
    intro b hb
    have hi := hvar b hb
    rw [inner_sub_right] at hi
    rw [ContinuousLinearMap.adjoint_inner_right, ContinuousLinearMap.adjoint_inner_right]
    dsimp [z]
    rw [real_inner_smul_right, real_inner_smul_right]
    have hi' : ⟪T b, r - T a⟫ ≤ ⟪T a, r - T a⟫ := by
      simpa only [real_inner_comm] using sub_nonpos.mp hi
    exact mul_le_mul_of_nonneg_left hi' (inv_nonneg.mpr hvpos.le)
  have hs := ball_support_eq hM (T.adjoint z) a ha hmax
  have hir : ⟪r - T a, z⟫ = ‖r - T a‖ := by
    dsimp [z]
    rw [real_inner_smul_right, real_inner_self_eq_norm_sq]
    field_simp
  refine ⟨z, hz.le, ?_⟩
  rw [← hs, ContinuousLinearMap.adjoint_inner_right, ← inner_sub_left]
  exact hir

/-- The universal dual bound at every nonnegative budget. -/
theorem dualValue_le_beta (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    (hM : 0 ≤ M) {z : Y} (hz : ‖z‖ ≤ 1) :
    ⟪r, z⟫ - M * ‖T.adjoint z‖ ≤ BudgetProfile.beta T r M := by
  obtain ⟨a, ha, heq⟩ := BudgetProfile.exists_budget_minimizer T r hM
  exact (dualValue_le_residual T r ha hz).trans_eq heq

omit [CompleteSpace H] [CompleteSpace Y] in
/-- The fixed-budget minimizer satisfies the full convex variational inequality. -/
theorem minimizer_variational (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    (a : H) (ha : ‖a‖ ≤ M) (hmin : ‖r - T a‖ = BudgetProfile.beta T r M) :
    ∀ b : H, ‖b‖ ≤ M → ⟪r - T a, T b - T a⟫ ≤ 0 := by
  have ha' : T a ∈ T '' Metric.closedBall 0 M :=
    ⟨a, by simpa only [Metric.mem_closedBall, dist_zero_right] using ha, rfl⟩
  have hmin' : ‖r - T a‖ = ⨅ w : (T '' Metric.closedBall 0 M), ‖r - w‖ := by
    simpa only [BudgetProfile.beta, Metric.infDist_eq_iInf, dist_eq_norm] using hmin
  have hv := (norm_eq_iInf_iff_real_inner_le_zero
    (BudgetProfile.convex_budget_image T M) ha').mp hmin'
  intro b hb
  exact hv (T b) ⟨b, by simpa only [Metric.mem_closedBall, dist_zero_right] using hb, rfl⟩

/-- WR04 sharpness: a witness in the closed unit ball attains the exact budget profile.
No closed-range, finite-dimensionality, positive-budget, or nonzero-residual assumption is needed. -/
theorem exists_attaining_dual_witness (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    (hM : 0 ≤ M) : ∃ z : Y, ‖z‖ ≤ 1 ∧
    ⟪r, z⟫ - M * ‖T.adjoint z‖ = BudgetProfile.beta T r M := by
  obtain ⟨a, ha, heq⟩ := BudgetProfile.exists_budget_minimizer T r hM
  obtain ⟨z, hz, hvalue⟩ := exists_sharp_witness_of_variational T r hM a ha
    (minimizer_variational T r a ha heq)
  exact ⟨z, hz, hvalue.trans heq⟩

/-- WR04 as a literal maximum, combining existence with the universal upper bound. -/
theorem sharp_budget_duality (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    (hM : 0 ≤ M) :
    IsGreatest ((fun z : Y => ⟪r, z⟫ - M * ‖T.adjoint z‖) ''
      Metric.closedBall (0 : Y) 1) (BudgetProfile.beta T r M) := by
  obtain ⟨z, hz, heq⟩ := exists_attaining_dual_witness T r hM
  constructor
  · exact ⟨z, by simpa only [Metric.mem_closedBall, dist_zero_right] using hz, heq⟩
  · rintro _ ⟨w, hw, rfl⟩
    exact dualValue_le_beta T r hM (by
      simpa only [Metric.mem_closedBall, dist_zero_right] using hw)

/-- Any witness above epsilon excludes every correction with that budget and residual tolerance. -/
theorem strict_exclusion_certificate (T : H →L[ℝ] Y) (r : Y) {M ε : ℝ}
    {z : Y} (hz : ‖z‖ ≤ 1) (hcert : ε < ⟪r, z⟫ - M * ‖T.adjoint z‖) :
    ¬ ∃ a : H, ‖a‖ ≤ M ∧ ‖r - T a‖ ≤ ε := by
  rintro ⟨a, ha, hres⟩
  exact (not_lt_of_ge ((dualValue_le_residual T r ha hz).trans hres)) hcert

end KomorebiSpace.BudgetDuality
