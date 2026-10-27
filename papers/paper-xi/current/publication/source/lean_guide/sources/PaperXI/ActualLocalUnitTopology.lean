import Mathlib.NumberTheory.LocalField.Basic
import Mathlib.Topology.Algebra.Group.Units
import Mathlib.Topology.Homeomorph.Lemmas

/-!
# The actual compact open unit subgroup of a nonarchimedean local field

The subgroup is the image of the unit group of the valuation ring under its
canonical embedding in the field. Its topological properties are derived from
the local-field hypotheses; they are not assumptions on an abstract subgroup.
No characteristic-zero hypothesis is used.
-/

namespace PaperXI.ActualLocalUnitTopology

open ValuativeRel

noncomputable section

variable (K : Type*) [Field K] [ValuativeRel K]

/-- The canonical homomorphism from integral units to nonzero field elements. -/
def unitEmbedding : 𝒪[K]ˣ →* Kˣ :=
  Units.map (algebraMap 𝒪[K] K).toMonoidHom

/-- The actual integral-unit subgroup of the multiplicative group of the field. -/
def compactUnitSubgroup : Subgroup Kˣ := (unitEmbedding K).range

@[simp] theorem coe_unitEmbedding (u : 𝒪[K]ˣ) :
    ((unitEmbedding K u : Kˣ) : K) = algebraMap 𝒪[K] K (u : 𝒪[K]) := rfl

theorem unitEmbedding_injective : Function.Injective (unitEmbedding K) :=
  Units.map_injective Subtype.val_injective

theorem mem_compactUnitSubgroup_iff (u : Kˣ) :
    u ∈ compactUnitSubgroup K ↔ valuation K (u : K) = 1 := by
  constructor
  · rintro ⟨v, rfl⟩
    exact (Valuation.integer.integers (valuation K)).valuation_unit v
  · intro hu
    let x : 𝒪[K] := ⟨u, hu.le⟩
    have hx : IsUnit x :=
      (Valuation.integer.integers (valuation K)).isUnit_iff_valuation_eq_one.mpr hu
    refine ⟨hx.unit, ?_⟩
    apply Units.ext
    change algebraMap 𝒪[K] K (hx.unit : 𝒪[K]) = (u : K)
    rw [hx.unit_spec]
    rfl

theorem compactUnitSubgroup_eq_units :
    compactUnitSubgroup K = (𝒪[K]).toSubmonoid.units := by
  ext u
  rw [mem_compactUnitSubgroup_iff]
  change valuation K (u : K) = 1 ↔
    valuation K (u : K) ≤ 1 ∧ valuation K ((u⁻¹ : Kˣ) : K) ≤ 1
  rw [Units.val_inv_eq_inv_val, map_inv₀,
    inv_le_one₀ (by simp [zero_lt_iff])]
  exact le_antisymm_iff

variable [TopologicalSpace K]

theorem continuous_unitEmbedding : Continuous (unitEmbedding K) :=
  (continuous_subtype_val : Continuous (algebraMap 𝒪[K] K)).units_map _

variable [IsNonarchimedeanLocalField K]

instance localFieldT2Space : T2Space K := by
  let := IsTopologicalAddGroup.rightUniformSpace K
  have := isUniformAddGroup_of_addCommGroup (G := K)
  infer_instance

/-- Compactness is inherited from the compact valuation ring via its unit group. -/
theorem isCompact_compactUnitSubgroup : IsCompact (compactUnitSubgroup K : Set Kˣ) := by
  rw [compactUnitSubgroup_eq_units]
  exact Submonoid.units_isCompact (IsNonarchimedeanLocalField.isCompact_closedBall K 1)

/-- The actual integral-unit subgroup is open in the field unit group. -/
theorem isOpen_compactUnitSubgroup : IsOpen (compactUnitSubgroup K : Set Kˣ) := by
  rw [compactUnitSubgroup_eq_units]
  apply Submonoid.isOpen_units
  exact (valuation K).isOpen_integer

/-- Integral units and their image subgroup agree as topological groups. -/
def unitEmbeddingEquiv : 𝒪[K]ˣ ≃ₜ* compactUnitSubgroup K where
  __ := MonoidHom.ofInjective (unitEmbedding_injective K)
  continuous_toFun := (continuous_unitEmbedding K).subtype_mk _
  continuous_invFun :=
    Continuous.continuous_symm_of_equiv_compact_to_t2
      (f := (MonoidHom.ofInjective (unitEmbedding_injective K)).toEquiv)
      ((continuous_unitEmbedding K).subtype_mk _)

@[simp] theorem coe_unitEmbeddingEquiv (u : 𝒪[K]ˣ) :
    ((unitEmbeddingEquiv K u : compactUnitSubgroup K) : Kˣ) = unitEmbedding K u := rfl

/-- An open set of integral units remains open in the field unit group. -/
theorem unitEmbedding_isOpenMap : IsOpenMap (unitEmbedding K) :=
  (isOpen_compactUnitSubgroup K).isOpenMap_subtype_val.comp
    (unitEmbeddingEquiv K).toHomeomorph.isOpenMap

end

end PaperXI.ActualLocalUnitTopology
