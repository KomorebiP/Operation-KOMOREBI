import PaperXI.HenselianGaloisResidue
import PaperXI.HenselianLiftTower
import PaperXI.FiniteResidueBaseChange
import Mathlib.Analysis.Normed.Unbundled.SpectralNorm
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.NumberTheory.LocalField.Basic

/-!
# Geometric Frobenius for a finite Galois spectral extension

The integer ring is constructed from the spectral norm of the actual extension.
Valuation stability, the Hensel property, and residue finiteness are derived.
The Frobenius-lift premise is then discharged by the inherited Galois/Hensel
surjectivity theorem. No full absolute Weil group or automorphic object is asserted.
-/
set_option autoImplicit false
noncomputable section

namespace PaperXI.SpectralGeometricFrobenius
open IsLocalRing ValuativeRel
open scoped Pointwise

variable (E L : Type*) [NontriviallyNormedField E] [IsUltrametricDist E]
  [CompleteSpace E] [ProperSpace E] [Field L] [Algebra E L]
  [FiniteDimensional E L]

/-- A transparent copy of L recording which base supplies the spectral norm. -/
def SpectralExtension (_E L : Type*) := L

instance spectralField : Field (SpectralExtension E L) := inferInstanceAs (Field L)
instance spectralAlgebra : Algebra E (SpectralExtension E L) := inferInstanceAs (Algebra E L)
instance spectralFinite : FiniteDimensional E (SpectralExtension E L) :=
  inferInstanceAs (FiniteDimensional E L)
instance spectralGalois [IsGalois E L] : IsGalois E (SpectralExtension E L) :=
  inferInstanceAs (IsGalois E L)

/-- The copy has precisely the original field and base-algebra operations. -/
def originalFieldEquiv : SpectralExtension E L ≃ₐ[E] L := AlgEquiv.refl

local notation "Lₛ" => SpectralExtension E L

private local instance extensionNorm : NormedField Lₛ := spectralNorm.normedField E Lₛ
private local instance extensionNontrivial : NontriviallyNormedField Lₛ :=
  spectralNorm.nontriviallyNormedField E Lₛ
private local instance extensionSpace : NormedSpace E Lₛ := spectralNorm.normedSpace E Lₛ
private local instance extensionAlgebra : NormedAlgebra E Lₛ := spectralNorm.normedAlgebra E Lₛ
private local instance extensionComplete : CompleteSpace Lₛ := spectralNorm.completeSpace E Lₛ
private local instance extensionProper : ProperSpace Lₛ := FiniteDimensional.proper E Lₛ
private local instance extensionUltra : IsUltrametricDist Lₛ := by
  constructor
  intro x y z
  change (spectralNorm E Lₛ (x-z) : ℝ) ≤
    max (spectralNorm E Lₛ (x-y) : ℝ) (spectralNorm E Lₛ (y-z) : ℝ)
  rw [← sub_add_sub_cancel x y z]
  exact_mod_cast isNonarchimedean_spectralNorm (K := E) (L := Lₛ) (x-y) (y-z)
private local instance extensionValued : Valued Lₛ NNReal := NormedField.toValued
private local instance extensionRel : ValuativeRel Lₛ :=
  ValuativeRel.ofValuation (NormedField.valuation (K := Lₛ))
private local instance extensionCompatible : (NormedField.valuation (K := Lₛ)).Compatible :=
  Valuation.Compatible.ofValuation _
private local instance extensionTopology : IsValuativeTopology Lₛ := by
  exact IsValuativeTopology.of_mem_nhds_zero_iff_vle
    (NormedField.valuation (K := Lₛ)) (by intro U; exact Valued.mem_nhds_zero)
private local instance extensionValNontrivial : ValuativeRel.IsNontrivial Lₛ := by
  exact (ValuativeRel.isNontrivial_iff_isNontrivial
    (NormedField.valuation (K := Lₛ))).mpr inferInstance
private local instance extensionLocalField : IsNonarchimedeanLocalField Lₛ where
  toIsValuativeTopology := inferInstance
  toLocallyCompactSpace := inferInstance
  toIsNontrivial := inferInstance

/-- The actual spectral valuation ring in the given extension field. -/
def integers : ValuationSubring Lₛ := (ValuativeRel.valuation Lₛ).valuationSubring

/-- The base integer ring, using the original norm on E. -/
def baseIntegers : ValuationSubring E := (NormedField.valuation (K := E)).valuationSubring

