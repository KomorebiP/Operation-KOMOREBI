import PaperX.NormResidueAutomaticCounting

/-!
# Exact scalar-norm witness criterion

Degree--totient coprimality is a convenient sufficient condition for a scalar
unit witness, but it is stronger than necessary.  The exact scalar criterion is
simply the existence of a residue unit `a` on which the character is nontrivial
after the field-degree power map.  This module exposes that weaker hypothesis
and keeps automatic inverse-class representative selection.
-/

set_option autoImplicit false
noncomputable section

open Ideal NumberField MeasureTheory Filter Set Asymptotics
open scoped NumberField nonZeroDivisors Classical Topology

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- A scalar residue unit whose field-degree norm has nontrivial character value
is already the quotient-unit witness needed by the counting argument. -/
theorem exists_scalarResidueUnit_witness_of_scalar_power
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (a : (ZMod m)ˣ)
    (ha : χ ((a : ZMod m) ^ Module.finrank ℚ K) ≠ 1) :
    ∃ u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ,
      χ (integerQuotientNorm K m
        (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1 := by
  refine ⟨scalarResidueUnit K m hm a, ?_⟩
  rw [integerQuotientNorm_scalarResidueUnit]
  exact ha

end PaperX.NormResidue

namespace PaperX.NormResidueLattice

open PaperX.NormResidue
open PaperX.IdealClassQuantitative PaperX.IdealNormWeighted
open PaperX.RealAxisMellinMoment

variable (K : Type*) [Field K] [NumberField K]

/-- Exact-scalar-criterion form of the norm-character power saving.  This drops
the degree--totient coprimality assumption when a direct scalar witness is
available. -/
theorem exists_classNormSum_bound_of_scalar_power_autoRep
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hpow : ∃ a : (ZMod m)ˣ,
      χ ((a : ZMod m) ^ Module.finrank ℚ K) ≠ 1) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K := by
  obtain ⟨J, hJ, hJcop⟩ :=
    exists_coprime_inverse_class_representative K C m hm
  obtain ⟨a, ha⟩ := hpow
  obtain ⟨u, hu⟩ :=
    exists_scalarResidueUnit_witness_of_scalar_power K m hm χ a ha
  exact exists_classNormSum_bound_of_unit K hJ m hm χ u hu
    (character_natCast_ne_zero_of_coprime m (absNorm (J : Ideal (𝓞 K))) χ hJcop)

/-- Exact-scalar-criterion endpoint variation for the actual norm-character
Mellin factor. -/
theorem normCharacterMellin_sub_isBigO_of_scalar_power_autoRep
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hpow : ∃ a : (ZMod m)ˣ,
      χ ((a : ZMod m) ^ Module.finrank ℚ K) ≠ 1) :
    (fun h => normCharacterMellin K C m χ h - normCharacterMellin K C m χ 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  obtain ⟨B, _, hB⟩ :=
    exists_classNormSum_bound_of_scalar_power_autoRep K C m hm χ hpow
  exact mellinIntegral_sub_isBigO_of_power_bound
    (measurable_classNormSum K C (fun n => χ (n : ZMod m))).aestronglyMeasurable
    (PaperX.IdealClassCharacter.countExponent_lt_one K) (fun x hx => hB x hx.le)

end PaperX.NormResidueLattice
