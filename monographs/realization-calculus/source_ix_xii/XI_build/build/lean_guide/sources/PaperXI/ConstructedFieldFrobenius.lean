import PaperXI.SpectralGeometricFrobenius
import PaperXI.SpectralLocalField

/-!
# Specialization to Paper XI's constructed spectral local field

The base of the finite Galois extension is the literal UpperField(K,s) from the
verified predecessor. The base residue cardinality in geometric normalization
is identified with the residue cardinality of that same field, by equality of
integer subrings and the induced residue equivalence.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ConstructedFieldFrobenius
open ValuativeRel IsLocalRing
open PaperXI.SpectralGeometricFrobenius

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s] [FiniteDimensional 𝓀[K] s]

abbrev BaseField := PaperXI.SpectralLocalField.UpperField K s

variable (L : Type*) [Field L] [Algebra (BaseField K s) L]
  [FiniteDimensional (BaseField K s) L]

/-- The restricted extension valuation recovers this very base's integer subring. -/
theorem restricted_integer_subring :
    ((integers (BaseField K s) L).comap
      (algebraMap (BaseField K s) (SpectralExtension (BaseField K s) L))).toSubring =
      (ValuativeRel.valuation (BaseField K s)).integer := by
  rw [integers_comap]
  exact (PaperXI.SpectralLocalField.relation_integer_eq_norm_integer K s).symm

/-- The underlying base integer rings are equal, not merely equicardinal. -/
def baseIntegerEquiv :
    (integers (BaseField K s) L).comap
      (algebraMap (BaseField K s) (SpectralExtension (BaseField K s) L)) ≃+*
        𝒪[BaseField K s] :=
  RingEquiv.subringCongr (restricted_integer_subring K s L)

/-- Residue identification obtained from that literal integer-subring equality. -/
def baseResidueEquiv : BaseResidue (BaseField K s) L ≃+* 𝓀[BaseField K s] :=
  IsLocalRing.ResidueField.mapEquiv (baseIntegerEquiv K s L)

theorem baseResidue_card :
    Nat.card (BaseResidue (BaseField K s) L) = Nat.card 𝓀[BaseField K s] :=
  Nat.card_congr (baseResidueEquiv K s L).toEquiv

variable [IsGalois (BaseField K s) L]

/-- An actual automorphism lifting geometric Frobenius normalized by the residue
cardinality of Paper XI's constructed base field. -/
theorem exists_normalized_field_automorphism :
    ∃ g : SpectralExtension (BaseField K s) L ≃ₐ[BaseField K s]
        SpectralExtension (BaseField K s) L,
      residueAction (BaseField K s) L g = geometricFrobenius (BaseField K s) L ∧
      ∀ x : ExtensionResidue (BaseField K s) L,
        (residueAction (BaseField K s) L g x) ^ Nat.card 𝓀[BaseField K s] = x := by
  refine ⟨geometricLift (BaseField K s) L, residue_geometricLift _ _, ?_⟩
  intro x
  rw [← baseResidue_card K s L]
  exact geometricLift_normalized (BaseField K s) L x

end PaperXI.ConstructedFieldFrobenius
