module
public import PolynomialDigitBridge

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialSurjectiveStep
open Komorebi.NativeAffine Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
variable {d e : ℕ}

/-- The actual residue-ring Jacobian depends only on the point modulo q. -/
theorem digitJacobian_eq (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x y : Fin d → ℤ) (hxy : ∀ i, (q : ℤ) ∣ y i - x i) :
    digitJacobian q F y = digitJacobian q F x := by
  apply LinearMap.ext
  intro t
  ext i
  change (∑ k, (MvPolynomial.eval y (MvPolynomial.pderiv k (F i)) : ZMod q) * t k) =
    ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * t k
  apply Finset.sum_congr rfl
  intro k _
  have hd := Komorebi.PolynomialTaylor.pderiv_eval_dvd_of_dvd (F i) x y q hxy k
  have hz := (ZMod.intCast_zmod_eq_zero_iff_dvd
    (MvPolynomial.eval y (MvPolynomial.pderiv k (F i)) -
      MvPolynomial.eval x (MvPolynomial.pderiv k (F i))) q).mpr hd
  rw [Int.cast_sub, sub_eq_zero] at hz
  rw [hz]

/-- Every positive-depth digit correction preserves the actual finite Jacobian. -/
theorem digitJacobian_shift_eq (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x s : Fin d → ℤ) :
    digitJacobian q F (x + (q : ℤ)^L • s) = digitJacobian q F x := by
  apply digitJacobian_eq
  intro i
  change (q : ℤ) ∣ x i + (q : ℤ)^L * s i - x i
  rw [add_sub_cancel_left]
  exact dvd_mul_of_dvd_left (dvd_pow_self (q : ℤ) (by omega : L ≠ 0)) _

/-- Surjectivity of the reduced Jacobian produces an actual next polynomial
solution and is preserved at that new solution. -/
theorem one_step_lift (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian q F x)) :
    ∃ y : Fin d → ℤ,
      (∀ i, (q : ℤ)^L ∣ (y - x) i) ∧
      (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F y i) ∧
      Function.Surjective (digitJacobian q F y) := by
  obtain ⟨r, hr⟩ := Komorebi.PolynomialObstruction.residual_exists q L F x hx
  obtain ⟨t, ht⟩ := hJ (-(reduction q e r))
  have hcorr : reduction q e r + digitJacobian q F x t = 0 := by
    rw [ht, add_neg_cancel]
  refine ⟨x + (q : ℤ)^L • integerLift q t, ?_, ?_, ?_⟩
  · exact (same_residue_iff ((q : ℤ)^L) x _).mpr ⟨integerLift q t, rfl⟩
  · exact (digit_solution_iff q L hq hL F x r hr t).mpr hcorr
  · rw [digitJacobian_shift_eq q L hL F x]
    exact hJ

end Komorebi.PolynomialSurjectiveStep
