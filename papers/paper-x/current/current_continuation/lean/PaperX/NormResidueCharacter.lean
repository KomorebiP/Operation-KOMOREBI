import PaperX.NormResidueArithmetic
import Mathlib.Analysis.Complex.Basic

/-! A unit witness gives zero mean for a pulled-back norm character on the
whole finite residue ring. Nontriviality on the codomain alone is not enough:
the character must remain nontrivial on the image of a unit. -/

set_option autoImplicit false
noncomputable section

open scoped BigOperators NumberField

namespace PaperX.NormResidue

/-- Multiplication by a unit permutes every element of a finite monoid,
including nonunits. A nontrivial multiplier therefore forces zero total sum. -/
theorem sum_norm_character_eq_zero {R S : Type*} [Monoid R] [Fintype R] [Monoid S]
    (N : R →* S) (χ : S →* ℂ) (u : Rˣ) (hu : χ (N (u : R)) ≠ 1) :
    ∑ a : R, χ (N a) = 0 := by
  have hs : χ (N (u : R)) * ∑ a : R, χ (N a) = ∑ a : R, χ (N a) := by
    rw [Finset.mul_sum]
    simp_rw [← map_mul χ, ← map_mul N]
    exact Equiv.sum_comp u.mulLeft (fun a => χ (N a))
  have hz : (χ (N (u : R)) - 1) * ∑ a : R, χ (N a) = 0 := by
    rw [sub_mul, one_mul, hs, sub_self]
  exact (mul_eq_zero.mp hz).resolve_left (sub_ne_zero.mpr hu)

/-- A fixed residue multiplier, in particular a fixed norm sign, preserves
the zero-mean conclusion. -/
theorem sum_mul_norm_character_eq_zero {R S : Type*}
    [Monoid R] [Fintype R] [Monoid S]
    (N : R →* S) (χ : S →* ℂ) (u : Rˣ) (hu : χ (N (u : R)) ≠ 1) (c : S) :
    ∑ a : R, χ (c * N a) = 0 := by
  simp_rw [map_mul χ]
  rw [← Finset.mul_sum, sum_norm_character_eq_zero N χ u hu, mul_zero]

/-- Nontriviality of the character pulled back to units is exactly the
existence of the unit witness used by the cancellation theorem. -/
theorem norm_unit_character_ne_one_iff {R S : Type*} [Monoid R] [Monoid S]
    (N : R →* S) (χ : S →* ℂ) :
    (χ.comp N).comp (Units.coeHom R) ≠ 1 ↔ ∃ u : Rˣ, χ (N (u : R)) ≠ 1 := by
  constructor
  · intro h
    by_contra hn
    push Not at hn
    apply h
    exact MonoidHom.ext (fun u => by simpa using hn u)
  · rintro ⟨u, hu⟩ h
    apply hu
    exact DFunLike.congr_fun h u

variable (K : Type*) [Field K] [NumberField K]

/-- Zero mean for the actual determinant norm on the residue ring of integers.
The finite enumeration can be obtained from `integer_quotient_finite` for every
nonzero modulus. The unit witness remains explicit. -/
theorem integerQuotient_sum_character_eq_zero (m : ℕ)
    [Fintype (𝓞 K ⧸ modulusIdeal (𝓞 K) m)]
    (χ : ZMod m →*₀ ℂ) (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1) :
    ∑ a : 𝓞 K ⧸ modulusIdeal (𝓞 K) m, χ (integerQuotientNorm K m a) = 0 :=
  sum_norm_character_eq_zero (integerQuotientNorm K m) χ.toMonoidHom u hu

/-- The same exact mean cancellation holds after any fixed residue multiplier,
so positive and negative norm-sign sectors have the same cancellation input. -/
theorem integerQuotient_sum_mul_character_eq_zero (m : ℕ)
    [Fintype (𝓞 K ⧸ modulusIdeal (𝓞 K) m)]
    (χ : ZMod m →*₀ ℂ) (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1)
    (c : ZMod m) :
    ∑ a : 𝓞 K ⧸ modulusIdeal (𝓞 K) m, χ (c * integerQuotientNorm K m a) = 0 :=
  sum_mul_norm_character_eq_zero (integerQuotientNorm K m) χ.toMonoidHom u hu c

end PaperX.NormResidue
