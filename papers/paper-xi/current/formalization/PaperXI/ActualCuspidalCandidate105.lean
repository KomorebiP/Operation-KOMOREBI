import PaperXI.FullTypeIntertwining105
import PaperXI.ActualPacketTypeRealization70

/-! The actual character-dependent constructor of Block 70 now returns an
irreducible induced candidate, not a conditional promise requiring its full
intertwining locus. The residual cuspidality, arithmetic Cartan decomposition,
and BK tensor-to-residue reduction remain explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCuspidalCandidate105
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60 ActualFieldTypeQuotient69
open PaperXI.IntertwiningAlong105

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)

/-- The literal field-centralizer matrices on the original F-carrier. -/
def centralizerMap : GL m E →* GL n F :=
  (coordinateAut e).symm.toMonoidHom.comp (restrictScalarMatrix F E m)

abbrev compact := compactGroup F E m n e D θ
abbrev extended := fieldGroup F E n (scalarMatrixEmbedding F E m n e)
  (compact F E m n e D θ)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [ValuativeRel E]
  [IsNonarchimedeanLocalField E] [Nonempty n] in
/-- The scalar field action agrees with the embedding used by the old constructor. -/
theorem centralizer_scalar (c : Eˣ) :
    centralizerMap F E m n e (GeneralLinearGroup.scalar m c) =
      unitsEmbedding F E n (scalarMatrixEmbedding F E m n e) c := by
  apply (coordinateAut e).injective
  change coordinateAut e ((coordinateAut e).symm
    (restrictScalarMatrix F E m (GeneralLinearGroup.scalar m c))) = _
  rw [MulEquiv.apply_symm_apply, coordinateAut_unitsEmbedding]
  ext v i
  simp [restrictScalarMatrix_apply, Matrix.mulVec, dotProduct, Matrix.scalar_apply, Matrix.diagonal_apply]

variable (hmodel : compact F E m n e D θ ≤ matrixType F E m n e)
variable {W U : Type*} [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  [AddCommGroup U] [Module ℂ U]
  (κ : Representation ℂ (compact F E m n e D θ) W)
  (σ : Representation ℂ (GL m 𝓀[E]) U)

/-- The constructor keeps the same theta, residue map, kappa and tensor carrier.
No whole-type extension, full-H bound, or induced irreducibility is an input. -/
theorem candidate_exists
    (hF : Continuous (algebraMap F E))
    (hDo : IsOpen (D : Set (GL n F)))
    (hB : ∀ u : GL m 𝒪[E],
      (coordinateAut e).symm (integralMatrix F E m u) ∈ CharacterNormalizer61.normalizer D θ)
    (hfull : ∀ g : GL n F,
      g ∈ CharacterNormalizer61.normalizer D θ ↔
        ∃ a : Eˣ, ∃ j : compact F E m n e D θ,
          unitsEmbedding F E n (scalarMatrixEmbedding F E m n e) a * (j : GL n F) = g)
    [IsIrreducible (κ.comp (firstSubgroup F E m n e D θ).subtype)] [IsIrreducible σ]
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hβ : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      NormalizerIntertwining60.IntertwinedAt (compact F E m n e D θ) κ g)
    (π : 𝒪[E]) (hπ : (π : E) ≠ 0) (hπred : IsLocalRing.residue 𝒪[E] π = 0)
    (hCartan : CuspidalCartan105.HasCartan (ι := m) (valuation E).integer.subtype π hπ)
    (hσc : CuspidalCartan105.Cuspidal σ)
    (hBK532 : ∀ g : GL n F,
      ExistsAt (compact F E m n e D θ).subtype
        (CompactTypeTensor58.action (reduction F E m n e D θ hmodel) κ σ) g →
      ∃ j₁ j₂ : compact F E m n e D θ, ∃ y : GL m E,
        g = (j₁ : GL n F) * centralizerMap F E m n e y * (j₂ : GL n F) ∧
        ExistsAt (ActualIntegralGeneralLinear.embedding E m)
          (σ.comp (ActualResidueGeneralLinear.reduction E m)) y) :
    FiniteDimensional ℂ (W ⊗[ℂ] U) ∧
    ∃ Λ : Representation ℂ (extended F E m n e D θ) (W ⊗[ℂ] U),
      (∀ j : compact F E m n e D θ,
        Λ (PrescribedFieldType70.compactInclusion F E n (scalarMatrixEmbedding F E m n e)
          (compact F E m n e D θ) j) =
          CompactTypeTensor58.action (reduction F E m n e D θ hmodel) κ σ j) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ ∧
      FullIntertwiningLocus69.locus (extended F E m n e D θ) Λ =
        (extended F E m n e D θ : Set (GL n F)) ∧
      Function.Injective (TensorTypeOperators70.realize (extended F E m n e D θ) Λ) ∧
      Nontrivial (IndV (extended F E m n e D θ).subtype Λ) ∧
      SmoothDegreeQuotient.IsSmooth (ind (extended F E m n e D θ).subtype Λ) ∧
      IsIrreducible (ind (extended F E m n e D θ).subtype Λ) := by
  let : Fintype 𝓀[E] := Fintype.ofFinite 𝓀[E]
  obtain ⟨_, hfin, Λ, hr, _, hi, hs, hinj, _, _, hcategory⟩ :=
    ActualPacketTypeRealization70.candidate_exists F E m n e D θ hmodel κ σ
      hF hDo hB hfull hκ hβ
  let : Nontrivial (W ⊗[ℂ] U) := GeneratedIrreducibility.nontrivial_space Λ
  let hJH : compact F E m n e D θ ≤ extended F E m n e D θ := le_sup_left
  have hrestrict : Λ.comp (Subgroup.inclusion hJH) =
      CompactTypeTensor58.action (reduction F E m n e D θ hmodel) κ σ := by
    apply MonoidHom.ext
    intro j
    exact hr j
  have hI := FullTypeIntertwining105.full_locus
    (valuation E).integer.subtype (IsLocalRing.residue 𝒪[E])
    IsLocalRing.residue_surjective π hπ hπred hCartan σ hσc
    (centralizerMap F E m n e) (compact F E m n e D θ)
    (extended F E m n e D θ) hJH
    (fun u => integralMatrix_mem_compactGroup F E m n e D θ hB u)
    (fun c => (show (unitsEmbedding F E n (scalarMatrixEmbedding F E m n e)).range ≤
      extended F E m n e D θ from le_sup_right)
        ⟨c, (centralizer_scalar F E m n e c).symm⟩)
    Λ (by
      intro g hg
      rw [hrestrict] at hg
      exact hBK532 g hg)
  obtain ⟨hn, hsm, hir, _⟩ := hcategory hI
  exact ⟨hfin, Λ, hr, hi, hs, hI, hinj, hn, hsm, hir⟩

end PaperXI.ActualCuspidalCandidate105
