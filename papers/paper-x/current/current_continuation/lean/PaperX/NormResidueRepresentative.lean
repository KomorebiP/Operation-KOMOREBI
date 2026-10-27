import PaperX.NormResidueTotientWitness

/-!
# Coprime inverse-class representatives

A multiplicative character on `ZMod m` is nonzero exactly on units.  Hence an
inverse-class ideal whose absolute norm is coprime to `m` automatically
satisfies the representative nonvanishing hypothesis in the norm-character
transfer theorem.
-/

set_option autoImplicit false
noncomputable section

open Ideal NumberField
open scoped NumberField nonZeroDivisors

namespace PaperX.NormResidue

/-- Coprimality of an integer with the modulus forces every multiplicative
character to be nonzero on its residue class. -/
theorem mulChar_natCast_ne_zero_of_coprime (m n : ℕ) (χ : ZMod m →*₀ ℂ)
    (h : n.Coprime m) : χ (n : ZMod m) ≠ 0 := by
  exact (((ZMod.isUnit_iff_coprime n m).2 h).map χ).ne_zero

end PaperX.NormResidue

namespace PaperX.NormResidueLattice

open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- Under the scalar-unit/totient criterion, a coprime inverse-class
representative is enough for the actual ideal norm-character power saving.
The separate nonvanishing character-value hypothesis has disappeared. -/
theorem exists_classNormSum_bound_of_totient_coprime_representative
    {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient)
    (hJcop : (absNorm (J : Ideal (𝓞 K))).Coprime m) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K := by
  apply exists_classNormSum_bound_of_totient_coprime K hJ m hm χ hχ hdeg
  exact mulChar_natCast_ne_zero_of_coprime m _ χ hJcop

end PaperX.NormResidueLattice
