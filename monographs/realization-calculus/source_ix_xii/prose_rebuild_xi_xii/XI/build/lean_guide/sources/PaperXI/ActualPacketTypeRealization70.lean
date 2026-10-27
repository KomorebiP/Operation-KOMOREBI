import PaperXI.PacketTypeAttachment70
import PaperXI.PrescribedFieldType70
import PaperXI.ArithmeticTypeCertificate69
import PaperXI.ActualCharacterIdentification61
import PaperXI.ActualCharacterResidue61

/-! Same-theta, same-kappa construction at the actual residue map and field join.
This replaces the old compact-subgroup Mackey premise by a full-locus condition
on the newly constructed extension. Standard character/type leaves remain
explicit; this is not a formalization of their classification theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualPacketTypeRealization70
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualCharacterType61 ActualCharacterIdentification61 ActualCharacterResidue61
open ActualELatticeTopology60 ActualELatticeResidue59 ActualEmbeddedUniformizer58
open LatticeCongruenceTopology60
open NormalizerExtensionInducing58 ActualFieldTypeQuotient69

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GeneralLinearGroup n F)) (θ : D →* ℂˣ)

variable (hmodel : (compactGroup F E m n e D θ) ≤ matrixType F E m n e)
variable {W U : Type*} [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  [AddCommGroup U] [Module ℂ U]
  (κ : Representation ℂ (compactGroup F E m n e D θ) W) (σ : Representation ℂ (GeneralLinearGroup m 𝓀[E]) U)

/-- Construct the exact arithmetic extended tensor type. All later full-locus
and induced-category claims refer to this same Lambda. No arbitrary Atom type,
assumed whole-type irreducibility, or compact-J off-normalizer bound is used. -/
theorem candidate_exists
    (hF : Continuous (algebraMap F E))
    (hDo : IsOpen (D : Set (GeneralLinearGroup n F)))
    (hB : ∀ b : GeneralLinearGroup m 𝒪[E],
      (coordinateAut e).symm (integralMatrix F E m b) ∈ CharacterNormalizer61.normalizer D θ)
    (hfull : ∀ g : GeneralLinearGroup n F,
      g ∈ CharacterNormalizer61.normalizer D θ ↔
        ∃ a : Eˣ, ∃ j : (compactGroup F E m n e D θ), unitsEmbedding F E n (scalarMatrixEmbedding F E m n e) a * (j : GeneralLinearGroup n F) = g)
    [IsIrreducible (κ.comp (firstSubgroup F E m n e D θ).subtype)] [IsIrreducible σ]
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hβ : ∀ g : GeneralLinearGroup n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      NormalizerIntertwining60.IntertwinedAt (compactGroup F E m n e D θ) κ g) :
    (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) = CharacterNormalizer61.normalizer D θ ∧
    FiniteDimensional ℂ (W ⊗[ℂ] U) ∧
    ∃ Λ : Representation ℂ (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) (W ⊗[ℂ] U),
      (∀ j : (compactGroup F E m n e D θ), Λ (PrescribedFieldType70.compactInclusion F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ) j) =
        CompactTypeTensor58.action (reduction F E m n e D θ hmodel) κ σ j) ∧
      (∃ A : Module.End ℂ W, A ≠ 0 ∧
        ∀ w u, Λ (PrescribedFieldType70.fieldGenerator F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) (w ⊗ₜ[ℂ] u) =
          A w ⊗ₜ[ℂ] u) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ ∧
      Function.Injective (TensorTypeOperators70.realize (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ) ∧
      (∀ j : (firstSubgroup F E m n e D θ), PacketTypeAttachment70.typeAction (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ
        (PrescribedFieldType70.compactInclusion F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ) (j : (compactGroup F E m n e D θ))) =
          TensorTypeOperators70.realize (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ (κ (j : (compactGroup F E m n e D θ)))) ∧
      (∀ xs : List (Module.End ℂ W),
        (xs.map (TensorTypeOperators70.realize (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ)).prod = 1 ↔ xs.prod = 1) ∧
      (FullIntertwiningLocus69.locus (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ = ((fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) : Set (GeneralLinearGroup n F)) →
        Nontrivial (IndV (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)).subtype Λ) ∧
        SmoothDegreeQuotient.IsSmooth (ind (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)).subtype Λ) ∧
        IsIrreducible (ind (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)).subtype Λ) ∧
        (∀ f : IntertwiningMap Λ ((ind (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)).subtype Λ).comp (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)).subtype), f ≠ 0 →
          LinearMap.range f.toLinearMap = InducedTypeSpace68.typeSpace (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ)) := by
  have hθ := uniformizer_mem_full_normalizer F E m n e D θ (compactGroup F E m n e D θ) hfull
  let ht := uniformizer_normalizes_compactGroup F E m n e D θ hθ
  have htop := compactGroup_compact_open F E m n e D θ hF hDo
  have hu := integralUnit_mem_compactGroup F E m n e D θ hB
  have hq := reduction_surjective F E m n e D θ hmodel hB
  have hN : (firstSubgroup F E m n e D θ) ≤ (reduction F E m n e D θ hmodel).ker := (reduction_kernel F E m n e D θ hmodel).ge
  obtain ⟨T, hT⟩ := NormalizerIntertwining60.exists_normalizerIntertwiner (compactGroup F E m n e D θ) κ (embeddedUniformizer F E n (scalarMatrixEmbedding F E m n e)) ht
    (hβ (embeddedUniformizer F E n (scalarMatrixEmbedding F E m n e)) (CharacterNormalizer61.character_intertwinedAt D θ hθ))
  obtain ⟨hf, Λ, hr, hg, hi, hs⟩ := PrescribedFieldType70.exists_prescribed_extension
    F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ) ht hu (firstSubgroup F E m n e D θ) (reduction F E m n e D θ hmodel) hN κ σ hF htop.1 htop.2
    (firstSubgroup_open F E m n e D θ hF) hq
    (reduction_conjugation F E m n e D θ hmodel hθ) hκ T hT
  have hdom : (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) = CharacterNormalizer61.normalizer D θ := by
    change (compactGroup F E m n e D θ) ⊔ (unitsEmbedding F E n (scalarMatrixEmbedding F E m n e)).range = _
    rw [← ActualNormalizerTypeExtension58.extendedSubgroup_eq_field_join F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ) ht hu]
    exact extendedSubgroup_eq_full_normalizer F E m n e D θ (compactGroup F E m n e D θ) hF inf_le_right hu hfull
  let : Nontrivial U := GeneratedIrreducibility.nontrivial_space σ
  refine ⟨hdom, hf, Λ, hr, ⟨T.toLinearMap, ?_, hg⟩, hi, hs,
    TensorTypeOperators70.realize_injective (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ, ?_,
    TensorTypeOperators70.holonomy_iff (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ, ?_⟩
  · intro hz
    apply hT
    ext w
    exact LinearMap.congr_fun hz w
  · intro j
    exact PacketTypeAttachment70.first_factor_action (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ
      (PrescribedFieldType70.compactInclusion F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) (reduction F E m n e D θ hmodel) κ σ hr
      (j : (compactGroup F E m n e D θ)) (hN j.property)
  · intro hI
    let : FiniteDimensional ℂ (W ⊗[ℂ] U) := hf
    let : IsIrreducible Λ := hi
    obtain ⟨hn, hsm, hir, _⟩ := ArithmeticTypeCertificate69.from_full_intertwining_locus
      F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ) Λ hF htop.1 htop.2 ht hu hs hI
    refine ⟨hn, hsm, hir, ?_⟩
    let : Nontrivial (W ⊗[ℂ] U) := GeneratedIrreducibility.nontrivial_space Λ
    intro f hf0
    exact InducedTypeSpace68.range_eq_identity (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ
      ((FullIntertwiningLocus69.locus_eq_iff (fieldGroup F E n (scalarMatrixEmbedding F E m n e) (compactGroup F E m n e D θ)) Λ).mp hI) f hf0

end PaperXI.ActualPacketTypeRealization70
