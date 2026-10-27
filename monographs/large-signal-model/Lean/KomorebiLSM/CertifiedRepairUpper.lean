import KomorebiLSM.ConvexRepairBracketing
import KomorebiLSM.RationalBernsteinMargin

/-! An actual complete rational subdivision certificate supplies P80's upper
bracket for the same repaired family, rather than an assumed feasibility result. -/
set_option autoImplicit false
namespace Komorebi.LSM.CertifiedRepairUpper
open LorentzCylinder RobustOrientedMargin InteriorRepair ConvexRepairBracketing RationalBernsteinMargin
variable {A : Type*} {n : ℕ}

/-- Exact family identification connects the finite P75 witness to the repair being bracketed. -/
theorem bernstein_upper_bound
    (H : A → ℝ → State ℂ →L[ℝ] State ℂ) (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (etaU : ℝ) (hetaU : etaU∈Set.Icc 0 1) (certificate : ∀ a,Certificate (G a) kappa)
    (sameFamily : ∀ a u,PolynomialGram.operatorPolynomial (fun k => matrixOperator (G a k)) u=
      repair (H a u) 1 etaU) :
    etaStar H (kappa : ℝ)≤etaU := by
  apply certificate_upper_bound H (kappa : ℝ) etaU hetaU
  intro a u hu
  simpa only [sameFamily a u] using (certificate a).margin u hu

/-- The lower endpoint is bracketed by a genuine evaluated positive functional
and a complete, sound certificate on the entire repaired family. -/
theorem certified_bracket
    (H : A → ℝ → State ℂ →L[ℝ] State ℂ) (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (hkappa : kappa∈Set.Icc 0 1) (etaU : ℝ) (hetaU : etaU∈Set.Icc 0 1)
    (certificate : ∀ a,Certificate (G a) kappa)
    (sameFamily : ∀ a u,PolynomialGram.operatorPolynomial (fun k => matrixOperator (G a k)) u=
      repair (H a u) 1 etaU)
    (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) (v q : ℂ) (hv : ‖v‖≤1) (hq : ‖q‖≤1)
    (hbad : separator q (H a u (1,v))<(kappa : ℝ)) :
    etaStar H (kappa : ℝ)∈Set.Icc 0 1 ∧
      (kappa-separator q (H a u (1,v)))/(1-separator q (H a u (1,v)))≤etaStar H (kappa : ℝ) ∧
      etaStar H (kappa : ℝ)≤etaU := by
  have hkappa1 : (kappa : ℝ)≤1 := by exact_mod_cast hkappa.2
  exact ⟨etaStar_in_unit H _ hkappa1,
    separator_lower_endpoint H _ hkappa1 a u hu v q hv hq hbad,
    bernstein_upper_bound H G kappa etaU hetaU certificate sameFamily⟩

end Komorebi.LSM.CertifiedRepairUpper
