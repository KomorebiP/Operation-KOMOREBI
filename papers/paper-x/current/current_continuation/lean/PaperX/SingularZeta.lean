import PaperX.Singular
import PaperX.Zeta

/-! Rational singular seed zeta in Q[[X]], proved at all coefficient indices. -/
set_option autoImplicit false
namespace PaperX.SingularZeta
open PowerSeries

noncomputable def rootCoeff (q e m : ℕ) : ℚ :=
  if m = 0 then 0 else (q : ℚ) ^ (m - (m ⌈/⌉ e))

noncomputable def rootZeta (q e : ℕ) : ℚ⟦X⟧ := mk (rootCoeff q e)

theorem ceil_add_period (n e : ℕ) (he : 0 < e) :
    (n+e) ⌈/⌉ e = (n ⌈/⌉ e)+1 := by
  simp only [Nat.ceilDiv_eq_add_pred_div]
  have h : n + e + e - 1 = (n+e-1) + e := by omega
  rw [h, Nat.add_div_right _ he]

/-- After the initial e coefficients, the coefficients recur with ratio q^(e-1). -/
theorem rootCoeff_period (q e n : ℕ) (he : 0 < e) (hn : 0 < n) :
    rootCoeff q e (n+e) = rootCoeff q e n * (q : ℚ)^(e-1) := by
  have hc := PaperX.Singular.ceil_threshold_le n e he
  have ht : (n+e) - ((n ⌈/⌉ e)+1) = (n - (n ⌈/⌉ e)) + (e-1) := by omega
  simp only [rootCoeff, ite_eq_right (by omega : n+e ≠ 0), ite_eq_right (by omega : n ≠ 0)]
  rw [ceil_add_period n e he, ht, pow_add]

theorem initial_coefficient (q e n : ℕ) (he : 0 < e) (hn : 0 < n) (hne : n ≤ e) :
    rootCoeff q e n = (q : ℚ)^(n-1) := by
  have hupper : n ⌈/⌉ e ≤ 1 := (ceilDiv_le_iff_le_mul he).mpr (by simpa using hne)
  have hlower : 1 ≤ n ⌈/⌉ e := by
    have h := le_smul_ceilDiv (b := n) he
    simp only [smul_eq_mul] at h
    by_contra H
    have hz : n ⌈/⌉ e = 0 := by omega
    simp [hz] at h
    omega
  have hc : n ⌈/⌉ e = 1 := by omega
  simp [rootCoeff, hc, show n ≠ 0 by omega]

/-- The denominator removes the infinite tail, leaving an actual polynomial. -/
theorem singular_denominator_identity (q e : ℕ) (he : 0 < e) :
    rootZeta q e * (1 - C ((q : ℚ)^(e-1)) * X^e) =
      (trunc (e+1) (rootZeta q e) : ℚ⟦X⟧) := by
  rw [mul_sub, mul_one, ← mul_assoc]
  ext n
  simp only [map_sub, Polynomial.coeff_coe, coeff_trunc, coeff_mul_X_pow', coeff_mul_C,
    rootZeta, coeff_mk]
  by_cases hn : n < e
  · simp [show ¬ e ≤ n by omega, show n < e+1 by omega]
  · by_cases hne : n = e
    · subst n
      simp [rootCoeff]
    · have hp : 0 < n-e := by omega
      have h := rootCoeff_period q e (n-e) he hp
      rw [Nat.sub_add_cancel (by omega : e ≤ n)] at h
      simp [show e ≤ n by omega, show ¬n < e+1 by omega, h]

/-- The rational zeta function. Its numerator is supported in degrees 1,...,e. -/
theorem singular_zeta_formula (q e : ℕ) (he : 0 < e) :
    rootZeta q e = (trunc (e+1) (rootZeta q e) : ℚ⟦X⟧) *
      (1 - C ((q : ℚ)^(e-1)) * X^e)⁻¹ := by
  apply (eq_mul_inv_iff_mul_eq (by simp [Nat.ne_of_gt he])).mpr
  exact singular_denominator_identity q e he

/-- This identifies every numerator coefficient with the manuscript's finite sum. -/
theorem numerator_coefficients (q e n : ℕ) (he : 0 < e) :
    (trunc (e+1) (rootZeta q e)).coeff n =
      if 0 < n ∧ n ≤ e then (q : ℚ)^(n-1) else 0 := by
  rw [coeff_trunc]
  simp only [rootZeta, coeff_mk]
  by_cases hn : 0 < n ∧ n ≤ e
  · simp [hn, show n < e+1 by omega, initial_coefficient q e n he hn.1 hn.2]
  · by_cases hz : n = 0
    · subst n
      simp [rootCoeff]
    · simp [hn, show ¬ n < e+1 by omega]

variable {O : Type*} [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]
variable [Finite (O ⧸ IsLocalRing.maximalIdeal O)]

/-- Generating series defined from cardinalities of actual polynomial roots. -/
noncomputable def actualRootZeta (e : ℕ) : ℚ⟦X⟧ :=
  mk fun m => if m = 0 then 0 else (Nat.card (PaperX.Singular.Roots (O := O) m e) : ℚ)

theorem actualRootZeta_eq_model (e : ℕ) (he : 0 < e) :
    actualRootZeta (O := O) e = rootZeta (Nat.card (O ⧸ IsLocalRing.maximalIdeal O)) e := by
  ext n
  simp [actualRootZeta, rootZeta, rootCoeff, PaperX.Singular.singular_root_count n e he]

theorem actual_singular_zeta (e : ℕ) (he : 0 < e) :
    actualRootZeta (O := O) e = (trunc (e+1) (actualRootZeta (O := O) e) : ℚ⟦X⟧) *
      (1 - C ((Nat.card (O ⧸ IsLocalRing.maximalIdeal O) : ℚ)^(e-1)) * X^e)⁻¹ := by
  rw [actualRootZeta_eq_model e he]
  exact singular_zeta_formula _ e he

end PaperX.SingularZeta
