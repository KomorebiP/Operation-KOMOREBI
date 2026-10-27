import PaperX.NormResidueCoprimeRepresentative
import PaperX.NormResidueMellinAttachment

/-!
# Automatic representative selection for norm-character counting

The coprime inverse-class representative is now constructed internally, so the
public counting and Mellin interfaces require only the scalar character
criterion and the degree--totient coprimality condition.
-/

set_option autoImplicit false
noncomputable section

open Ideal NumberField MeasureTheory Filter Set Asymptotics
open scoped NumberField nonZeroDivisors Classical Topology

namespace PaperX.NormResidueLattice

open PaperX.NormResidue
open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted
open PaperX.RealAxisMellinMoment

variable (K : Type*) [Field K] [NumberField K]

/-- Automatic-representative form of the Paper X norm-character power saving. -/
theorem exists_classNormSum_bound_of_scalar_units_autoRep
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K := by
  obtain ⟨J, hJ, hJcop⟩ :=
    exists_coprime_inverse_class_representative K C m hm
  exact exists_classNormSum_bound_of_scalar_units K hJ m hm χ hχ hdeg hJcop

/-- Automatic-representative logarithmic first-moment bound. -/
theorem integrable_normCharacter_logMoment_of_scalar_units_autoRep
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient) :
    Integrable (fun x : ℝ =>
      (1 + Real.log x) *
        ‖(x ^ (-2 : ℝ)) • classNormSum K C (fun n => χ (n : ZMod m)) x‖)
      (volume.restrict (Ioi 1)) := by
  obtain ⟨J, hJ, hJcop⟩ :=
    exists_coprime_inverse_class_representative K C m hm
  exact integrable_normCharacter_logMoment_of_scalar_units K hJ m hm χ hχ hdeg hJcop

/-- Automatic-representative first-order endpoint variation of the actual
norm-character Mellin factor. -/
theorem normCharacterMellin_sub_isBigO_of_scalar_units_autoRep
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient) :
    (fun h => normCharacterMellin K C m χ h - normCharacterMellin K C m χ 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  obtain ⟨J, hJ, hJcop⟩ :=
    exists_coprime_inverse_class_representative K C m hm
  exact normCharacterMellin_sub_isBigO_of_scalar_units K hJ m hm χ hχ hdeg hJcop

end PaperX.NormResidueLattice
