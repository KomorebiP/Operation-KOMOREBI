import KomorebiSpace.DiagonalNoisyRate

set_option autoImplicit false
noncomputable section

namespace KomorebiSpace.DiagonalRegularization

/-- An inexact solve retains the printed diagonal rate at the literal rounded
parameter. The normal residual is evaluated against the measured datum `s`.
Here `T`, `b`, and `w` belong to the actual infinite diagonal Hilbert model,
and `alpha m = ((m : ℝ)^2)⁻¹`. No exact-data bias hypothesis is assumed. -/
theorem diagonal_inexact_rounded_rate (s a : H) {δ κ ε : ℝ}
    (hδ : 0 < δ) (hδ₁ : δ ≤ 1) (hκ : 0 ≤ κ)
    (hdata : ‖s - b‖ ≤ δ)
    (hsolve : ‖T.adjoint (T a - s) +
      alpha (Nat.ceil (δ ^ (-(2 : ℝ) / 3))) • a‖ ≤ ε)
    (hε : ε ≤ κ * alpha (Nat.ceil (δ ^ (-(2 : ℝ) / 3))) *
      δ ^ ((1 : ℝ) / 3)) :
    ‖a - w‖ ≤ (Real.sqrt 2 + 1 + κ) * δ ^ ((1 : ℝ) / 3) := by
  let m := Nat.ceil (δ ^ (-(2 : ℝ) / 3))
  have hm : 1 ≤ m := one_le_noiseSchedule hδ
  have hα : 0 < alpha m := alpha_pos hm
  have hres : ‖RegularizedHilbertRepair.gradient T (alpha m) s a‖ ≤ ε := by
    have he : RegularizedHilbertRepair.gradient T (alpha m) s a =
        T.adjoint (T a - s) + alpha m • a := by
      simp only [RegularizedHilbertRepair.gradient,
        RegularizedHilbertRepair.normal_apply, map_sub]
      abel
    rw [he]
    exact hsolve
  have hbudget : 0 ≤ κ * δ ^ ((1 : ℝ) / 3) :=
    mul_nonneg hκ (Real.rpow_pos_of_pos hδ _).le
  have hsolver :
      ‖a - RegularizedHilbertRepair.correction T (alpha m) hα s‖ ≤
        κ * δ ^ ((1 : ℝ) / 3) := by
    refine (RegularizedHilbertRepair.correction_error_bound T (alpha m) hα s a).trans ?_
    apply (div_le_iff₀ hα).2
    have hr := hres.trans hε
    nlinarith [hbudget]
  have hnoisy := corollary_30_3 s hδ hδ₁ hdata
  change ‖RegularizedHilbertRepair.correction T (alpha m) hα s - w‖ ≤
      Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 ∧
    Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 ≤
      (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) at hnoisy
  have he : a - w =
      (a - RegularizedHilbertRepair.correction T (alpha m) hα s) +
      (RegularizedHilbertRepair.correction T (alpha m) hα s - w) := by abel
  rw [he]
  exact (norm_add_le _ _).trans
    ((add_le_add hsolver (hnoisy.1.trans hnoisy.2)).trans_eq (by ring))

end KomorebiSpace.DiagonalRegularization
