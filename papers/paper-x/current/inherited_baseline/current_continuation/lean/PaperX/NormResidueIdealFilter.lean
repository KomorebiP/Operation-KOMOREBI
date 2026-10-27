import PaperX.NormResidueArithmetic

/-!
# Finite residue filters for actual ideal norms

For `I * J = (x)`, the norm of `I` is recovered from the residue of `x`
after fixing its norm sign and assuming the norm of `J` is a unit modulo `m`.
The residue target may be empty; no surjectivity of the norm is asserted.
-/

set_option backward.isDefEq.respectTransparency.types false
noncomputable section

open scoped NumberField

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- Signed residue norm, with `true` selecting the nonnegative sign. -/
def signedResidue (m : ℕ) (positive : Bool)
    (q : 𝓞 K ⧸ modulusIdeal (𝓞 K) m) : ZMod m :=
  if positive then integerQuotientNorm K m q else -integerQuotientNorm K m q

/-- The sign condition needed to identify a signed norm with its absolute value. -/
def normSign (positive : Bool) (x : 𝓞 K) : Prop :=
  if positive then 0 ≤ Algebra.norm ℤ x else Algebra.norm ℤ x ≤ 0

theorem signedResidue_mk (m : ℕ) (positive : Bool) {x : 𝓞 K}
    (hx : normSign K positive x) :
    signedResidue K m positive (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x) =
      (Ideal.absNorm (Ideal.span {x}) : ZMod m) := by
  cases positive with
  | false => exact (principal_absNorm_residue_nonpos K m hx).symm
  | true => exact (principal_absNorm_residue_nonneg K m hx).symm

theorem ideal_product_norm_residue (m : ℕ) (I J : Ideal (𝓞 K)) {x : 𝓞 K}
    (hIJ : I * J = Ideal.span {x}) :
    (Ideal.absNorm I : ZMod m) * (Ideal.absNorm J : ZMod m) =
      (Ideal.absNorm (Ideal.span {x}) : ZMod m) := by
  rw [← Nat.cast_mul, ← map_mul, hIJ]

theorem signedResidue_eq_ideal_product (m : ℕ) (positive : Bool)
    (I J : Ideal (𝓞 K)) {x : 𝓞 K}
    (hIJ : I * J = Ideal.span {x}) (hx : normSign K positive x) :
    signedResidue K m positive (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x) =
      (Ideal.absNorm I : ZMod m) * (Ideal.absNorm J : ZMod m) := by
  rw [signedResidue_mk K m positive hx, ideal_product_norm_residue K m I J hIJ]

/-- The actual finite residue classes which encode one prescribed ideal norm residue. -/
def idealResidueTarget (m : ℕ) (positive : Bool) (J : Ideal (𝓞 K)) (c : ZMod m) :
    Set (𝓞 K ⧸ modulusIdeal (𝓞 K) m) :=
  {q | signedResidue K m positive q = c * (Ideal.absNorm J : ZMod m)}

theorem idealResidueTarget_finite (m : ℕ) (hm : m ≠ 0) (positive : Bool)
    (J : Ideal (𝓞 K)) (c : ZMod m) : (idealResidueTarget K m positive J c).Finite := by
  let := integer_quotient_finite K m hm
  exact Set.toFinite _

theorem ideal_norm_residue_iff (m : ℕ) (positive : Bool)
    (I J : Ideal (𝓞 K)) {x : 𝓞 K} (c : ZMod m)
    (hIJ : I * J = Ideal.span {x}) (hx : normSign K positive x)
    (hJ : IsUnit (Ideal.absNorm J : ZMod m)) :
    (Ideal.absNorm I : ZMod m) = c ↔
      Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x ∈ idealResidueTarget K m positive J c := by
  change _ ↔ signedResidue K m positive _ = _
  rw [signedResidue_eq_ideal_product K m positive I J hIJ hx]
  exact hJ.mul_left_inj.symm

theorem ideal_norm_residue_iff_of_coprime (m : ℕ) (positive : Bool)
    (I J : Ideal (𝓞 K)) {x : 𝓞 K} (c : ZMod m)
    (hIJ : I * J = Ideal.span {x}) (hx : normSign K positive x)
    (hJ : (Ideal.absNorm J).Coprime m) :
    (Ideal.absNorm I : ZMod m) = c ↔
      Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x ∈ idealResidueTarget K m positive J c :=
  ideal_norm_residue_iff K m positive I J c hIJ hx ((ZMod.isUnit_iff_coprime _ _).mpr hJ)

end PaperX.NormResidue
