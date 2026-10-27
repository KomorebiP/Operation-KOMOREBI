import PaperXI.ActualCompactTypeCompletion58
import PaperXI.ActualFieldTypeQuotient69

/-! Construction of the full inducing representation from the same compact
first factor and actual finite quotient. The full-H locus is a later condition
on this exact constructed extension, not on an unrelated supplied Lambda. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PrescribedFieldType70
open Matrix ValuativeRel Representation
open scoped TensorProduct
open ActualEmbeddedUniformizer58 ActualFieldTypeQuotient69 NormalizerExtensionInducing58

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (ι : E →ₐ[F] Matrix n n F) (J : Subgroup (GeneralLinearGroup n F))
  (ht : embeddedUniformizer F E n ι ∈ Subgroup.normalizer (J : Set (GeneralLinearGroup n F)))
  (hu : ∀ u : 𝒪[E]ˣ, unitsEmbedding F E n ι (ActualLocalUnitTopology.unitEmbedding E u) ∈ J)
variable {Q W U : Type*} [Group Q] [Finite Q]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  [AddCommGroup U] [Module ℂ U]
variable (N : Subgroup J) (q : J →* Q) (hN : N ≤ q.ker)
  (κ : Representation ℂ J W) (σ : Representation ℂ Q U)

/-- Literal inclusion of the compact group into the field-generated subgroup. -/
def compactInclusion : J →* fieldGroup F E n ι J := Subgroup.inclusion le_sup_left

/-- The actual extension-field uniformizer in the field-generated subgroup. -/
def fieldGenerator : fieldGroup F E n ι J :=
  ⟨embeddedUniformizer F E n ι, (show (unitsEmbedding F E n ι).range ≤ fieldGroup F E n ι J from le_sup_right)
    ⟨ActualLocalUnitDecomposition.uniformizerUnit E, rfl⟩⟩

/-- Identifies the previously constructed normalizer coordinates with the
literal arithmetic field join. Its underlying ambient map is the identity. -/
def domainEquiv : extendedSubgroup J (embeddedUniformizer F E n ι) ht ≃*
    fieldGroup F E n ι J := MulEquiv.subgroupCongr
  (ActualNormalizerTypeExtension58.extendedSubgroup_eq_field_join F E n ι J ht hu)

include hu hN in
/-- On the actual arithmetic group, construct the extension and retain both
its compact action and its exact first-factor uniformizer operator. -/
theorem exists_prescribed_extension
    (hF : Continuous (algebraMap F E))
    (hJc : IsCompact (J : Set (GeneralLinearGroup n F)))
    (hJo : IsOpen (J : Set (GeneralLinearGroup n F)))
    (hNo : IsOpen (N : Set J)) (hq : Function.Surjective q)
    (hqa : ∀ j, q (conjugation J (embeddedUniformizer F E n ι) ht j) = q j)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ]
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (T : IntertwiningMap κ (κ.comp (conjugation J (embeddedUniformizer F E n ι) ht).toMonoidHom))
    (hT : T ≠ 0) :
    FiniteDimensional ℂ (W ⊗[ℂ] U) ∧
    ∃ Λ : Representation ℂ (fieldGroup F E n ι J) (W ⊗[ℂ] U),
      (∀ j : J, Λ (compactInclusion F E n ι J j) = CompactTypeTensor58.action q κ σ j) ∧
      (∀ w u, Λ (fieldGenerator F E n ι J) (w ⊗ₜ[ℂ] u) = T w ⊗ₜ[ℂ] u) ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ := by
  obtain ⟨hf, _, _, _, L, hr, hg, hi, hs⟩ :=
    ActualCompactTypeCompletion58.completed F E n ι J ht N q hN κ σ
      hF hJc hJo hNo hq hqa hκ T hT
  let e := domainEquiv F E n ι J ht hu
  let Λ := L.comp e.symm.toMonoidHom
  have hei (j : J) : e.symm (compactInclusion F E n ι J j) =
      subgroupInclusion J (embeddedUniformizer F E n ι) ht j := Subtype.ext rfl
  have heg : e.symm (fieldGenerator F E n ι J) =
      generator J (embeddedUniformizer F E n ι) ht := Subtype.ext rfl
  have hLs : SmoothDegreeQuotient.IsSmooth Λ := by
    intro x
    have he : (SmoothDegreeQuotient.vectorStabilizer Λ x : Set (fieldGroup F E n ι J)) =
        e.symm ⁻¹' (SmoothDegreeQuotient.vectorStabilizer L x : Set _) := rfl
    rw [he]
    have hc : Continuous e.symm := continuous_subtype_val.subtype_mk _
    exact (hs x).preimage hc
  let : IsIrreducible L := hi
  have hLi : IsIrreducible Λ :=
    (QuotientRepresentation.irreducible_comp_iff e.symm.toMonoidHom e.symm.surjective L).mpr hi
  refine ⟨hf, Λ, ?_, ?_, hLi, hLs⟩
  · intro j
    change L (e.symm (compactInclusion F E n ι J j)) = _
    rw [hei, hr]
  · intro w u
    change L (e.symm (fieldGenerator F E n ι J)) (w ⊗ₜ[ℂ] u) = _
    rw [heg]
    exact hg w u

end PaperXI.PrescribedFieldType70
