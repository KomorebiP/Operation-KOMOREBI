import KomorebiSpace.BudgetProfile
import Mathlib.Analysis.InnerProductSpace.Adjoint

set_option autoImplicit false

noncomputable section
namespace KomorebiSpace.BudgetRobustness

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y]

/-- Perturbing both the datum and operator changes the residual at a fixed
candidate by at most the data error plus the model error times its norm. -/
theorem candidate_residual_difference_bound
    (T S : H →L[ℝ] Y) (r s : Y) {η δ : ℝ}
    (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ) (a : H) :
    ‖(r - T a) - (s - S a)‖ ≤ δ + η * ‖a‖ := by
  have hid : (r - T a) - (s - S a) = (r - s) - (T - S) a := by
    simp only [sub_apply]
    abel
  rw [hid]
  calc
    ‖(r - s) - (T - S) a‖ ≤ ‖r - s‖ + ‖(T - S) a‖ := norm_sub_le _ _
    _ ≤ δ + ‖T - S‖ * ‖a‖ := add_le_add hrs ((T - S).le_opNorm a)
    _ ≤ δ + η * ‖a‖ := add_le_add (le_refl δ)
      (mul_le_mul_of_nonneg_right hTS (norm_nonneg a))

/-- The reverse triangle inequality controls the change in the residual norm. -/
theorem candidate_residual_abs_bound
    (T S : H →L[ℝ] Y) (r s : Y) {η δ : ℝ}
    (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ) (a : H) :
    |‖r - T a‖ - ‖s - S a‖| ≤ δ + η * ‖a‖ := by
  exact (abs_norm_sub_norm_le _ _).trans
    (candidate_residual_difference_bound T S r s hTS hrs a)

/-- Candidate-level uncertainty certificate, before imposing any fixed budget. -/
theorem candidate_residual_le
    (T S : H →L[ℝ] Y) (r s : Y) {η δ : ℝ}
    (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ) (a : H) :
    ‖r - T a‖ ≤ ‖s - S a‖ + δ + η * ‖a‖ := by
  have h := (abs_le.mp (candidate_residual_abs_bound T S r s hTS hrs a)).2
  linarith

/-- One common feasible ball gives the uniform candidate error allowance. -/
theorem budget_candidate_residual_abs_bound
    (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ}
    (hη : 0 ≤ η) (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ)
    {a : H} (ha : ‖a‖ ≤ M) :
    |‖r - T a‖ - ‖s - S a‖| ≤ δ + η * M := by
  exact (candidate_residual_abs_bound T S r s hTS hrs a).trans
    (add_le_add (le_refl δ) (mul_le_mul_of_nonneg_left ha hη))

variable [CompleteSpace H] [CompleteSpace Y]

/-- Evaluate the first profile at a minimizer for the second, on the same ball. -/
theorem beta_le_beta_add_uncertainty
    (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ}
    (hM : 0 ≤ M) (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ) :
    BudgetProfile.beta T r M ≤ BudgetProfile.beta S s M + (δ + η * M) := by
  have hη : 0 ≤ η := (norm_nonneg (T - S)).trans hTS
  obtain ⟨a, ha, hamin⟩ := BudgetProfile.exists_budget_minimizer S s hM
  have h := (abs_le.mp
    (budget_candidate_residual_abs_bound T S r s hη hTS hrs ha)).2
  calc
    BudgetProfile.beta T r M ≤ ‖r - T a‖ := BudgetProfile.beta_le_residual T r ha
    _ ≤ ‖s - S a‖ + (δ + η * M) := by linarith
    _ = BudgetProfile.beta S s M + (δ + η * M) := by rw [hamin]

/-- WR05: fixed-budget profiles vary by at most the explicit model/data allowance.
The norm bounds already force η and δ to be nonnegative. The source, target,
and feasible correction ball are identical in the two problems. -/
theorem beta_abs_sub_le
    (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ}
    (hM : 0 ≤ M) (hTS : ‖T - S‖ ≤ η) (hrs : ‖r - s‖ ≤ δ) :
    |BudgetProfile.beta T r M - BudgetProfile.beta S s M| ≤ δ + η * M := by
  have hST : ‖S - T‖ ≤ η := by simpa only [norm_sub_rev] using hTS
  have hsr : ‖s - r‖ ≤ δ := by simpa only [norm_sub_rev] using hrs
  have h₁ := beta_le_beta_add_uncertainty T S r s hM hTS hrs
  have h₂ := beta_le_beta_add_uncertainty S T s r hM hST hsr
  exact abs_le.mpr ⟨by linarith, by linarith⟩

end KomorebiSpace.BudgetRobustness
