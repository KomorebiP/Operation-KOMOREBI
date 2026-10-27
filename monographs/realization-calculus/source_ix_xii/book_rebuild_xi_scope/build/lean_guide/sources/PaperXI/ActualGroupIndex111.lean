import PaperXI.ActualCoordinateDeepIdeal111
import PaperXI.ActualOnePlusTopology111
import PaperXI.MoritaEndomorphismCoordinates111
import PaperXI.MoritaPairIndex110
import PaperXI.MoritaRadicalDictionary110
import PaperXI.DegreeIndex110

/-! The exact ambient group index from two supplied open coordinate lattices
and two finite full Morita lattices. Canonical H1/J1 identifications remain
source matches; no index identity or common ideal is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualGroupIndex111
open Matrix Module ValuativeRel Topology
open PaperXI.OnePlusIntersection110 PaperXI.ActualCoordinateDeepIdeal111
open PaperXI.MoritaLattice110 PaperXI.MoritaCornerRank110
open PaperXI.MoritaActualCartan110 PaperXI.MoritaRadicalDictionary110
open PaperXI.MoritaEndomorphismCoordinates111

section GroupOrientation
variable {S : Type*} [Ring S]

/-- Ring conjugation by g inverse is the inverse group conjugation map. -/
theorem units_innerRing_inv (g : Sˣ) :
    Units.map (innerRing g⁻¹).toMonoidHom = (MulAut.conj g).symm.toMonoidHom := by
  ext u
  change (g⁻¹ : Sˣ) * (u : S) * ((g⁻¹)⁻¹ : Sˣ) =
    ((MulAut.conj g).symm u : S)
  rw [MulAut.conj_symm_apply]
  simp only [Units.val_mul, inv_inv]

/-- The literal g-inverse image is the g-conjugation pullback. -/
theorem map_inner_inv_eq_comap (K : Subgroup Sˣ) (g : Sˣ) :
    K.map (Units.map (innerRing g⁻¹).toMonoidHom) =
      K.comap (MulAut.conj g).toMonoidHom := by
  rw [units_innerRing_inv]
  exact Subgroup.map_equiv_eq_comap_symm' (MulAut.conj g).symm K

end GroupOrientation

