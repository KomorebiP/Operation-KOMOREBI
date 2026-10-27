import PaperX.NormResidueScalarPower
import PaperX.NormResidueCharacterCounting
import Mathlib.Data.Nat.Totient

/-!
# Totient criterion for automatic norm-residue cancellation

The scalar unit group of `ZMod m` has cardinality `φ(m)`.  Thus coprimality of
`[K : ℚ]` with `φ(m)` makes the degree power map on scalar units bijective.  A
nontrivial scalar-unit character then supplies the residue-unit witness needed
by the actual ideal norm-character cancellation theorem.
-/

set_option autoImplicit false
noncomputable section

open scoped NumberField nonZeroDivisors
open Ideal NumberField

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- Concrete Euler-totient version of the scalar power witness criterion. -/
theorem exists_scalarResidueUnit_witness_of_totient_coprime
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient) :
    ∃ u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ,
      χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1 := by
  let _ : NeZero m := ⟨hm⟩
  apply exists_scalarResidueUnit_witness_of_card_coprime K m hm χ hχ
  rw [Nat.card_eq_fintype_card, ZMod.card_units_eq_totient]
  exact hdeg.symm

end PaperX.NormResidue

namespace PaperX.NormResidueLattice

open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- The residue-unit witness is eliminated from the class norm-character bound
whenever the scalar restriction is nontrivial and the field degree is coprime
to `φ(m)`.  The inverse-class representative nonvanishing condition remains
explicit. -/
theorem exists_classNormSum_bound_of_totient_coprime
    {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient)
    (hχJ : χ (absNorm (J : Ideal (𝓞 K)) : ZMod m) ≠ 0) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K := by
  obtain ⟨u, hu⟩ :=
    exists_scalarResidueUnit_witness_of_totient_coprime K m hm χ hχ hdeg
  exact exists_classNormSum_bound_of_unit K hJ m hm χ u hu hχJ

end PaperX.NormResidueLattice
