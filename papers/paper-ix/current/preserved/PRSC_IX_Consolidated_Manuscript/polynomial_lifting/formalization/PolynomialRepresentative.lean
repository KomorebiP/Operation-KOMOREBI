module
public import PolynomialObstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRepresentative
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
variable {d e : ℕ}

/-- The reduced actual Jacobian depends only on the point modulo q. -/
theorem digit_jacobian_eq (q : ℕ)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x y : Fin d → ℤ)
    (hxy : ∀ i, (q : ℤ) ∣ y i - x i) :
    digitMap q (jacobian F y) = digitMap q (jacobian F x) := by
  apply LinearMap.ext
  intro t
  have hz : reduction q e (jacobian F y t - jacobian F x t) = 0 := by
    apply (reduction_zero_iff q _).mpr
    intro i
    change (q : ℤ) ∣ (∑ k, MvPolynomial.eval y (MvPolynomial.pderiv k (F i)) * t k) -
      ∑ k, MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) * t k
    rw [← Finset.sum_sub_distrib]
    apply Finset.dvd_sum
    intro k _
    rw [← sub_mul]
    exact dvd_mul_of_dvd_left
      (Komorebi.PolynomialTaylor.pderiv_eval_dvd_of_dvd (F i) x y q hxy k) _
  change reduction q e (jacobian F y t) = reduction q e (jacobian F x t)
  exact sub_eq_zero.mp (by simpa only [map_sub] using hz)

/-- Changing an integer representative at positive depth preserves the reduced Jacobian. -/
theorem digit_jacobian_shift_eq (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x s : Fin d → ℤ) :
    digitMap q (jacobian F (x + (q : ℤ)^L • s)) = digitMap q (jacobian F x) := by
  apply digit_jacobian_eq
  intro i
  change (q : ℤ) ∣ x i + (q : ℤ)^L * s i - x i
  rw [add_sub_cancel_left]
  exact dvd_mul_of_dvd_left (dvd_pow_self (q : ℤ) (by omega : L ≠ 0)) _

/-- Exact residuals of two representatives differ by the Jacobian correction modulo q. -/
theorem residual_digit_transport (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x s : Fin d → ℤ)
    (r r' : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (hr' : evalSystem F (x + (q : ℤ)^L • s) = (q : ℤ)^L • r') :
    reduction q e r' = reduction q e (r + jacobian F x s) := by
  have hqL : (q : ℤ)^L ≠ 0 := pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hq))
  have hz : reduction q e (r' - (r + jacobian F x s)) = 0 := by
    apply (reduction_zero_iff q _).mpr
    intro i
    have ht := taylor_residual_dvd q L hL F x r hr s i
    rw [hr'] at ht
    change (q : ℤ)^(L+1) ∣ (q : ℤ)^L * r' i - (q : ℤ)^L * (r + jacobian F x s) i at ht
    rw [← mul_sub, pow_succ, mul_dvd_mul_iff_left hqL] at ht
    exact ht
  exact sub_eq_zero.mp (by simpa only [map_sub] using hz)

/-- In the common reduced-Jacobian quotient, the residual class is representative independent. -/
theorem residual_class_independent (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x s : Fin d → ℤ)
    (r r' : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (hr' : evalSystem F (x + (q : ℤ)^L • s) = (q : ℤ)^L • r') :
    obstruction q (jacobian F x) r' = obstruction q (jacobian F x) r := by
  unfold obstruction
  rw [residual_digit_transport q L hq hL F x s r r' hr hr']
  exact obstruction_representative_independent q (jacobian F x) r s

/-- Representative independence stated with a single explicit reduced map,
whose cokernel simultaneously identifies the two obstruction modules. -/
theorem representative_independence (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x y : Fin d → ℤ)
    (hxy : ∀ i, (q : ℤ)^L ∣ (y - x) i)
    (r r' : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (hr' : evalSystem F y = (q : ℤ)^L • r') :
    ∃ J : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ZMod q),
      digitMap q (jacobian F x) = J ∧ digitMap q (jacobian F y) = J ∧
      (Submodule.Quotient.mk (reduction q e r') : (Fin e → ZMod q) ⧸ LinearMap.range J) =
      Submodule.Quotient.mk (reduction q e r) := by
  obtain ⟨s, rfl⟩ := (same_residue_iff ((q : ℤ)^L) x y).mp hxy
  exact ⟨digitMap q (jacobian F x), rfl, digit_jacobian_shift_eq q L hL F x s,
    residual_class_independent q L hq hL F x s r r' hr hr'⟩

end Komorebi.PolynomialRepresentative
