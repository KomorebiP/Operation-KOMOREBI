import PaperXI.ActualCoordinateDeepIdeal111
import PaperXI.ActualIntegralGeneralLinear
import Mathlib.Topology.Algebra.IsOpenUnits
import Mathlib.Topology.Instances.Matrix

/-! Openness of an actual one-plus group supplies additive lattice openness. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualOnePlusTopology111
open Matrix Topology
open PaperXI.ActualCoordinateDeepIdeal111 PaperXI.OnePlusIntersection110

section MatrixUnits
variable (F d : Type*) [Field F] [TopologicalSpace F] [IsTopologicalRing F]
  [ContinuousInv₀ F] [T1Space F] [Fintype d] [DecidableEq d]

/-- The actual matrix unit topology agrees with the open nonzero-determinant
subspace, using continuity of the nonsingular matrix inverse there. -/
def matrixUnitsHomeomorph : (Matrix d d F)ˣ ≃ₜ {A : Matrix d d F | A.det ≠ 0} where
  toFun u := ⟨u, (Matrix.isUnits_det_units u).ne_zero⟩
  invFun A := ⟨A.1, A.1⁻¹,
    Matrix.mul_nonsing_inv A.1 (isUnit_iff_ne_zero.mpr A.2),
    Matrix.nonsing_inv_mul A.1 (isUnit_iff_ne_zero.mpr A.2)⟩
  left_inv u := by apply Units.ext; rfl
  right_inv A := rfl
  continuous_toFun := Units.continuous_val.subtype_mk _
  continuous_invFun := by
    apply Units.continuous_iff.mpr
    refine ⟨continuous_subtype_val, ?_⟩
    change Continuous (fun A : {A : Matrix d d F | A.det ≠ 0} => A.1⁻¹)
    apply continuous_iff_continuousAt.mpr
    intro A
    apply (continuousAt_matrix_inv A.1 ?_).comp continuous_subtype_val.continuousAt
    simpa only [Ring.inverse_eq_inv'] using (continuousAt_inv₀ A.2)

/-- This is derived for actual matrices; no matrix open-units instance is
assumed as an input. -/
theorem matrix_isOpenUnits : IsOpenUnits (Matrix d d F) := by
  have hoF : IsOpen {x : F | x ≠ 0} := isOpen_ne
  have ho : IsOpen {A : Matrix d d F | A.det ≠ 0} :=
    hoF.preimage continuous_id.matrix_det
  exact ⟨ho.isOpenEmbedding_subtypeVal.comp (matrixUnitsHomeomorph F d).isOpenEmbedding⟩

end MatrixUnits

section ActualLocalField
open ValuativeRel
variable (F : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
variable (d : Type*) [Fintype d] [DecidableEq d]

/-- Actual local-field matrices have an open unit embedding. -/
theorem actual_matrix_isOpenUnits : IsOpenUnits (Matrix d d F) := by
  let : T2Space F := PaperXI.ActualIntegralGeneralLinear.field_t2Space F
  exact matrix_isOpenUnits F d

/-- Exact one-plus carrier identities turn openness of the actual ambient
image group into openness of its additive integral-order lattice. -/
theorem additive_open_of_image_group_open
    (L : AddSubgroup (Matrix d d 𝒪[F])) (K : Subgroup (Matrix d d 𝒪[F])ˣ)
    (hK : ∀ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) = 1 + (x : _))
    (hopen : IsOpen (K.map (Units.map (integralEmbedding F d).toMonoidHom) :
      Set (GL d F))) : IsOpen (L : Set (Matrix d d 𝒪[F])) := by
  let : IsOpenUnits (Matrix d d F) := actual_matrix_isOpenUnits F d
  let f := integralEmbedding F d
  let H := K.map (Units.map f.toMonoidHom)
  have hu : IsOpen ((Units.val : (Matrix d d F)ˣ → Matrix d d F) '' (H : Set _)) :=
    IsOpenUnits.isOpenEmbedding_unitsVal.isOpenMap _ hopen
  have hoff : IsOpen ((fun x : Matrix d d F => x - 1) ''
      ((Units.val : (Matrix d d F)ˣ → Matrix d d F) '' (H : Set _))) :=
    (Homeomorph.subRight (1 : Matrix d d F)).isOpenMap _ hu
  have he : ((fun x : Matrix d d F => x - 1) ''
      ((Units.val : (Matrix d d F)ˣ → Matrix d d F) '' (H : Set _))) =
        (L.map f.toAddMonoidHom : Set (Matrix d d F)) := by
    ext x
    constructor
    · rintro ⟨_, ⟨g, hg, rfl⟩, rfl⟩
      exact mapped_offsets f L K hK ⟨g, hg⟩
    · intro hx
      obtain ⟨g, hg⟩ := mapped_onePlus f L K hL ⟨x, hx⟩
      refine ⟨(g : (Matrix d d F)ˣ), ⟨g, g.property, rfl⟩, ?_⟩
      rw [hg]
      simp
  rw [he] at hoff
  have hinj : Function.Injective f := Matrix.map_injective Subtype.val_injective
  have hpre : f ⁻¹' (L.map f.toAddMonoidHom : Set (Matrix d d F)) =
      (L : Set (Matrix d d 𝒪[F])) := by
    ext x
    constructor
    · rintro ⟨z, hz, he⟩
      exact hinj he ▸ hz
    · intro hx
      exact ⟨x, hx, rfl⟩
  rw [← hpre]
  exact hoff.preimage (integralEmbedding_open F d).continuous

/-- Both lattice openness and the common ideal/finite quotient now follow from
actual group openness and exact one-plus carriers. -/
theorem onePlus_conjugate_relIndex_of_group_open
    (L : AddSubgroup (Matrix d d 𝒪[F])) (K : Subgroup (Matrix d d 𝒪[F])ˣ)
    (hK : ∀ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) = 1 + (x : _))
    (hopen : IsOpen (K.map (Units.map (integralEmbedding F d).toMonoidHom) : Set (GL d F)))
    (y : GL d F) :
    (K.map (Units.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toMonoidHom)).relIndex
        (K.map (Units.map (integralEmbedding F d).toMonoidHom)) =
      (L.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toAddMonoidHom).relIndex
        (L.map (integralEmbedding F d).toAddMonoidHom) :=
  onePlus_conjugate_relIndex F d L
    (additive_open_of_image_group_open F d L K hK hL hopen) K hK hL y

end ActualLocalField
end PaperXI.ActualOnePlusTopology111
