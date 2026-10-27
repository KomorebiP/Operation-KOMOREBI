import PaperXI.ArithmeticAttachment110
import PaperXI.NormalizerDictionary110

/-! Residue rank one from the lower-level simple-character support dictionary.
The model containment, compact support, integral normalization and finite
residue factor are derived. Canonical character data are not manufactured. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.RankOneSourceCandidate110
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCuspidalCandidate105
open ActualELatticeTopology60 LatticeCongruenceTopology60 ActualELatticeResidue59
open ActualEmbeddedUniformizer58

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (e : (Fin 1 → E) ≃L[F] (n → F))
  (D J₁ : Subgroup (GL n F)) (θ : D →* ℂˣ)
  (hDc : D ≤ matrixCongruence F E (Fin 1) n e)
variable {W : Type*} [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  (κ : Representation ℂ (compact F E (Fin 1) n e D θ) W)

/-- The original carrier and compact restriction are retained. No supplied
sigma, model inclusion, compact support, integral normalization, eta Hom
dimension, trace profile or lattice-index identity is an input in this branch. -/
theorem candidate_exists
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hJ : J₁ ≤ matrixCongruence F E (Fin 1) n e)
    (hJN : J₁ ≤ CharacterNormalizer61.normalizer D θ)
    (hθcentralizer : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ a : J₁, ∃ b : (centralizerMap F E (Fin 1) n e).range,
      ∃ c : J₁, (a : GL n F) * (b : GL n F) * (c : GL n F) = g)
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
    (hc : ActualCharacterData108.Contains F E (Fin 1) n e D θ hDc κ) :
    FiniteDimensional ℂ (W ⊗[ℂ] ℂ) ∧
    ∃ Λ : Representation ℂ (extended F E (Fin 1) n e D θ) (W ⊗[ℂ] ℂ),
      (∀ j : compact F E (Fin 1) n e D θ,
        Λ (PrescribedFieldType70.compactInclusion F E n
          (scalarMatrixEmbedding F E (Fin 1) n e)
          (compact F E (Fin 1) n e D θ) j) =
          (κ.tprod (Representation.trivial ℂ (compact F E (Fin 1) n e D θ) ℂ)) j) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ ∧
      FullIntertwiningLocus69.locus (extended F E (Fin 1) n e D θ) Λ =
        (extended F E (Fin 1) n e D θ : Set (GL n F)) ∧
      Nontrivial (IndV (extended F E (Fin 1) n e D θ).subtype Λ) ∧
      SmoothDegreeQuotient.IsSmooth (ind (extended F E (Fin 1) n e D θ).subtype Λ) ∧
      IsIrreducible (ind (extended F E (Fin 1) n e D θ).subtype Λ) := by
  have hB := ArithmeticAttachment110.integral_normalization_of_full_rank_one
    F E n e D θ hfull
  have hmodel := NormalizerDictionary110.actual_model_from_centralizer
    F E (Fin 1) n e D θ J₁ hJ hJN hθcentralizer hB
  have hs := NormalizerDictionary110.character_support_compact
    F E (Fin 1) n e D θ J₁ hJ hJN hθcentralizer
  obtain ⟨hf, Λ, hr, hi, hsm, hI, hn, hsi, hir⟩ :=
    ArithmeticAttachment110.rank_one_candidate_exists F E n e D θ hDc hmodel κ
      hF hDo hfull hκ hβ hc hs
  refine ⟨hf, Λ, ?_, hi, hsm, hI, hn, hsi, hir⟩
  intro j
  rw [hr]
  ext w
  simp [CompactTypeTensor58.action, ArithmeticAttachment110.residueOne,
    Representation.tprod_apply]

end PaperXI.RankOneSourceCandidate110