omit [ProperSpace E] in
/-- Spectral integrality is norm at most one. -/
theorem mem_integers (x : Lₛ) : x ∈ integers E L ↔ spectralNorm E Lₛ x ≤ 1 := by
  change ValuativeRel.valuation Lₛ x ≤ 1 ↔ _
  have h := ValuativeRel.isEquiv (NormedField.valuation (K := Lₛ))
    (ValuativeRel.valuation Lₛ) x 1
  have h' : (ValuativeRel.valuation Lₛ x ≤ 1 ↔ ‖x‖₊ ≤ 1) := by
    simpa using h.symm
  rw [h']
  change ‖x‖₊ ≤ 1 ↔ ‖x‖ ≤ 1
  exact NNReal.coe_le_coe

omit [ProperSpace E] in
/-- Restricting this valuation ring recovers the original norm-integer ring. -/
theorem integers_comap : (integers E L).comap (algebraMap E Lₛ) = baseIntegers E := by
  ext x
  change algebraMap E Lₛ x ∈ integers E L ↔ _
  rw [mem_integers]
  change spectralNorm E Lₛ (algebraMap E Lₛ x) ≤ 1 ↔ ‖x‖₊ ≤ 1
  exact_mod_cast (show spectralNorm E Lₛ (algebraMap E Lₛ x) ≤ 1 ↔ ‖x‖ ≤ 1 by
    rw [spectralNorm_extends (K := E) (L := Lₛ)])

omit [ProperSpace E] in
/-- Every base-field automorphism of the extension preserves its spectral integers. -/
theorem automorphism_stable (g : Lₛ ≃ₐ[E] Lₛ) :
    g ∈ (integers E L).decompositionSubgroup E := by
  change g • integers E L = integers E L
  ext x
  rw [ValuationSubring.mem_smul_pointwise_iff_exists]
  constructor
  · rintro ⟨y, hy, rfl⟩
    rw [mem_integers] at hy ⊢
    exact (spectralNorm_eq_of_equiv g y) ▸ hy
  · intro hx
    refine ⟨g.symm x, ?_, g.apply_symm_apply x⟩
    rw [mem_integers] at hx ⊢
    exact (spectralNorm_eq_of_equiv g.symm x) ▸ hx

instance integersDVR : IsDiscreteValuationRing (integers E L) := by
  change IsDiscreteValuationRing 𝒪[Lₛ]
  infer_instance

instance integersFiniteResidue : Finite (ResidueField (integers E L)) := by
  change Finite 𝓀[Lₛ]
  infer_instance

instance integersHenselian : HenselianLocalRing (integers E L) := by
  change HenselianLocalRing 𝒪[Lₛ]
  exact HenselianLiftTower.henselian_of_complete

abbrev BaseResidue := ResidueField ((integers E L).comap (algebraMap E Lₛ))
abbrev ExtensionResidue := ResidueField (integers E L)

private local instance baseFinite : Finite (BaseResidue E L) :=
  Finite.of_injective (ValuationResidueEmbedding.residueMap (integers E L) (algebraMap E Lₛ))
    (ValuationResidueEmbedding.residueMap_injective (integers E L) (algebraMap E Lₛ))
private local instance baseFintype : Fintype (BaseResidue E L) := Fintype.ofFinite _
private local instance upperFintype : Fintype (ExtensionResidue E L) := Fintype.ofFinite _
private local instance residueAlgebra : Algebra (BaseResidue E L) (ExtensionResidue E L) :=
  (ValuationResidueEmbedding.residueMap (integers E L) (algebraMap E Lₛ)).toAlgebra

/-- Geometric residue Frobenius is the inverse of the actual cardinality-power map. -/
def geometricFrobenius : RingAut (ExtensionResidue E L) :=
  FiniteResidueBaseChange.geometric (BaseResidue E L) (ExtensionResidue E L)

/-- Arithmetic residue Frobenius uses the original full base residue field. -/
def arithmeticFrobenius : RingAut (ExtensionResidue E L) :=
  FiniteResidueBaseChange.arithmetic (BaseResidue E L) (ExtensionResidue E L)

theorem arithmetic_apply (x : ExtensionResidue E L) :
    arithmeticFrobenius E L x = x ^ Nat.card (BaseResidue E L) := by
  simpa only [arithmeticFrobenius, Nat.card_eq_fintype_card] using
    FiniteResidueBaseChange.arithmetic_apply (BaseResidue E L) (ExtensionResidue E L) x

theorem geometric_inverse_power (x : ExtensionResidue E L) :
    geometricFrobenius E L x ^ Nat.card (BaseResidue E L) = x := by
  simpa only [geometricFrobenius, Nat.card_eq_fintype_card] using
    FiniteResidueBaseChange.geometric_inverse_power (BaseResidue E L) (ExtensionResidue E L) x

/-- The actual action on the residue field induced by field automorphisms. -/
def residueAction : (Lₛ ≃ₐ[E] Lₛ) →* RingAut (ExtensionResidue E L) :=
  HenselianGaloisResidue.residueAction E (integers E L) (automorphism_stable E L)

variable [IsGalois E L]

/-- A normalized geometric Frobenius lift exists; no residue-surjectivity premise is supplied. -/
theorem exists_geometric_lift : ∃ g : Lₛ ≃ₐ[E] Lₛ,
    residueAction E L g = geometricFrobenius E L := by
  apply HenselianGaloisResidue.lift_automorphism E (integers E L) (automorphism_stable E L)
  intro x
  exact (FiniteField.frobeniusAlgEquivOfAlgebraic (BaseResidue E L)
    (ExtensionResidue E L)).symm.commutes x

/-- A selected actual field automorphism lifting geometric Frobenius. -/
def geometricLift : Lₛ ≃ₐ[E] Lₛ := (exists_geometric_lift E L).choose

theorem residue_geometricLift :
    residueAction E L (geometricLift E L) = geometricFrobenius E L :=
  (exists_geometric_lift E L).choose_spec

/-- Arithmetic normalization of the same lift, expressed as a residue equation. -/
theorem geometricLift_normalized (x : ExtensionResidue E L) :
    (residueAction E L (geometricLift E L) x) ^ Nat.card (BaseResidue E L) = x := by
  rw [residue_geometricLift]
  exact geometric_inverse_power E L x

end PaperXI.SpectralGeometricFrobenius
