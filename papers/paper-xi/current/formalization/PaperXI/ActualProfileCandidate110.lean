import PaperXI.DegreeIndex110

/-! The existing actual candidate from original eta trace support, centralizer
character covariance and the oriented ambient index identity. The degree,
finite quotient and Heisenberg Hom dimension are derived, not supplied.
Actual simple-character and category instantiation remains separate. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualProfileCandidate110
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60 ActualFieldTypeQuotient69
open PaperXI.IntertwiningAlong105 ActualCuspidalCandidate105
open DegreeIndex110 IntersectionModel108

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

/-- The original candidate retains its literal theta, kappa and tensor carrier.
Its eta-dimension input is discharged from the three explicit arithmetic leaves. -/
theorem candidate_exists_from_original_profiles
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
    (hz : ∀ x : firstSubgroup F E m n e D θ,
      x ∉ actualScalarSubgroup F E m n e D θ →
      Representation.character (ActualIntersection108.restriction F E m n e D θ κ) x = 0)
    (hcov : ∀ y : GL m E,
      ∀ p : pairs (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y),
      ∀ h₁ : left (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      ∀ h₂ : right (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      actualScalarCharacter F E m n e D θ
        ⟨left (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₁⟩ =
      actualScalarCharacter F E m n e D θ
        ⟨right (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₂⟩)
    (hindex : ∀ y : GL m E,
      ((ActualIntersection108.embedding F E m n e D θ).range ⊓
        (ActualIntersection108.embedding F E m n e D θ).range.comap
          (MulAut.conj (centralizerMap F E m n e y)).toMonoidHom).relIndex
            (ActualIntersection108.embedding F E m n e D θ).range =
      (D ⊓ D.comap (MulAut.conj (centralizerMap F E m n e y)).toMonoidHom).relIndex D) :
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
  have hηdimension := DegreeIndex110.actual_eta_dimension_ambient F E m n e D θ hDc κ
    hF hDo hκ hc hz hcov hindex
  exact ActualCharacterCandidate108.candidate_exists F E m n e D θ hDc hmodel κ σ
    hF hDo hB hfull hκ hβ hσc hc hθsupport hηdimension

end PaperXI.ActualProfileCandidate110
