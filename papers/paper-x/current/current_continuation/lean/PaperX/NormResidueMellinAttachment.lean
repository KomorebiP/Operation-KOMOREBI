import PaperX.NormResidueScalarCounting
import PaperX.IdealClassCharacterBound
import PaperX.IdealNormCharacterMellin

/-! Real-axis Mellin control for the actual ideal norm-character sum under the
checked scalar-unit arithmetic criteria. -/

set_option autoImplicit false
noncomputable section

open Ideal NumberField MeasureTheory Filter Set Asymptotics
open scoped nonZeroDivisors Classical Topology

namespace PaperX.NormResidueLattice

open PaperX.NormResidue
open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted
open PaperX.RealAxisMellinMoment

variable (K : Type*) [Field K] [NumberField K]

/-- Actual norm-character Mellin factor attached to one ordinary ideal class. -/
def normCharacterMellin (C : ClassGroup (𝓞 K)) (m : ℕ)
    (χ : ZMod m →*₀ ℂ) (h : ℝ) : ℂ :=
  normMellin K C (fun n => χ (n : ZMod m)) h

/-- The scalar-unit arithmetic criteria imply the logarithmic first moment for
the actual ideal norm-character sum. -/
theorem integrable_normCharacter_logMoment_of_scalar_units
    {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹) (m : ℕ) (hm : m ≠ 0)
    (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient)
    (hJcop : (absNorm (J : Ideal (𝓞 K))).Coprime m) :
    Integrable (fun x : ℝ =>
      (1 + Real.log x) *
        ‖(x ^ (-2 : ℝ)) • classNormSum K C (fun n => χ (n : ZMod m)) x‖)
      (volume.restrict (Ioi 1)) := by
  obtain ⟨B, _, hB⟩ :=
    exists_classNormSum_bound_of_scalar_units K hJ m hm χ hχ hdeg hJcop
  exact integrable_weighted_moment_of_power_bound
    (measurable_classNormSum K C (fun n => χ (n : ZMod m))).aestronglyMeasurable
    (PaperX.IdealClassCharacter.countExponent_lt_one K) (fun x hx => hB x hx.le)

/-- The actual norm-character Mellin factor has first-order right-endpoint
variation. This is the analytic input used by the pole-rigidity assembly. -/
theorem normCharacterMellin_sub_isBigO_of_scalar_units
    {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹) (m : ℕ) (hm : m ≠ 0)
    (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient)
    (hJcop : (absNorm (J : Ideal (𝓞 K))).Coprime m) :
    (fun h => normCharacterMellin K C m χ h - normCharacterMellin K C m χ 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  obtain ⟨B, _, hB⟩ :=
    exists_classNormSum_bound_of_scalar_units K hJ m hm χ hχ hdeg hJcop
  exact mellinIntegral_sub_isBigO_of_power_bound
    (measurable_classNormSum K C (fun n => χ (n : ZMod m))).aestronglyMeasurable
    (PaperX.IdealClassCharacter.countExponent_lt_one K) (fun x hx => hB x hx.le)

end PaperX.NormResidueLattice
