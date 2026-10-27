import PaperXI.ActualProfileCandidate110
import PaperXI.HeisenbergCharacterProfile111
import PaperXI.ActualGroupIndex111

/-! The original candidate from exact type quotient/form data and literal
one-plus/Morita lattice matches. Trace support, covariance, finite quotient,
degree-square and the ambient index equality are derived. The input record
still requires its canonical type-theoretic instance; this is not Claim16.2. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualSourceCandidate111
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60 ActualFieldTypeQuotient69
open PaperXI.IntertwiningAlong105 ActualCuspidalCandidate105
open DegreeIndex110 IntersectionModel108
open HeisenbergCharacterProfile111 ActualGroupIndex111

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

variable {k X : Type*} [Field k] [AddCommGroup X] [Module k X]

/-- Retain the original theta, kappa and tensor carrier. No trace, covariance,
eta Hom dimension, index equality, deep ideal or additive openness is assumed.
The source quotient/form and actual lattice dictionary remain explicit inputs. -/
theorem candidate_exists_from_source_dictionary
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
    (τ : ((firstSubgroup F E m n e D θ) ⧸
      actualScalarSubgroup F E m n e D θ) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ x y : firstSubgroup F E m n e D θ,
      ψ (B (coordinate (actualScalarSubgroup F E m n e D θ) τ x)
        (coordinate (actualScalarSubgroup F E m n e D θ) τ y)) =
      characterCommutator (actualScalarSubgroup F E m n e D θ) τ
        (actualScalarCharacter F E m n e D θ) x y)
    (hθcentralizer : ∀ y : GL m E, NormalizerIntertwining60.IntertwinedAt D
      (MonomialInduction.scalarRepresentation θ) (centralizerMap F E m n e y))
    (data : ActualLatticeData F E m n e D θ) :
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
  have : Nonempty m := by
    by_contra hm
    have : IsEmpty m := not_nonempty_iff.mp hm
    have h : (0 : n → F) = 1 := e.symm.injective (Subsingleton.elim _ _)
    exact zero_ne_one h
  let c : E →ₗ[F] (m → E) := LinearMap.pi (fun _ => LinearMap.id)
  have hc_inj : Function.Injective c := by
    intro x y h
    exact congrFun h (Classical.choice (inferInstance : Nonempty m))
  let : FiniteDimensional F E := FiniteDimensional.of_injective
    (e.toLinearMap.comp c) (e.injective.comp hc_inj)
  have hηdimension := actual_eta_dimension_from_quotient_form F E m n e D θ hDc κ
    hF hDo hκ hc τ B ψ hψ hnd hform hθcentralizer
    (ActualLatticeData.actual_index F n E m e D θ data hF hDo)
  exact ActualCharacterCandidate108.candidate_exists F E m n e D θ hDc hmodel κ σ
    hF hDo hB hfull hκ hβ hσc hc hθsupport hηdimension

end PaperXI.ActualSourceCandidate111
