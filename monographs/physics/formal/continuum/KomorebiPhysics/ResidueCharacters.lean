module
public import Mathlib.Analysis.Fourier.ZMod
public import Mathlib.Tactic

/-! Exact finite character selection, with positive modulus and explicit
exponential/sign conventions. No floating point or sampled orthogonality. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResidueCharacters
open scoped BigOperators
variable (M : ℕ) [NeZero M]

theorem modulus_pos : 0 < M := Nat.pos_of_ne_zero (NeZero.ne M)

theorem modulus_cast_ne_zero : (M : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (NeZero.ne M)

theorem character_norm (j : ZMod M) : ‖ZMod.stdAddChar j‖ = 1 := by
  rw [ZMod.stdAddChar_apply]
  exact Circle.norm_coe _

theorem character_sum (d : ZMod M) :
    ∑ k : ZMod M, ZMod.stdAddChar (d * k) = if d = 0 then (M : ℂ) else 0 := by
  by_cases h : d = 0
  · simp [h, ZMod.card]
  · rw [ite_eq_right h]
    exact AddChar.sum_eq_zero_of_ne_one (ZMod.isPrimitive_stdAddChar M h)

/-- The negative receiving character selects n=r, not n=-r. -/
theorem selection (r n : ZMod M) :
    (M : ℂ)⁻¹ * ∑ k : ZMod M,
      ZMod.stdAddChar (-(r * k)) * ZMod.stdAddChar (k * n) =
        if n = r then 1 else 0 := by
  have he (k : ZMod M) : -(r * k) + k * n = (n-r)*k := by ring
  simp_rw [← AddChar.map_add_eq_mul, he]
  rw [character_sum]
  by_cases h : n = r
  · simp [h]
  · simp [sub_ne_zero.mpr h, h]

theorem character_nat (a b : ℕ) :
    ZMod.stdAddChar ((a : ZMod M) * (b : ZMod M)) =
      Complex.exp (2 * Real.pi * Complex.I * (a : ℂ) * (b : ℂ) / (M : ℂ)) := by
  have h := ZMod.stdAddChar_coe (N := M) ((a : ℤ) * (b : ℤ))
  push_cast at h
  simpa only [mul_assoc] using h

theorem character_negative_nat (a b : ℕ) :
    ZMod.stdAddChar (-((a : ZMod M) * (b : ZMod M))) =
      Complex.exp (-(2 * Real.pi * Complex.I * (a : ℂ) * (b : ℂ) / (M : ℂ))) := by
  have h := ZMod.stdAddChar_coe (N := M) (-((a : ℤ) * (b : ℤ)))
  push_cast at h
  convert h using 1
  congr 1
  ring

theorem character_product_exponential (r k : ZMod M) (n : ℕ) :
    ZMod.stdAddChar (-(r*k)) * ZMod.stdAddChar (k*(n : ZMod M)) =
      Complex.exp (-(2 * Real.pi * Complex.I * (r.val : ℂ) * (k.val : ℂ) / (M : ℂ))) *
      Complex.exp (2 * Real.pi * Complex.I * (k.val : ℂ) * (n : ℂ) / (M : ℂ)) := by
  have h := character_negative_nat M r.val k.val
  have g := character_nat M k.val n
  simp only [ZMod.natCast_zmod_val] at h g
  rw [h, g]

/-- Literal exponential summands over canonical residue representatives. -/
theorem exponential_selection (r : ZMod M) (n : ℕ) :
    (M : ℂ)⁻¹ * ∑ k : ZMod M,
      Complex.exp (-(2 * Real.pi * Complex.I * (r.val : ℂ) * (k.val : ℂ) / (M : ℂ))) *
      Complex.exp (2 * Real.pi * Complex.I * (k.val : ℂ) * (n : ℂ) / (M : ℂ)) =
        if (n : ZMod M) = r then 1 else 0 := by
  simp_rw [← character_product_exponential]
  exact selection M r n

/-- Concrete test: at modulus three, the plus sign selects the wrong lane. -/
theorem wrong_sign_three :
    (3 : ℂ)⁻¹ * ∑ k : ZMod 3,
      ZMod.stdAddChar ((1 : ZMod 3)*k) * ZMod.stdAddChar (k*(1 : ZMod 3)) = 0 := by
  have h := selection 3 (-1) 1
  have hn : (1 : ZMod 3) ≠ -1 := by decide
  simpa [hn] using h

end ResidueCharacters
end KomorebiPhysics
