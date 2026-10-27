import PaperX.NormResidueAlgebra
import Mathlib.NumberTheory.NumberField.Norm

/-!
# Arithmetic residue norms and the sign of principal ideal norms

The finite residue norm is attached to the ring of integers itself. Absolute
ideal norms agree with signed element norms only after choosing a norm sign.
-/

set_option backward.isDefEq.respectTransparency.types false

noncomputable section

open scoped NumberField

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- The canonical norm map on the actual quotient of the ring of integers. -/
def integerQuotientNorm (m : ℕ) :
    𝓞 K ⧸ modulusIdeal (𝓞 K) m →* ZMod m :=
  quotientNorm (Module.Free.chooseBasis ℤ (𝓞 K)) m

theorem integerQuotientNorm_mk (m : ℕ) (x : 𝓞 K) :
    integerQuotientNorm K m (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x) =
      (Algebra.norm ℤ x : ZMod m) :=
  quotientNorm_mk _ _ _

theorem integer_norm_congr (m : ℕ) {x y : 𝓞 K}
    (h : x - y ∈ modulusIdeal (𝓞 K) m) :
    (Algebra.norm ℤ x : ZMod m) = (Algebra.norm ℤ y : ZMod m) :=
  norm_congr_of_sub_mem (Module.Free.chooseBasis ℤ (𝓞 K)) m h

theorem integer_quotient_finite (m : ℕ) (hm : m ≠ 0) :
    Finite (𝓞 K ⧸ modulusIdeal (𝓞 K) m) := by
  apply Ideal.finiteQuotientOfFreeOfNeBot
  change Ideal.span {(m : 𝓞 K)} ≠ ⊥
  intro h
  exact (Nat.cast_ne_zero.mpr hm) (Ideal.span_singleton_eq_bot.mp h)

theorem integer_quotient_card (m : ℕ) :
    Nat.card (𝓞 K ⧸ modulusIdeal (𝓞 K) m) = m ^ Module.finrank ℚ K := by
  rw [← Submodule.cardQuot_apply, ← Ideal.absNorm_apply]
  simp [modulusIdeal, Ideal.absNorm_span_singleton, Algebra.norm_natCast,
    NumberField.RingOfIntegers.rank]

theorem principal_absNorm_residue_nonneg (m : ℕ) {x : 𝓞 K}
    (hx : 0 ≤ Algebra.norm ℤ x) :
    (Ideal.absNorm (Ideal.span {x}) : ZMod m) =
      integerQuotientNorm K m (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x) := by
  rw [integerQuotientNorm_mk, Ideal.absNorm_span_singleton]
  have h : ((Algebra.norm ℤ x).natAbs : ℤ) = Algebra.norm ℤ x := by
    rw [Int.natCast_natAbs, abs_of_nonneg hx]
  simpa only [Int.cast_natCast, Int.cast_neg] using congrArg (fun z : ℤ => (z : ZMod m)) h

theorem principal_absNorm_residue_nonpos (m : ℕ) {x : 𝓞 K}
    (hx : Algebra.norm ℤ x ≤ 0) :
    (Ideal.absNorm (Ideal.span {x}) : ZMod m) =
      -integerQuotientNorm K m (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x) := by
  rw [integerQuotientNorm_mk, Ideal.absNorm_span_singleton]
  have h : ((Algebra.norm ℤ x).natAbs : ℤ) = -Algebra.norm ℤ x := by
    rw [Int.natCast_natAbs, abs_of_nonpos hx]
  simpa only [Int.cast_natCast, Int.cast_neg] using congrArg (fun z : ℤ => (z : ZMod m)) h

theorem principal_absNorm_congr_nonneg (m : ℕ) {x y : 𝓞 K}
    (h : x - y ∈ modulusIdeal (𝓞 K) m)
    (hx : 0 ≤ Algebra.norm ℤ x) (hy : 0 ≤ Algebra.norm ℤ y) :
    (Ideal.absNorm (Ideal.span {x}) : ZMod m) =
      (Ideal.absNorm (Ideal.span {y}) : ZMod m) := by
  rw [principal_absNorm_residue_nonneg K m hx, principal_absNorm_residue_nonneg K m hy,
    integerQuotientNorm_mk, integerQuotientNorm_mk]
  exact integer_norm_congr K m h

theorem principal_absNorm_congr_nonpos (m : ℕ) {x y : 𝓞 K}
    (h : x - y ∈ modulusIdeal (𝓞 K) m)
    (hx : Algebra.norm ℤ x ≤ 0) (hy : Algebra.norm ℤ y ≤ 0) :
    (Ideal.absNorm (Ideal.span {x}) : ZMod m) =
      (Ideal.absNorm (Ideal.span {y}) : ZMod m) := by
  rw [principal_absNorm_residue_nonpos K m hx, principal_absNorm_residue_nonpos K m hy,
    integerQuotientNorm_mk, integerQuotientNorm_mk]
  exact congrArg Neg.neg (integer_norm_congr K m h)

end PaperX.NormResidue
