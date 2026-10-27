module
public import PolynomialTaylorDisplacement
public import PolynomialWeightedInverse

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialMotionEstimate
open scoped BigOperators
open MvPolynomial PolynomialWeightedInverse
variable {d : ℕ}

/-- First-order displacement with the original Jacobian inverse certificate.
This estimate applies to any actual perturbed root having the weighted root bound. -/
theorem first_order_error_dvd (p s M : ℕ) [Fact p.Prime]
    (F H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (a b : Fin d → ℤ_[p])
    (A : Matrix (Fin d) (Fin d) ℤ_[p]) (hM : 2 * s < M)
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s •
      (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hFa : ∀ i, eval a (F i) = 0)
    (hRoot : ∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0)
    (hDepth : ∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) :
    ∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣
      b i - a i + (p : ℤ_[p]) ^ (M - s) *
        (A.mulVec (fun j => eval a (H j))) i := by
  have hFa' (i : Fin d) : eval a (precondition A F i) = 0 := by
    simp [precondition, hFa]
  have hRoot' (i : Fin d) : eval b (precondition A F i) +
      (p : ℤ_[p]) ^ M * eval b (precondition A H i) = 0 := by
    simp only [precondition, map_sum, map_mul, eval_C]
    rw [Finset.mul_sum, ← Finset.sum_add_distrib]
    apply Finset.sum_eq_zero
    intro j _
    calc
      A i j * eval b (F j) + (p : ℤ_[p]) ^ M * (A i j * eval b (H j)) =
          A i j * (eval b (F j) + (p : ℤ_[p]) ^ M * eval b (H j)) := by ring
      _ = 0 := by rw [hRoot j, mul_zero]
  have hlin (i : Fin d) :
      (∑ j, eval a (pderiv j (precondition A F i)) * (b j - a j)) =
        (p : ℤ_[p]) ^ s * (b i - a i) := by
    change (jacobian (precondition A F) a).mulVec (fun j => b j - a j) i = _
    rw [jacobian_precondition, hAJ, Matrix.smul_mulVec, Matrix.one_mulVec]
    rfl
  have hp : (p : ℤ_[p]) ≠ 0 := Nat.cast_ne_zero.mpr (Fact.out : p.Prime).ne_zero
  have hsM : s ≤ M := by omega
  have hpowM : (p : ℤ_[p]) ^ M = (p : ℤ_[p]) ^ s * (p : ℤ_[p]) ^ (M - s) := by
    rw [← pow_add, Nat.add_sub_of_le hsM]
  have hexp : s + (2 * M - 3 * s) = (M - s) * 2 := by omega
  have hpow : (p : ℤ_[p]) ^ s * (p : ℤ_[p]) ^ (2 * M - 3 * s) =
      ((p : ℤ_[p]) ^ (M - s)) ^ 2 := by
    rw [← pow_add, hexp, pow_mul]
  intro i
  have hTaylor := PolynomialTaylorDisplacement.taylor_remainder_dvd
    (precondition A F i) a b ((p : ℤ_[p]) ^ (M - s)) hDepth
  rw [hFa' i, sub_zero, hlin i] at hTaylor
  have hVariation := PolynomialTaylorRing.eval_dvd_of_dvd
    (precondition A H i) a b ((p : ℤ_[p]) ^ (M - s)) hDepth
  have hVariationM : ((p : ℤ_[p]) ^ (M - s)) ^ 2 ∣
      (p : ℤ_[p]) ^ M * (eval b (precondition A H i) - eval a (precondition A H i)) := by
    rw [pow_two]
    exact mul_dvd_mul (pow_dvd_pow (p : ℤ_[p]) (by omega)) hVariation
  have hBig : ((p : ℤ_[p]) ^ (M - s)) ^ 2 ∣
      (p : ℤ_[p]) ^ s * (b i - a i) + (p : ℤ_[p]) ^ M * eval a (precondition A H i) := by
    convert dvd_neg.mpr (dvd_add hTaylor hVariationM) using 1
    linear_combination hRoot' i
  rw [congrFun (eval_precondition A H a) i] at hBig
  apply (mul_dvd_mul_iff_left (pow_ne_zero s hp)).mp
  rw [hpow, mul_add, ← mul_assoc, ← hpowM]
  exact hBig

end Komorebi.PolynomialMotionEstimate
