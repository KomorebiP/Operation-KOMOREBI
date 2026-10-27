import PaperXI.ActualLocalCartan106
import PaperXI.ActualCuspidalCandidate105

/-! The same candidate constructor with Cartan decomposition discharged from
actual local-field structure. The BK tensor reduction remains explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCartanCandidate106
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60 ActualFieldTypeQuotient69
open PaperXI.IntertwiningAlong105 ActualCuspidalCandidate105

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)

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
  let : Nonempty m := by
    classical
    by_contra h
    let : IsEmpty m := not_nonempty_iff.mp h
    have he : (0 : n → F) = 1 := e.symm.injective (Subsingleton.elim _ _)
    exact zero_ne_one he
  let π := ActualLocalUnitDecomposition.uniformizer E
  have hp0 : (π : E) ≠ 0 := ActualLocalUnitDecomposition.uniformizer_ne_zero E
  have hpred := ActualLocalCartan106.uniformizer_residue_zero E
  have hc := ActualLocalCartan106.hasCartan E m
  exact ActualCuspidalCandidate105.candidate_exists F E m n e D θ hmodel κ σ
    hF hDo hB hfull hκ hβ π hp0 hpred hc hσc hBK532

end PaperXI.ActualCartanCandidate106
