import KomorebiSpaceRegularization

set_option autoImplicit false
noncomputable section
open KomorebiSpace
open scoped RealInnerProductSpace

example (T : ℝ →L[ℝ] ℝ) (α : ℝ) (hα : 0 < α) (r : ℝ) :
    ∃! a : ℝ, ∀ b : ℝ,
      RegularizedHilbertRepair.objective T α r a ≤
        RegularizedHilbertRepair.objective T α r b :=
  RegularizedHilbertRepair.exists_unique_minimizer T α hα r

example (α : ℝ) (hα : 0 < α) (r a : ℝ) :
    ‖a-RegularizedHilbertRepair.correction (0 : ℝ →L[ℝ] ℝ) α hα r‖ ≤
      ‖RegularizedHilbertRepair.gradient (0 : ℝ →L[ℝ] ℝ) α r a‖/α :=
  RegularizedHilbertRepair.correction_error_bound _ _ hα r a

example (D p : ℝ →L[ℝ] ℝ) (α : ℝ) (hα : 0 < α) (f r : ℝ) :
    p (ProtectedRegularizedRepair.repair D p α hα f r) = p f :=
  ProtectedRegularizedRepair.repair_preserves D p α hα f r

example (T : ℝ →L[ℝ] ℝ) (α : ℝ) (hα : 0 < α) (r a z : ℝ) :
    RegularizationCertificates.dual T α r z ≤ RegularizedHilbertRepair.objective T α r a :=
  RegularizationCertificates.dual_le_objective T α hα r z a

example : RegularizedHilbertRepair.gradient (0 : ℝ →L[ℝ] ℝ) (1/4) 0 1 = 1/4 := by
  norm_num [RegularizedHilbertRepair.gradient, RegularizedHilbertRepair.normal]

example : RegularizationCertificates.dual (0 : ℝ →L[ℝ] ℝ) 1 1 3 = -3 := by
  norm_num [RegularizationCertificates.dual, real_inner_comm]
