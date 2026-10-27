import PaperXI.ActualCharacterCandidate108

/-! A genuine residue-rank-one specialization. The finite residue representation
is constructed, and the full extended support follows directly from character
support because GL_1(E) consists of field scalars. No Heisenberg intersection
dimension, BK lattice index, or supplied finite cuspidal representation occurs
as an input. The actual simple-character/model/category leaves remain explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ArithmeticAttachment110
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60 ActualFieldTypeQuotient69
open ActualCuspidalCandidate105

def residueOne (k : Type*) [Field k] : Representation ℂ (GL (Fin 1) k) ℂ :=
  Representation.trivial ℂ (GL (Fin 1) k) ℂ

theorem residueOne_irreducible (k : Type*) [Field k] :
    IsIrreducible (residueOne k) := by
  apply RepresentationStability.irreducible_of_stable
  intro S _
  exact eq_bot_or_eq_top S

theorem residueOne_cuspidal (k : Type*) [Field k] :
    CuspidalCartan105.Cuspidal (residueOne k) := by
  intro S hne hproper
  exfalso
  apply hproper
  apply Finset.eq_univ_of_forall
  intro i
  obtain ⟨j, hj⟩ := hne
  simpa only [Subsingleton.elim i j] using hj

theorem gl_one_scalar {E : Type*} [CommRing E] (y : GL (Fin 1) E) :
    y = GeneralLinearGroup.scalar (Fin 1) (GeneralLinearGroup.det y) := by
  apply Units.ext
  ext i j
  fin_cases i
  fin_cases j
  simp [GeneralLinearGroup.scalar, GeneralLinearGroup.val_det_apply]

