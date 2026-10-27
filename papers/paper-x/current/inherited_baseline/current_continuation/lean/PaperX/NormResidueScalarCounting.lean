import PaperX.NormResidueScalarWitness
import PaperX.NormResidueCharacterCounting

/-! Scalar-unit criteria discharge the two explicit arithmetic hypotheses in the
norm-character counting theorem: the residue-unit witness and nonvanishing on
the chosen inverse-class representative. -/

set_option autoImplicit false
noncomputable section

open Ideal NumberField
open scoped nonZeroDivisors NumberField

namespace PaperX.NormResidue

/-- A multiplicative character is nonzero on every integer residue coprime to
its modulus. -/
theorem character_natCast_ne_zero_of_coprime (m n : ℕ) (χ : ZMod m →*₀ ℂ)
    (h : n.Coprime m) :
    χ (n : ZMod m) ≠ 0 := by
  exact (((ZMod.isUnit_iff_coprime n m).2 h).map χ.toMonoidHom).ne_zero

end PaperX.NormResidue

namespace PaperX.NormResidueLattice

open PaperX.NormResidue
open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted

variable (K : Type*) [Field K] [NumberField K]

/-- If the norm character is already nontrivial on scalar residue units, the
field degree is coprime to the unit-group order, and the inverse-class
representative has norm coprime to the modulus, then the actual ideal
norm-character sum has the Paper X power-saving bound with no supplied quotient
unit witness and no supplied nonvanishing value. -/
theorem exists_classNormSum_bound_of_scalar_units {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient)
    (hJcop : (absNorm (J : Ideal (𝓞 K))).Coprime m) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K := by
  obtain ⟨u, hu⟩ :=
    exists_scalarResidueUnit_witness_of_restricted_nontrivial K m hm χ hχ hdeg
  exact exists_classNormSum_bound_of_unit K hJ m hm χ u hu
    (character_natCast_ne_zero_of_coprime m (absNorm (J : Ideal (𝓞 K))) χ hJcop)

end PaperX.NormResidueLattice
