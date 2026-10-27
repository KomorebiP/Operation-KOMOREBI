import KomorebiSpace.DiagonalNoisyRate

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization

/-- The displayed infinite vector is the unique global regularized minimizer. -/
theorem a_unique_minimizer {m : ℕ} (hm : 1 ≤ m) :
    (∀ x : H, RegularizedHilbertRepair.objective T (alpha m) w (a m) ≤
      RegularizedHilbertRepair.objective T (alpha m) w x) ∧
    (∀ x : H, (∀ y : H, RegularizedHilbertRepair.objective T (alpha m) w x ≤
      RegularizedHilbertRepair.objective T (alpha m) w y) → x = a m) := by
  constructor
  · intro x
    rw [a_eq_correction hm]
    exact RegularizedHilbertRepair.correction_best T (alpha m) (alpha_pos hm) w x
  · intro x hx
    rw [a_eq_correction hm]
    exact RegularizedHilbertRepair.correction_unique T (alpha m) (alpha_pos hm) w x (hx _)

/-- Proposition 30.1, with all infinite-model and quantitative obligations combined.
The coordinate formulas are the definitions identified by `a_apply` and `v_apply`.
Membership in the actual Hilbert space is part of the types of `a m` and `v m`. -/
theorem proposition_30_1 (m K : ℕ) (hm : 1 ≤ m) (hmK : m ≤ K) :
    a m = RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) w ∧
    w - T (a m) = v m ∧
    ‖a m‖ ^ 2 = A m ∧ ‖v m‖ ^ 2 = B m ∧
    (m : ℝ) / 4 ≤ A m ∧ A m ≤ 4 * (m : ℝ) / 3 ∧
    1 / (4 * ((m : ℝ) + 1)) ≤ B m ∧ B m ≤ 2 / (m : ℝ) ∧
    0 ≤ A m - partialA m K ∧ A m - partialA m K ≤ (m : ℝ)^4 / (3 * (K : ℝ)^3) ∧
    0 ≤ B m - partialB m K ∧ B m - partialB m K ≤ 1 / (K : ℝ) := by
  exact ⟨a_eq_correction hm, residual_eq_v m, norm_a_sq m, norm_v_sq m,
    proposition_30_1_series m K hm hmK⟩

end KomorebiSpace.DiagonalRegularization
