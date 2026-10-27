import PaperXI.CoordinateDeepIdeal111

/-! The actual integral coordinate-order instance and its one-plus index
application. Ideal containment and quotient finiteness are conclusions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCoordinateDeepIdeal111
open Matrix Topology ValuativeRel
open PaperXI.OnePlusIntersection110 PaperXI.CoordinateDeepIdeal111

section InnerTopology
variable {S : Type*} [Ring S] [TopologicalSpace S] [IsTopologicalRing S]

def innerHomeomorph (y : Sˣ) : S ≃ₜ S where
  toEquiv := (innerRing y).toEquiv
  continuous_toFun := by change Continuous (fun x : S => (y : S) * x * ((y⁻¹ : Sˣ) : S)); fun_prop
  continuous_invFun := by change Continuous (fun x : S => ((y⁻¹ : Sˣ) : S) * x * (y : S)); fun_prop

end InnerTopology

variable (F : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
variable (d : Type*) [Fintype d] [DecidableEq d]

/-- Entrywise inclusion of the actual coordinate integral order. -/
def integralEmbedding : Matrix d d 𝒪[F] →+* Matrix d d F :=
  RingHom.mapMatrix (valuation F).integer.subtype

theorem integralEmbedding_open : IsOpenEmbedding (integralEmbedding F d) := by
  have h : IsOpenEmbedding ((valuation F).integer.subtype : 𝒪[F] → F) :=
    (Valuation.isOpen_integer (v := valuation F)).isOpenEmbedding_subtypeVal
  exact Topology.IsOpenEmbedding.piMap
    (fun _ : d => Topology.IsOpenEmbedding.piMap (fun _ : d => h))

/-- Conjugation of an open additive lattice in the actual integral order has
open image in the external field matrix algebra. -/
theorem conjugate_lattice_open
    (L : AddSubgroup (Matrix d d 𝒪[F])) (hL : IsOpen (L : Set (Matrix d d 𝒪[F])))
    (y : GL d F) :
    IsOpen (L.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toAddMonoidHom :
      Set (Matrix d d F)) := by
  change IsOpen ((fun x => innerHomeomorph y (integralEmbedding F d x)) '' (L : Set _))
  simpa only [Set.image_image] using (innerHomeomorph y).isOpenMap _
    ((integralEmbedding_open F d).isOpenMap _ hL)

/-- An actual open additive lattice and its arbitrary conjugate contain a
common open ideal of the original compact integral order. The relevant
quotient is finite by compactness and openness. -/
theorem exists_conjugate_common_ideal
    (L : AddSubgroup (Matrix d d 𝒪[F])) (hL : IsOpen (L : Set (Matrix d d 𝒪[F])))
    (y : GL d F) :
    ∃ I : Ideal 𝒪[F], IsOpen (I : Set 𝒪[F]) ∧
      (I.matrix d).toAddSubgroup ≤ pullbackLattice (integralEmbedding F d) L
        (L.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toAddMonoidHom) ∧
      Finite (L ⧸ (I.matrix d).toAddSubgroup.addSubgroupOf L) := by
  let M := pullbackLattice (integralEmbedding F d) L
    (L.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toAddMonoidHom)
  have hM : IsOpen (M : Set (Matrix d d 𝒪[F])) :=
    hL.inter ((conjugate_lattice_open F d L hL y).preimage
      (integralEmbedding_open F d).continuous)
  obtain ⟨I, hI, hsub, hfin⟩ := exists_common_ideal_finite L M hL hM
  exact ⟨I, hI, le_trans hsub inf_le_right, hfin⟩

/-- The common-ideal and finite-quotient premises of the continuation110
one-plus theorem are discharged in the literal actual coordinate order. -/
theorem onePlus_conjugate_relIndex
    (L : AddSubgroup (Matrix d d 𝒪[F])) (hopen : IsOpen (L : Set (Matrix d d 𝒪[F])))
    (K : Subgroup (Matrix d d 𝒪[F])ˣ)
    (hK : ∀ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : (Matrix d d 𝒪[F])ˣ) : Matrix d d 𝒪[F]) = 1 + (x : _))
    (y : GL d F) :
    (K.map (Units.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toMonoidHom)).relIndex
        (K.map (Units.map (integralEmbedding F d).toMonoidHom)) =
      (L.map ((innerRing y).toRingHom.comp (integralEmbedding F d)).toAddMonoidHom).relIndex
        (L.map (integralEmbedding F d).toAddMonoidHom) := by
  obtain ⟨I, _, hI, hfin⟩ := exists_conjugate_common_ideal F d L hopen y
  let : Finite (L ⧸ (I.matrix d).toAddSubgroup.addSubgroupOf L) := hfin
  exact conjugate_intersection_relIndex_eq (integralEmbedding F d) y (I.matrix d) L K hK hL hI

end PaperXI.ActualCoordinateDeepIdeal111
