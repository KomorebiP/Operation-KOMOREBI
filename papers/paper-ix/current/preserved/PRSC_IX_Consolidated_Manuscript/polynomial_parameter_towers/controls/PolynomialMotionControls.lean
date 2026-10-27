module
public import PolynomialWeightedControls
public import PolynomialRootMotion
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialMotionControls
open MvPolynomial Komorebi.PolynomialPadicUnique

/-- A unit-Jacobian example attaining the first-order error bound. -/
def sharpQuadratic : MvPolynomial (Fin 1) ℤ_[2] := X 0 + X 0 ^ 2

/-- The unperturbed system has an exact root and unit derivative at zero. -/
theorem sharpQuadratic_base :
    eval (0 : Fin 1 → ℤ_[2]) sharpQuadratic = 0 ∧
    eval (0 : Fin 1 → ℤ_[2]) (pderiv 0 sharpQuadratic) = 1 := by
  norm_num [sharpQuadratic]

/-- Exhaustive finite verification of the residue class of every even root. -/
theorem sharp_mod_eight (x : ZMod 8) (hx : x + x ^ 2 + 2 = 0)
    (heven : ∃ y : ZMod 8, x = 2 * y) : x + 2 = 4 := by
  have h : ∀ z : ZMod 8, z + z ^ 2 + 2 = 0 →
      (∃ y : ZMod 8, z = 2 * y) → z + 2 = 4 := by decide
  exact h x hx heven

/-- The first-order error is exactly depth two for any selected even root of
X + X² + 2. Existence is supplied by the main perturbation theorem. -/
theorem sharp_error_of_even_root (b : ℤ_[2]) (hb : (2 : ℤ_[2]) ∣ b)
    (hroot : b + b ^ 2 + 2 = 0) :
    (2 : ℤ_[2]) ^ 2 ∣ b + 2 ∧ ¬ (2 : ℤ_[2]) ^ 3 ∣ b + 2 := by
  rcases hb with ⟨c, hc⟩
  have herror : b + 2 = (2 : ℤ_[2]) ^ 2 * (-c ^ 2) := by
    rw [hc] at hroot ⊢
    linear_combination hroot
  constructor
  · exact ⟨-c ^ 2, herror⟩
  · intro hdeep
    have hzero : PadicInt.toZModPow 3 (b + 2) = 0 := by
      have h := (toZModPow_eq_iff_dvd_sub 2 3 (b + 2) 0).mpr
        (by simpa using hdeep)
      simpa only [map_zero] using h
    have hroot8 := congrArg (PadicInt.toZModPow 3) hroot
    have hc8 := congrArg (PadicInt.toZModPow 3) hc
    simp only [map_add, map_pow, map_ofNat, map_zero] at hroot8
    simp only [map_mul, map_ofNat] at hc8
    have hfour := sharp_mod_eight (PadicInt.toZModPow 3 b) hroot8
      ⟨PadicInt.toZModPow 3 c, hc8⟩
    simp only [map_add, map_ofNat] at hzero
    rw [hfour] at hzero
    exact (by decide : (4 : ZMod 8) ≠ 0) hzero

/-- The sharpness example has an actual p-adic root, constructed by the same
main theorem being tested, and its first-order error has no extra digit. -/
theorem exists_sharp_motion_root :
    ∃ b : ℤ_[2], b + b ^ 2 + 2 = 0 ∧ (2 : ℤ_[2]) ∣ b ∧
      (2 : ℤ_[2]) ^ 2 ∣ b + 2 ∧ ¬ (2 : ℤ_[2]) ^ 3 ∣ b + 2 := by
  have hJ : PolynomialWeightedInverse.jacobian
      (fun _ : Fin 1 => sharpQuadratic) (0 : Fin 1 → ℤ_[2]) =
      (1 : Matrix (Fin 1) (Fin 1) ℤ_[2]) := by
    ext i j
    fin_cases i
    fin_cases j
    norm_num [PolynomialWeightedInverse.jacobian, sharpQuadratic]
  obtain ⟨b, hb, _, hball, _⟩ :=
    PolynomialRootMotion.exists_perturbed_root_certificate 2 0 1 (by decide)
      (fun _ : Fin 1 => sharpQuadratic) (fun _ => C 1) (0 : Fin 1 → ℤ_[2])
      (1 : Matrix (Fin 1) (Fin 1) ℤ_[2])
      (by simp [hJ]) (by simp [hJ]) (fun _ => sharpQuadratic_base.1)
  have hroot : b 0 + b 0 ^ 2 + 2 = 0 := by
    simpa [PolynomialMotionNormalization.perturbSystem, sharpQuadratic] using hb 0
  have htwo : (2 : ℤ_[2]) ∣ b 0 := by simpa using hball 0
  exact ⟨b 0, hroot, htwo, sharp_error_of_even_root (b 0) htwo hroot⟩

/-- The universal claim of one additional error digit is false for actual roots. -/
theorem no_uniform_extra_error_digit :
    ¬ ∀ b : ℤ_[2], b + b ^ 2 + 2 = 0 → (2 : ℤ_[2]) ∣ b →
      (2 : ℤ_[2]) ^ 3 ∣ b + 2 := by
  intro h
  obtain ⟨b, hroot, heven, _, hnot⟩ := exists_sharp_motion_root
  exact hnot (h b hroot heven)

end Komorebi.PolynomialMotionControls
