module
public import PolynomialTowerControls

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialDeformationControls
open MvPolynomial PolynomialDigitBridge

def squareMinusOne : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 ^ 2 - C 1

/-- At the root one the actual Jacobian of X²−1 is invertible modulo three. -/
theorem square_minus_one_jacobian_bijective :
    Function.Bijective (digitJacobian 3 squareMinusOne (fun _ => 1)) := by
  have hformula : ∀ t : Fin 1 → ZMod 3,
      digitJacobian 3 squareMinusOne (fun _ => 1) t = fun i => 2 * t i := by
    intro t
    ext i
    simp [digitJacobian, squareMinusOne, Fin.eq_zero i]
  constructor
  · intro u v h
    funext i
    have hi := congrFun h i
    rw [hformula, hformula] at hi
    exact mul_left_cancel₀ (by decide : (2 : ZMod 3) ≠ 0) hi
  · intro y
    refine ⟨fun i => 2 * y i, ?_⟩
    rw [hformula]
    funext i
    calc
      (2 : ZMod 3) * (2 * y i) = (2 * 2) * y i := (mul_assoc _ _ _).symm
      _ = y i := by rw [show (2 : ZMod 3) * 2 = 1 by decide, one_mul]

/-- Distinct exact roots persist outside the local residue ball, even when
the initial reduced Jacobian is invertible. The second root is not congruent to the first modulo three. -/
theorem square_minus_one_two_padic_roots :
    ∃ a b : Fin 1 → ℤ_[3], a ≠ b ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[3]) a (squareMinusOne i) = 0) ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[3]) b (squareMinusOne i) = 0) ∧
      ¬ (3 : ℤ_[3]) ∣ b 0 - a 0 := by
  refine ⟨fun _ => 1, fun _ => -1, ?_, ?_, ?_, ?_⟩
  · intro h
    have := congrFun h 0
    norm_num at this
  · intro i
    simp [squareMinusOne]
  · intro i
    simp [squareMinusOne]
  · intro h
    have heq : (-1 : ℤ_[3]) - 1 = ((-2 : ℤ) : ℤ_[3]) := by norm_num
    have hd : (3 : ℤ_[3]) ^ 1 ∣ ((-2 : ℤ) : ℤ_[3]) := by
      simpa only [pow_one, ← heq] using h
    have hi := (PadicInt.pow_p_dvd_int_iff (p := 3) 1 (-2)).mp hd
    norm_num at hi

/-- Global uniqueness is false for a square polynomial with invertible initial Jacobian. -/
theorem square_minus_one_not_global_unique :
    ¬ ∀ a b : Fin 1 → ℤ_[3],
      (∀ i, eval₂ (Int.castRingHom ℤ_[3]) a (squareMinusOne i) = 0) →
      (∀ i, eval₂ (Int.castRingHom ℤ_[3]) b (squareMinusOne i) = 0) → a = b := by
  intro h
  obtain ⟨a, b, hne, ha, hb, _⟩ := square_minus_one_two_padic_roots
  exact hne (h a b ha hb)

/-- The polynomial X−2 is exactly a perturbation of X by 2 times an integral polynomial. -/
theorem linear_shift_coefficient_perturbation (i : Fin 1) :
    PolynomialTowerControls.linearMinusTwo i =
      X 0 + C (2 : ℤ) * C (-1) := by
  simp [PolynomialTowerControls.linearMinusTwo, sub_eq_add_neg]

/-- An actual nonsingular dyadic perturbation has root displacement exactly two,
so coefficient precision two cannot be strengthened to displacement divisible by four. -/
theorem linear_shift_no_extra_padic_precision :
    ¬ ∃ b : Fin 1 → ℤ_[2],
      eval₂ (Int.castRingHom ℤ_[2]) b (PolynomialTowerControls.linearMinusTwo 0) = 0 ∧
      (2 : ℤ_[2]) ^ 2 ∣ b 0 := by
  rintro ⟨b, hb, hd⟩
  have hroot : b 0 = 2 := by
    simpa [PolynomialTowerControls.linearMinusTwo, sub_eq_zero] using hb
  rw [hroot] at hd
  have hi : (2 : ℤ) ^ 2 ∣ 2 := by
    exact (PadicInt.pow_p_dvd_int_iff 2 2).mp hd
  norm_num at hi

end Komorebi.PolynomialDeformationControls