def tensorUnitEquiv {J k W : Type*} [Group J] [Field k]
    [AddCommGroup W] [Module ℂ W] (q : J →* GL (Fin 1) k)
    (κ : Representation ℂ J W) :
    Representation.Equiv (CompactTypeTensor58.action q κ (residueOne k)) κ := by
  refine Representation.Equiv.mk (TensorProduct.rid ℂ W) ?_
  intro g
  ext w
  simp [CompactTypeTensor58.action, residueOne, Representation.tprod_apply]

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (e : (Fin 1 → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)
  (hDc : D ≤ matrixCongruence F E (Fin 1) n e)
  (hmodel : compact F E (Fin 1) n e D θ ≤ matrixType F E (Fin 1) n e)
variable {W : Type*} [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  (κ : Representation ℂ (compact F E (Fin 1) n e D θ) W)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
theorem integral_normalization_of_full_rank_one
    (hfull : ∀ g : GL n F,
      g ∈ CharacterNormalizer61.normalizer D θ ↔
        ∃ a : Eˣ, ∃ j : compact F E (Fin 1) n e D θ,
          unitsEmbedding F E n (scalarMatrixEmbedding F E (Fin 1) n e) a *
            (j : GL n F) = g)
    (u : GL (Fin 1) 𝒪[E]) :
    (coordinateAut e).symm (integralMatrix F E (Fin 1) u) ∈
      CharacterNormalizer61.normalizer D θ := by
  rw [gl_one_scalar u]
  have he : (coordinateAut e).symm (integralMatrix F E (Fin 1)
      (GeneralLinearGroup.scalar (Fin 1) (GeneralLinearGroup.det u))) =
      unitsEmbedding F E n (scalarMatrixEmbedding F E (Fin 1) n e)
        (ActualLocalUnitTopology.unitEmbedding E (GeneralLinearGroup.det u)) := by
    apply (coordinateAut e).injective
    rw [MulEquiv.apply_symm_apply, coordinateAut_unitsEmbedding,
      ActualELatticeFieldJoin59.integralMatrix_scalar]
  rw [he]
  apply (hfull _).mpr
  exact ⟨ActualLocalUnitTopology.unitEmbedding E (GeneralLinearGroup.det u), 1,
    by simp⟩

theorem rank_one_candidate_exists
    (hF : Continuous (algebraMap F E))
    (hDo : IsOpen (D : Set (GL n F)))
    (hfull : ∀ g : GL n F,
      g ∈ CharacterNormalizer61.normalizer D θ ↔
        ∃ a : Eˣ, ∃ j : compact F E (Fin 1) n e D θ,
          unitsEmbedding F E n (scalarMatrixEmbedding F E (Fin 1) n e) a *
            (j : GL n F) = g)
    [IsIrreducible (κ.comp (firstSubgroup F E (Fin 1) n e D θ).subtype)]
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hβ : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      NormalizerIntertwining60.IntertwinedAt (compact F E (Fin 1) n e D θ) κ g)
    (hc : ActualCharacterData108.Contains F E (Fin 1) n e D θ hDc κ)
    (hθsupport : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ j₁ j₂ : compact F E (Fin 1) n e D θ, ∃ y : GL (Fin 1) E,
        g = (j₁ : GL n F) * centralizerMap F E (Fin 1) n e y * (j₂ : GL n F)) :
    FiniteDimensional ℂ (W ⊗[ℂ] ℂ) ∧
    ∃ Λ : Representation ℂ (extended F E (Fin 1) n e D θ) (W ⊗[ℂ] ℂ),
      (∀ j : compact F E (Fin 1) n e D θ,
        Λ (PrescribedFieldType70.compactInclusion F E n
          (scalarMatrixEmbedding F E (Fin 1) n e)
          (compact F E (Fin 1) n e D θ) j) =
          CompactTypeTensor58.action (reduction F E (Fin 1) n e D θ hmodel)
            κ (residueOne 𝓀[E]) j) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ ∧
      FullIntertwiningLocus69.locus (extended F E (Fin 1) n e D θ) Λ =
        (extended F E (Fin 1) n e D θ : Set (GL n F)) ∧
      Nontrivial (IndV (extended F E (Fin 1) n e D θ).subtype Λ) ∧
      SmoothDegreeQuotient.IsSmooth (ind (extended F E (Fin 1) n e D θ).subtype Λ) ∧
      IsIrreducible (ind (extended F E (Fin 1) n e D θ).subtype Λ) := by
  let : IsIrreducible (residueOne 𝓀[E]) := residueOne_irreducible 𝓀[E]
  have hB := integral_normalization_of_full_rank_one F E n e D θ hfull
  obtain ⟨_, hfin, Λ, hr, _, hi, hs, _, _, _, hcategory⟩ :=
    ActualPacketTypeRealization70.candidate_exists F E (Fin 1) n e D θ hmodel
      κ (residueOne 𝓀[E]) hF hDo hB hfull hκ hβ
  let : Nontrivial (W ⊗[ℂ] ℂ) := GeneratedIrreducibility.nontrivial_space Λ
  have hDJ := ActualCharacterData108.domain_le_compact F E (Fin 1) n e D θ hDc
  have hJH : compact F E (Fin 1) n e D θ ≤ extended F E (Fin 1) n e D θ :=
    le_sup_left
  have hDH : D ≤ extended F E (Fin 1) n e D θ := hDJ.trans hJH
  have hk := ActualCharacterData108.scalar_restriction F E (Fin 1) n e D θ hDc κ hc
  have hscalar : ∀ d : D,
      Λ (Subgroup.inclusion hDH d) = (θ d : ℂ) • LinearMap.id := by
    intro d
    change Λ (PrescribedFieldType70.compactInclusion F E n
      (scalarMatrixEmbedding F E (Fin 1) n e)
      (compact F E (Fin 1) n e D θ)
      (ActualCharacterData108.intoCompact F E (Fin 1) n e D θ hDc d)) = _
    rw [hr]
    ext w
    simp [CompactTypeTensor58.action, residueOne, Representation.tprod_apply, hk,
      TensorProduct.smul_tmul']
  have hI : FullIntertwiningLocus69.locus (extended F E (Fin 1) n e D θ) Λ =
      (extended F E (Fin 1) n e D θ : Set (GL n F)) := by
    apply Set.Subset.antisymm
    · intro g hg
      have hgθ := CharacterAttachment108.character_of_scalar
        (extended F E (Fin 1) n e D θ).subtype Λ D θ (Subgroup.inclusion hDH)
        (fun _ => rfl) hscalar g
        ((FullTypeIntertwining105.existsAt_iff_locus _ Λ g).mpr hg)
      obtain ⟨j₁, j₂, y, he⟩ := hθsupport g hgθ
      rw [he, gl_one_scalar y, centralizer_scalar]
      exact (extended F E (Fin 1) n e D θ).mul_mem
        ((extended F E (Fin 1) n e D θ).mul_mem (hJH j₁.property)
          ((show (unitsEmbedding F E n (scalarMatrixEmbedding F E (Fin 1) n e)).range ≤
            extended F E (Fin 1) n e D θ from le_sup_right)
            ⟨GeneralLinearGroup.det y, rfl⟩)) (hJH j₂.property)
    · exact FullIntertwiningLocus69.subgroup_subset _ Λ
  obtain ⟨hn, hsm, hir, _⟩ := hcategory hI
  exact ⟨hfin, Λ, hr, hi, hs, hI, hn, hsm, hir⟩

end PaperXI.ArithmeticAttachment110
