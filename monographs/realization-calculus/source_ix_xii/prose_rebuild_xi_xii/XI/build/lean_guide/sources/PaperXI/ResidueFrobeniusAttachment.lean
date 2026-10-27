import PaperXI.IntegerRingComparison
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.FieldTheory.Galois.Basic
import Mathlib.GroupTheory.SpecificGroups.Cyclic

/-! # Frobenius attachment to the constructed residue field -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.FiniteUnramifiedWeil

open PaperXI.LocalFieldResidueExtension
open PaperXI.IntegerRingComparison
open ValuativeRel
open scoped Classical Polynomial

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

abbrev UpperField := LocalFieldResidueExtension.field K s
abbrev BaseResidue := 𝓀[K]
abbrev UpperResidue := 𝓀[UpperField K s]
abbrev ResidueGalois := UpperResidue K s ≃ₐ[BaseResidue K] UpperResidue K s
abbrev ResidueDegree := Module.finrank K (UpperField K s)

private local instance baseResidueFintype : Fintype (BaseResidue K) :=
  Fintype.ofFinite _

private local instance upperResidueFintype : Fintype (UpperResidue K s) :=
  Fintype.ofFinite _

/-- Arithmetic Frobenius on the actual residue field of the constructed local field. -/
noncomputable def arithmeticFrobenius : ResidueGalois K s :=
  FiniteField.frobeniusAlgEquivOfAlgebraic (BaseResidue K) (UpperResidue K s)

/-- Geometric Frobenius is the inverse of arithmetic Frobenius. -/
noncomputable def geometricFrobenius : ResidueGalois K s :=
  (arithmeticFrobenius K s)⁻¹

@[simp]
theorem arithmeticFrobenius_apply (x : UpperResidue K s) :
    arithmeticFrobenius K s x = x ^ Fintype.card (BaseResidue K) :=
  rfl

@[simp]
theorem geometricFrobenius_inverse_power (x : UpperResidue K s) :
    geometricFrobenius K s x ^ Fintype.card (BaseResidue K) = x := by
  rw [← arithmeticFrobenius_apply K s]
  exact (arithmeticFrobenius K s).apply_symm_apply x

/-- Arithmetic Frobenius has order equal to the spectral residue degree. -/
theorem arithmeticFrobenius_order :
    orderOf (arithmeticFrobenius K s) =
      Module.finrank (BaseResidue K) (UpperResidue K s) :=
  FiniteField.orderOf_frobeniusAlgEquivOfAlgebraic _ _

/-- Geometric Frobenius has the same exact order. -/
theorem geometricFrobenius_order :
    orderOf (geometricFrobenius K s) =
      Module.finrank (BaseResidue K) (UpperResidue K s) := by
  rw [geometricFrobenius, orderOf_inv, arithmeticFrobenius_order]

/-- Frobenius order agrees with the degree of the constructed local-field extension. -/
theorem arithmeticFrobenius_order_eq_fieldDegree :
    orderOf (arithmeticFrobenius K s) = ResidueDegree K s := by
  rw [arithmeticFrobenius_order]
  exact (upper_degree_eq_spectral_residue_finrank K s).symm

/-- Geometric Frobenius order agrees with the field degree. -/
theorem geometricFrobenius_order_eq_fieldDegree :
    orderOf (geometricFrobenius K s) = ResidueDegree K s := by
  rw [geometricFrobenius_order]
  exact (upper_degree_eq_spectral_residue_finrank K s).symm

/-- The residue Galois group has cardinality equal to the upper field degree. -/
theorem natCard_residueGalois :
    Nat.card (ResidueGalois K s) = ResidueDegree K s := by
  rw [IsGalois.card_aut_eq_finrank]
  exact (upper_degree_eq_spectral_residue_finrank K s).symm

/-- Every residue automorphism is an integral power of arithmetic Frobenius. -/
theorem arithmeticFrobenius_mem_zpowers (σ : ResidueGalois K s) :
    σ ∈ Subgroup.zpowers (arithmeticFrobenius K s) := by
  obtain ⟨n, hn⟩ :=
    (FiniteField.bijective_frobeniusAlgEquivOfAlgebraic_pow
      (BaseResidue K) (UpperResidue K s)).2 σ
  rw [Subgroup.mem_zpowers_iff]
  refine ⟨(n.1 : ℤ), ?_⟩
  simpa [arithmeticFrobenius, zpow_natCast] using hn

/-- Arithmetic Frobenius generates the full residue Galois group. -/
theorem arithmeticFrobenius_zpowers_eq_top :
    Subgroup.zpowers (arithmeticFrobenius K s) = ⊤ := by
  rw [Subgroup.eq_top_iff']
  exact arithmeticFrobenius_mem_zpowers K s

/-- Geometric Frobenius also generates the full residue Galois group. -/
theorem geometricFrobenius_zpowers_eq_top :
    Subgroup.zpowers (geometricFrobenius K s) = ⊤ := by
  rw [geometricFrobenius, Subgroup.zpowers_inv,
    arithmeticFrobenius_zpowers_eq_top]

/-- Explicit cyclic coordinates in which one is geometric Frobenius. -/
noncomputable def geometricCycleEquiv :
    Multiplicative (ZMod (ResidueDegree K s)) ≃* ResidueGalois K s :=
  zmodMulEquivOfGenerator
    (fun σ => by
      rw [geometricFrobenius_zpowers_eq_top K s]
      trivial)
    (natCard_residueGalois K s)

@[simp]
theorem geometricCycleEquiv_one :
    geometricCycleEquiv K s (Multiplicative.ofAdd 1) = geometricFrobenius K s :=
  zmodMulEquivOfGenerator_apply_ofAdd_one _ _

/-- Galois groups of the spectral residue field and the prescribed residue field
are conjugate through the checked residue-field equivalence. -/
noncomputable def prescribedResidueGaloisEquiv :
    ResidueGalois K s ≃* (s ≃ₐ[BaseResidue K] s) :=
  AlgEquiv.autCongr (spectralResidueAlgEquiv K s)

/-- Arithmetic Frobenius is transported literally to arithmetic Frobenius on `s`. -/
theorem prescribedResidueGaloisEquiv_arithmetic :
    prescribedResidueGaloisEquiv K s (arithmeticFrobenius K s) =
      FiniteField.frobeniusAlgEquivOfAlgebraic (BaseResidue K) s := by
  apply AlgEquiv.ext
  intro x
  let e := spectralResidueAlgEquiv K s
  change e ((e.symm x) ^ Fintype.card (BaseResidue K)) =
    x ^ Fintype.card (BaseResidue K)
  rw [map_pow, e.apply_symm_apply]

/-- Geometric Frobenius is transported literally to geometric Frobenius on `s`. -/
theorem prescribedResidueGaloisEquiv_geometric :
    prescribedResidueGaloisEquiv K s (geometricFrobenius K s) =
      (FiniteField.frobeniusAlgEquivOfAlgebraic (BaseResidue K) s)⁻¹ := by
  rw [geometricFrobenius, map_inv, prescribedResidueGaloisEquiv_arithmetic]


end PaperXI.FiniteUnramifiedWeil
