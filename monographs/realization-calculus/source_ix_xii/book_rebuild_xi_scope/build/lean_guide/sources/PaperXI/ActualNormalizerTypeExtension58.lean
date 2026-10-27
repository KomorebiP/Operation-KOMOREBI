import PaperXI.ActualEmbeddedUniformizer58
import PaperXI.NormalizerExtensionInducing58

/-!
# Actual embedded-field normalizer extension

The noncentral matrix uniformizer's freeness is proved from compactness and
actual local-field arithmetic. Given its actual normalization of the compact
subgroup and one nonzero intertwiner, the literal representation is extended.
Simple-character normalization and beta-extension intertwining are explicit
remaining arithmetic inputs; no claim that they have been constructed is made.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualNormalizerTypeExtension58

open Matrix ValuativeRel Representation
open ActualEmbeddedUniformizer58 NormalizerExtensionInducing58

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K]
  [Field E] [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]
  [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (ι : E →ₐ[K] Matrix n n K)
variable (J : Subgroup (GeneralLinearGroup n K))
  (ht : embeddedUniformizer K E n ι ∈ Subgroup.normalizer (J : Set (GeneralLinearGroup n K)))

omit [ValuativeRel K] [TopologicalSpace K] [IsNonarchimedeanLocalField K] [Nonempty n] in
/-- With integral E-units in J, the generated subgroup is exactly the join
of J and the actual embedded multiplicative group of E. -/
theorem extendedSubgroup_eq_field_join
    (hunits : ∀ u : 𝒪[E]ˣ,
      unitsEmbedding K E n ι (ActualLocalUnitTopology.unitEmbedding E u) ∈ J) :
    extendedSubgroup J (embeddedUniformizer K E n ι) ht =
      J ⊔ (unitsEmbedding K E n ι).range := by
  apply le_antisymm
  · rw [extendedSubgroup_eq_sup]
    apply sup_le le_sup_left
    apply Subgroup.zpowers_le.mpr
    exact (show (unitsEmbedding K E n ι).range ≤ J ⊔ (unitsEmbedding K E n ι).range from
      le_sup_right) ⟨ActualLocalUnitDecomposition.uniformizerUnit E, rfl⟩
  · apply sup_le (le_extendedSubgroup J (embeddedUniformizer K E n ι) ht)
    rintro g ⟨a, rfl⟩
    obtain ⟨r, j, hj⟩ := field_product_normalForm K E n ι J hunits a 1
    have he : unitsEmbedding K E n ι a = embeddedUniformizer K E n ι ^ r * j := by
      simpa using hj
    rw [he]
    exact Subgroup.mul_mem _
      (Subgroup.zpow_mem _ (generator_mem J (embeddedUniformizer K E n ι) ht) r)
      (le_extendedSubgroup J (embeddedUniformizer K E n ι) ht j.property)

variable {V : Type*} [AddCommGroup V] [Module ℂ V]
  (σ : Representation ℂ J V)

/-- Actual matrix-field freeness discharges the cyclic extension obstruction.
One nonzero actual intertwiner produces a smooth irreducible extension on the
literal ambient subgroup. Neither centrality nor induced-category conclusions
are assumed. -/
theorem exists_smooth_irreducible_extension
    (hK : Continuous (algebraMap K E))
    (hcompact : IsCompact (J : Set (GeneralLinearGroup n K)))
    (hopen : IsOpen (J : Set (GeneralLinearGroup n K)))
    [IsIrreducible σ] (hsmooth : SmoothDegreeQuotient.IsSmooth σ)
    (T : IntertwiningMap σ
      (σ.comp (conjugation J (embeddedUniformizer K E n ι) ht).toMonoidHom))
    (hT : T ≠ 0) :
    ∃ Λ : Representation ℂ (extendedSubgroup J (embeddedUniformizer K E n ι) ht) V,
      (∀ j : J, Λ (subgroupInclusion J (embeddedUniformizer K E n ι) ht j) = σ j) ∧
      Λ (generator J (embeddedUniformizer K E n ι) ht) = T.toLinearMap ∧
      IsIrreducible Λ ∧ SmoothDegreeQuotient.IsSmooth Λ := by
  let t := embeddedUniformizer K E n ι
  have hfree := embeddedUniformizer_free_of_algebraMap K E n ι hK J hcompact
  let e := T.ofBijective (intertwiner_bijective J t ht σ T hT)
  refine ⟨extensionOfEquiv J t ht σ e hfree, ?_, ?_, ?_, ?_⟩
  · intro j
    exact extensionOfEquiv_restrict J t ht σ e hfree j
  · exact extensionOfEquiv_generator J t ht σ e hfree
  · exact extendedRepresentation_irreducible J t ht σ _ _ hfree
  · exact extendedRepresentation_smooth J t ht σ _ _ hfree hopen hsmooth

end PaperXI.ActualNormalizerTypeExtension58
