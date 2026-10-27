import PaperX.PrimeDegreeSummabilityFrobenius
import Mathlib.FieldTheory.Galois.Basic

/-!
# Frobenius descent for actual field automorphisms

An actual E-linear field automorphism of T induces an actual O_E-linear
automorphism of O_T. This attachment commutes with scalar restriction.
Nonsummability is still assumed. Neither the Frobenius congruence nor this
attachment alone supplies unramifiedness.
-/

noncomputable section
set_option autoImplicit false

namespace PaperX.PrimeDegreeFieldFrobenius

open NumberField IsDedekindDomain

variable (E T : Type*) [Field E] [Field T] [Algebra E T]

/-- Restrict an actual field automorphism to the actual ring of integers. -/
def integralAut (τ : T ≃ₐ[E] T) : (𝓞 T) ≃ₐ[𝓞 E] (𝓞 T) :=
  RingOfIntegers.mapAlgEquiv τ

/-- The integral action is literally the original field action on integral elements. -/
theorem integralAut_apply (τ : T ≃ₐ[E] T) (x : 𝓞 T) :
    (integralAut E T τ x : T) = τ (x : T) := rfl

/-- The prime set is defined using the integral action of the supplied field automorphism. -/
def prescribedPrimes (τ : T ≃ₐ[E] T) : Set (HeightOneSpectrum (𝓞 E)) :=
  PrimeDegreeSummabilityFrobenius.prescribedPrimes E T (integralAut E T τ).toAlgHom

variable (K : Type*) [Field K] [Algebra K E] [Algebra K T] [IsScalarTower K E T]

/-- Integral attachment and restriction of scalars commute as algebra automorphisms. -/
theorem integralAut_restrictScalars (τ : T ≃ₐ[E] T) :
    (integralAut E T τ).restrictScalars (𝓞 K) =
      integralAut K T (τ.restrictScalars K) := rfl

/-- The corresponding equality of algebra endomorphisms used by the Frobenius predicate. -/
theorem integralHom_restrictScalars (τ : T ≃ₐ[E] T) :
    ((integralAut E T τ).toAlgHom).restrictScalars (𝓞 K) =
      (integralAut K T (τ.restrictScalars K)).toAlgHom := rfl

variable [NumberField K] [NumberField E]

/-- Nonsummability of the actual field-automorphism prime set gives descended Frobenius. -/
theorem exists_descended_field_frobenius
    (τ : T ≃ₐ[E] T)
    (hdiv : ¬ Summable (fun q : prescribedPrimes E T τ => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ∃ Q : HeightOneSpectrum (𝓞 T), (Q.under (𝓞 E)).under (𝓞 K) ∉ bad ∧
      (Q.asIdeal.under (𝓞 E)).inertiaDeg (𝓞 K) = 1 ∧
      (integralAut K T (τ.restrictScalars K)).toAlgHom.IsArithFrobAt Q.asIdeal := by
  simpa only [integralHom_restrictScalars] using
    PrimeDegreeSummabilityFrobenius.exists_descended_frobenius K E T
      (integralAut E T τ).toAlgHom hdiv bad hbad

section FixedField

variable (F U : Type*) [Field F] [Field U] [Algebra F U] [FiniteDimensional F U]

/-- Regard an actual automorphism as linear over the fixed field of the subgroup it generates. -/
def overFixedField (ρ : U ≃ₐ[F] U) :
    U ≃ₐ[IntermediateField.fixedField (Subgroup.zpowers ρ)] U :=
  IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers ρ)
    ⟨ρ, Subgroup.mem_zpowers ρ⟩

/-- The fixed-field automorphism has the original action on every field element. -/
theorem overFixedField_apply (ρ : U ≃ₐ[F] U) (x : U) :
    overFixedField F U ρ x = ρ x := rfl

/-- Returning to the original coefficient field recovers the original automorphism. -/
theorem overFixedField_restrictScalars (ρ : U ≃ₐ[F] U) :
    (overFixedField F U ρ).restrictScalars F = ρ := by
  ext x
  rfl

variable [NumberField F] [NumberField U]

/-- The fixed-field construction attaches the original automorphism to descended Frobenius. -/
theorem exists_fixedField_descended_frobenius
    (ρ : U ≃ₐ[F] U)
    (hdiv : ¬ Summable
      (fun q : prescribedPrimes (IntermediateField.fixedField (Subgroup.zpowers ρ)) U
        (overFixedField F U ρ) => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 F))) (hbad : bad.Finite) :
    ∃ Q : HeightOneSpectrum (𝓞 U),
      (Q.under (𝓞 (IntermediateField.fixedField (Subgroup.zpowers ρ)))).under (𝓞 F) ∉ bad ∧
      (Q.asIdeal.under (𝓞 (IntermediateField.fixedField (Subgroup.zpowers ρ)))).inertiaDeg
        (𝓞 F) = 1 ∧
      (integralAut F U ρ).toAlgHom.IsArithFrobAt Q.asIdeal := by
  simpa only [overFixedField_restrictScalars] using
    exists_descended_field_frobenius
      (IntermediateField.fixedField (Subgroup.zpowers ρ)) U F (overFixedField F U ρ)
      hdiv bad hbad

end FixedField

end PaperX.PrimeDegreeFieldFrobenius