variable (F : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
variable (n : Type*) [Fintype n] [DecidableEq n]

omit [TopologicalSpace F] [IsNonarchimedeanLocalField F] in
/-- This is the actual existing entrywise integral general-linear embedding. -/
theorem integralUnitMap_eq_actualEmbedding :
    Units.map (integralEmbedding F n).toMonoidHom =
      ActualIntegralGeneralLinear.embedding F n := rfl

/-- At the literal first-coordinate orientation, the common deep ideal is
constructed from openness rather than supplied as an arithmetic hypothesis. -/
theorem onePlus_backward_relIndex
    (L : AddSubgroup (Matrix n n 𝒪[F])) (hopen : IsOpen (L : Set (Matrix n n 𝒪[F])))
    (K : Subgroup (Matrix n n 𝒪[F])ˣ)
    (hK : ∀ u : K, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L)
    (hL : ∀ x : L, ∃ u : K, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (g : GL n F) :
    ((K.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj g).toMonoidHom).relIndex
          (K.map (ActualIntegralGeneralLinear.embedding F n)) =
    ((L.map (integralEmbedding F n).toAddMonoidHom) ⊓
      (L.map (integralEmbedding F n).toAddMonoidHom).map
        (innerRing g⁻¹).toAddMonoidHom).relIndex
          (L.map (integralEmbedding F n).toAddMonoidHom) := by
  have h := onePlus_conjugate_relIndex F n L hopen K hK hL g⁻¹
  have hm : Units.map
      ((innerRing g⁻¹).toRingHom.comp (integralEmbedding F n)).toMonoidHom =
      (Units.map (innerRing g⁻¹).toMonoidHom).comp
        (Units.map (integralEmbedding F n).toMonoidHom) := rfl
  rw [hm, ← Subgroup.map_map, map_inner_inv_eq_comap,
    integralUnitMap_eq_actualEmbedding] at h
  have ha : L.map
      ((innerRing g⁻¹).toRingHom.comp (integralEmbedding F n)).toAddMonoidHom =
      (L.map (integralEmbedding F n).toAddMonoidHom).map
        (innerRing g⁻¹).toAddMonoidHom := by
    change L.map ((innerRing g⁻¹).toAddMonoidHom.comp
      (integralEmbedding F n).toAddMonoidHom) = _
    exact (AddSubgroup.map_map L (innerRing g⁻¹).toAddMonoidHom
      (integralEmbedding F n).toAddMonoidHom).symm
  rw [ha] at h
  simpa only [Subgroup.inf_relIndex_left, AddSubgroup.inf_relIndex_left] using h


variable (E : Type*) [Field E] [Algebra F E] [Module.Finite F E]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]
variable (m : Type*) [Fintype m] [DecidableEq m] [Nonempty m]

omit [Module.Finite F E] [ValuativeRel E] [IsNonarchimedeanLocalField E] [Nonempty m] in
/-- Explicit lattice image matching transports the one-plus group index to the
original Morita carrier, with the required inverse centralizer orientation. -/
theorem onePlus_index_of_Morita_image
    (e : (m → E) ≃L[F] (n → F))
    (L : AddSubgroup (Matrix n n 𝒪[F])) (hopen : IsOpen (L : Set (Matrix n n 𝒪[F])))
    (K : Subgroup (Matrix n n 𝒪[F])ˣ)
    (hK : ∀ u : K, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L)
    (hL : ∀ x : L, ∃ u : K, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (M : AddSubgroup (Matrix m m (Module.End F E)))
    (himage : L.map (integralEmbedding F n).toAddMonoidHom =
      M.map (coordinateRingEquiv F E m n e).toAddMonoidHom)
    (y : GL m E) :
    ((K.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (K.map (ActualIntegralGeneralLinear.embedding F n)) =
    (M ⊓ M.map (unitConjugation (centralizerEmbedding F E m y⁻¹)).toAddMonoidHom).relIndex M := by
  have h := onePlus_backward_relIndex F n L hopen K hK hL
    (ActualCuspidalCandidate105.centralizerMap F E m n e y)
  rw [himage] at h
  have hy : coordinateUnitMap F E m n e (centralizerEmbedding F E m y⁻¹) =
      (ActualCuspidalCandidate105.centralizerMap F E m n e y)⁻¹ := by
    rw [coordinateUnitMap_centralizer, map_inv]
  have ha : (innerRing (ActualCuspidalCandidate105.centralizerMap F E m n e y)⁻¹).toAddMonoidHom =
      (unitConjugation (coordinateUnitMap F E m n e
        (centralizerEmbedding F E m y⁻¹))).toAddMonoidHom := by
    rw [hy]
    rfl
  rw [ha] at h
  exact h.trans (coordinate_intersection_relIndex F E m n e M
    (centralizerEmbedding F E m y⁻¹))

/-- Two actual numerical Cartan formulas at the same inverse y prove the
ambient H/J index equality. All one-plus and lattice image matches are literal. -/
theorem ambient_pair_index
    (e : (m → E) ≃L[F] (n → F))
    (L₁ L₂ : AddSubgroup (Matrix n n 𝒪[F]))
    (hopen₁ : IsOpen (L₁ : Set (Matrix n n 𝒪[F])))
    (hopen₂ : IsOpen (L₂ : Set (Matrix n n 𝒪[F])))
    (K₁ K₂ : Subgroup (Matrix n n 𝒪[F])ˣ)
    (hK₁ : ∀ u : K₁, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L₁)
    (hL₁ : ∀ x : L₁, ∃ u : K₁, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (hK₂ : ∀ u : K₂, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L₂)
    (hL₂ : ∀ x : L₂, ∃ u : K₂, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (M₁ M₂ : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (himage₁ : L₁.map (integralEmbedding F n).toAddMonoidHom =
      M₁.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom)
    (himage₂ : L₂.map (integralEmbedding F n).toAddMonoidHom =
      M₂.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom)
    (hM₁ : IsMatrixBimodule (coefficientMap F E) M₁.toAddSubgroup)
    (hM₂ : IsMatrixBimodule (coefficientMap F E) M₂.toAddSubgroup)
    (hfg₁ : M₁.FG) (hfg₂ : M₂.FG)
    (hfull₁ : Submodule.span F (M₁ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hfull₂ : Submodule.span F (M₂ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm₁ : RadicalCommutes F E m M₁.toAddSubgroup)
    (hcomm₂ : RadicalCommutes F E m M₂.toAddSubgroup) (y : GL m E) :
    ((K₁.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K₁.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (K₁.map (ActualIntegralGeneralLinear.embedding F n)) =
    ((K₂.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K₂.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (K₂.map (ActualIntegralGeneralLinear.embedding F n)) := by
  rw [onePlus_index_of_Morita_image F n E m e L₁ hopen₁ K₁ hK₁ hL₁
      M₁.toAddSubgroup himage₁ y,
    onePlus_index_of_Morita_image F n E m e L₂ hopen₂ K₂ hK₂ hL₂
      M₂.toAddSubgroup himage₂ y]
  exact MoritaPairIndex110.actual_pair_index F E m M₁ M₂ hM₁ hM₂
    hfg₁ hfg₂ hfull₁ hfull₂ hcomm₁ hcomm₂ y⁻¹

/-- Source-style radical-product equalities supply both scalar-radical premises. -/
theorem ambient_pair_index_of_radical_products
    (e : (m → E) ≃L[F] (n → F))
    (L₁ L₂ : AddSubgroup (Matrix n n 𝒪[F]))
    (hopen₁ : IsOpen (L₁ : Set (Matrix n n 𝒪[F])))
    (hopen₂ : IsOpen (L₂ : Set (Matrix n n 𝒪[F])))
    (K₁ K₂ : Subgroup (Matrix n n 𝒪[F])ˣ)
    (hK₁ : ∀ u : K₁, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L₁)
    (hL₁ : ∀ x : L₁, ∃ u : K₁, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (hK₂ : ∀ u : K₂, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L₂)
    (hL₂ : ∀ x : L₂, ∃ u : K₂, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _))
    (M₁ M₂ : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (himage₁ : L₁.map (integralEmbedding F n).toAddMonoidHom =
      M₁.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom)
    (himage₂ : L₂.map (integralEmbedding F n).toAddMonoidHom =
      M₂.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom)
    (hM₁ : IsMatrixBimodule (coefficientMap F E) M₁.toAddSubgroup)
    (hM₂ : IsMatrixBimodule (coefficientMap F E) M₂.toAddSubgroup)
    (hfg₁ : M₁.FG) (hfg₂ : M₂.FG)
    (hfull₁ : Submodule.span F (M₁ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hfull₂ : Submodule.span F (M₂ : Set (Matrix m m (Module.End F E))) = ⊤)
    (hrad₁ : additiveProduct (actualRadical F E m) M₁.toAddSubgroup =
      additiveProduct M₁.toAddSubgroup (actualRadical F E m))
    (hrad₂ : additiveProduct (actualRadical F E m) M₂.toAddSubgroup =
      additiveProduct M₂.toAddSubgroup (actualRadical F E m)) (y : GL m E) :
    ((K₁.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K₁.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (K₁.map (ActualIntegralGeneralLinear.embedding F n)) =
    ((K₂.map (ActualIntegralGeneralLinear.embedding F n)) ⊓
      (K₂.map (ActualIntegralGeneralLinear.embedding F n)).comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (K₂.map (ActualIntegralGeneralLinear.embedding F n)) :=
  ambient_pair_index F n E m e L₁ L₂ hopen₁ hopen₂ K₁ K₂ hK₁ hL₁ hK₂ hL₂
    M₁ M₂ himage₁ himage₂ hM₁ hM₂ hfg₁ hfg₂ hfull₁ hfull₂
    (RadicalCommutes_of_actual_radical_products F E m M₁.toAddSubgroup hM₁ hrad₁)
    (RadicalCommutes_of_actual_radical_products F E m M₂.toAddSubgroup hM₂ hrad₂) y

/-- Exact source matches only. Openness, common deep ideals, finite congruence
quotients and the final relative-index identity are not fields of this data. -/
structure ActualLatticeData
    (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
    [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
    [IsNonarchimedeanLocalField E] [Algebra F E]
    (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
    [Nonempty n] (e : (m → E) ≃L[F] (n → F))
    (D : Subgroup (GL n F)) (θ : D →* ℂˣ) where
  L1 : AddSubgroup (Matrix n n 𝒪[F])
  L2 : AddSubgroup (Matrix n n 𝒪[F])
  K1 : Subgroup (Matrix n n 𝒪[F])ˣ
  K2 : Subgroup (Matrix n n 𝒪[F])ˣ
  offsets1 : ∀ u : K1, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L1
  onePlus1 : ∀ x : L1, ∃ u : K1,
    ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _)
  offsets2 : ∀ u : K2, ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) - 1 ∈ L2
  onePlus2 : ∀ x : L2, ∃ u : K2,
    ((u : (Matrix n n 𝒪[F])ˣ) : Matrix n n 𝒪[F]) = 1 + (x : _)
  M1 : Submodule 𝒪[E] (Matrix m m (Module.End F E))
  M2 : Submodule 𝒪[E] (Matrix m m (Module.End F E))
  image1 : L1.map (integralEmbedding F n).toAddMonoidHom =
    M1.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom
  image2 : L2.map (integralEmbedding F n).toAddMonoidHom =
    M2.toAddSubgroup.map (coordinateRingEquiv F E m n e).toAddMonoidHom
  bimodule1 : IsMatrixBimodule (coefficientMap F E) M1.toAddSubgroup
  bimodule2 : IsMatrixBimodule (coefficientMap F E) M2.toAddSubgroup
  finite1 : M1.FG
  finite2 : M2.FG
  full1 : Submodule.span F (M1 : Set (Matrix m m (Module.End F E))) = ⊤
  full2 : Submodule.span F (M2 : Set (Matrix m m (Module.End F E))) = ⊤
  radical1 : additiveProduct (actualRadical F E m) M1.toAddSubgroup =
    additiveProduct M1.toAddSubgroup (actualRadical F E m)
  radical2 : additiveProduct (actualRadical F E m) M2.toAddSubgroup =
    additiveProduct M2.toAddSubgroup (actualRadical F E m)
  groupImage1 : K1.map (ActualIntegralGeneralLinear.embedding F n) =
    (ActualIntersection108.embedding F E m n e D θ).range
  groupImage2 : K2.map (ActualIntegralGeneralLinear.embedding F n) = D

variable [Nonempty n]

/-- The exact H/J index hypothesis consumed by the original-character
candidate. Existing open-group hypotheses derive lattice openness; the actual
Cartan formulas then supply the index at the required inverse orientation. -/
theorem ActualLatticeData.actual_index
    (e : (m → E) ≃L[F] (n → F)) (D : Subgroup (GL n F)) (θ : D →* ℂˣ)
    (data : ActualLatticeData F E m n e D θ)
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (y : GL m E) :
    ((ActualIntersection108.embedding F E m n e D θ).range ⊓
      (ActualIntersection108.embedding F E m n e D θ).range.comap
        (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex
          (ActualIntersection108.embedding F E m n e D θ).range =
    (D ⊓ D.comap
      (MulAut.conj (ActualCuspidalCandidate105.centralizerMap F E m n e y)).toMonoidHom).relIndex D := by
  have ho1 : IsOpen
      (data.K1.map (Units.map (integralEmbedding F n).toMonoidHom) : Set (GL n F)) := by
    rw [integralUnitMap_eq_actualEmbedding, data.groupImage1]
    exact DegreeIndex110.actual_embedding_range_open F E m n e D θ hF hDo
  have ho2 : IsOpen
      (data.K2.map (Units.map (integralEmbedding F n).toMonoidHom) : Set (GL n F)) := by
    rw [integralUnitMap_eq_actualEmbedding, data.groupImage2]
    exact hDo
  have hL1 := ActualOnePlusTopology111.additive_open_of_image_group_open
    F n data.L1 data.K1 data.offsets1 data.onePlus1 ho1
  have hL2 := ActualOnePlusTopology111.additive_open_of_image_group_open
    F n data.L2 data.K2 data.offsets2 data.onePlus2 ho2
  have h := ambient_pair_index_of_radical_products F n E m e data.L1 data.L2
    hL1 hL2 data.K1 data.K2 data.offsets1 data.onePlus1 data.offsets2 data.onePlus2
    data.M1 data.M2 data.image1 data.image2 data.bimodule1 data.bimodule2
    data.finite1 data.finite2 data.full1 data.full2 data.radical1 data.radical2 y
  simpa only [data.groupImage1, data.groupImage2] using h

end PaperXI.ActualGroupIndex111
