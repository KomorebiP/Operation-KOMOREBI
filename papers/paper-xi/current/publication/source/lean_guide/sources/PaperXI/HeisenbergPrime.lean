import PaperXI.SchrodingerOperator
import Mathlib.FieldTheory.Finite.Basic

/-! The odd-prime specialization uses exactly the manuscript's exponential
additive character, with nontriviality and invertibility of two proved. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergPrime

variable {p : ℕ} [Fact p.Prime]

theorem two_ne_zero (hp : p ≠ 2) : (2 : ZMod p) ≠ 0 := by
  intro h
  have hd : p ∣ 2 := (ZMod.natCast_eq_zero_iff 2 p).mp h
  exact hp ((Nat.prime_dvd_prime_iff_eq (Fact.out : p.Prime) Nat.prime_two).mp hd)

theorem character_nontrivial : (ZMod.stdAddChar (N := p)) ≠ 1 := by
  intro h
  have he : ZMod.stdAddChar (1 : ZMod p) = ZMod.stdAddChar (0 : ZMod p) := by
    rw [h]
    rfl
  exact one_ne_zero (ZMod.injective_stdAddChar he)

theorem character_formula (j : ℤ) :
    ZMod.stdAddChar (j : ZMod p) =
      Complex.exp (2 * Real.pi * Complex.I * j / p) :=
  ZMod.stdAddChar_coe j

end PaperXI.HeisenbergPrime
