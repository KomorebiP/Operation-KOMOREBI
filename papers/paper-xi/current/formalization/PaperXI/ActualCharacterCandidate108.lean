import PaperXI.ActualCharacterData108

/-! Character attachment removes a redundant beta-support input. Character
support and the Heisenberg Hom dimension are still arithmetic hypotheses. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCharacterCandidate108
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

variable (hDc : D ≤ matrixCongruence F E m n e)
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
    (hc : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (hθsupport : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ j₁ j₂ : compact F E m n e D θ, ∃ y : GL m E,
        g = (j₁ : GL n F) * centralizerMap F E m n e y * (j₂ : GL n F))
    (hηdimension : ∀ y : GL m E,
      Module.finrank ℂ (IntertwiningSpace107.space
        ((compact F E m n e D θ).subtype.comp (firstSubgroup F E m n e D θ).subtype)
        (κ.comp (firstSubgroup F E m n e D θ).subtype) (centralizerMap F E m n e y)) = 1) :
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
  have hs := ActualCharacterData108.scalar_restriction F E m n e D θ hDc κ hc
  have hDJ := ActualCharacterData108.domain_le_compact F E m n e D θ hDc
  have hDN := ActualCharacterData108.intoCompact_mem_first F E m n e D θ hDc
  have hηsupport : ∀ g : GL n F,
      ExistsAt ((compact F E m n e D θ).subtype.comp
        (firstSubgroup F E m n e D θ).subtype)
        (κ.comp (firstSubgroup F E m n e D θ).subtype) g →
      ∃ j₁ j₂ : compact F E m n e D θ, ∃ y : GL m E,
        g = (j₁ : GL n F) * centralizerMap F E m n e y * (j₂ : GL n F) := by
    intro g hg
    exact hθsupport g ((CharacterSupport108.restricted_iff_character D
      (compact F E m n e D θ) hDJ (firstSubgroup F E m n e D θ) hDN θ κ hs hβ g).mp hg)
  have hβB : ∀ y : GL m E,
      ExistsAt (compact F E m n e D θ).subtype κ (centralizerMap F E m n e y) := by
    intro y
    exact CharacterSupport108.beta_of_dimension_pos D (compact F E m n e D θ)
      hDJ (firstSubgroup F E m n e D θ) hDN θ κ hs hβ (centralizerMap F E m n e y)
      (by rw [hηdimension]; exact Nat.zero_lt_one)
  exact ActualHeisenbergCandidate107.candidate_exists F E m n e D θ hmodel κ σ
    hF hDo hB hfull hκ hβ hσc hηsupport hηdimension hβB

end PaperXI.ActualCharacterCandidate108
