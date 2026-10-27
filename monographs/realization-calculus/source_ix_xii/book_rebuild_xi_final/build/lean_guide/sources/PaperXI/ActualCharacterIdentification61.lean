import PaperXI.ActualCharacterType61

/-!
# Identification with the supplied genuine compact type group

The exact standard-theory input is the actual full character-normalizer
formula N(theta)=E^× J0, together with integral E-units in J0 and preservation
of the lattice chain. These imply that the constructed compact intersection
is literally J0. No equality J1=U_a1 is used or concluded.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCharacterIdentification61
open Matrix ValuativeRel
open ActualCharacterType61 ActualELatticeTopology60 ActualEmbeddedUniformizer58
open NormalizerExtensionInducing58 ActualLocalUnitTopology

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra K E]
variable (n d : Type*) [Fintype n] [DecidableEq n] [Fintype d] [DecidableEq d]
  [Nonempty d] (e : (n → E) ≃L[K] (d → K))
variable (H : Subgroup (GeneralLinearGroup d K)) (θ : H →* ℂˣ)
variable (J0 : Subgroup (GeneralLinearGroup d K))

/-- The exact full-normalizer formula identifies the actual compact intersection with genuine J0. -/
theorem compactGroup_eq_of_full_normalizer (hK : Continuous (algebraMap K E))
    (hJ : J0 ≤ chainGroup K E n d e)
    (hu : ∀ u : 𝒪[E]ˣ,
      unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) (unitEmbedding E u) ∈ J0)
    (hfull : ∀ g : GeneralLinearGroup d K,
      g ∈ CharacterNormalizer61.normalizer H θ ↔
        ∃ a : Eˣ, ∃ j : J0,
          unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) a * (j : GeneralLinearGroup d K) = g) :
    compactGroup K E n d e H θ = J0 := by
  apply le_antisymm
  · intro g hg
    obtain ⟨a, j, he⟩ := (hfull g).mp hg.1
    obtain ⟨r, k, hr⟩ := field_product_normalForm K E d
      (scalarMatrixEmbedding K E n d e) J0 hu a j
    have hgk : embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ^ r =
        g * (k : GeneralLinearGroup d K)⁻¹ := by
      rw [← he, hr]
      group
    have hm : embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ^ r ∈
        chainGroup K E n d e := by
      rw [hgk]
      exact (chainGroup K E n d e).mul_mem hg.2 ((chainGroup K E n d e).inv_mem (hJ k.property))
    have hz := embeddedUniformizer_free_of_algebraMap K E d
      (scalarMatrixEmbedding K E n d e) hK (chainGroup K E n d e)
      (chainGroup_compact K E n d e hK) r hm
    have hg' : g = k := by rw [← he, hr, hz, zpow_zero, one_mul]
    exact hg' ▸ k.property
  · intro j hj
    exact ⟨(hfull j).mpr ⟨1, ⟨j, hj⟩, by simp⟩, hJ hj⟩

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- The same exact formula supplies actual uniformizer covariance of theta. -/
theorem uniformizer_mem_full_normalizer
    (hfull : ∀ g : GeneralLinearGroup d K,
      g ∈ CharacterNormalizer61.normalizer H θ ↔
        ∃ a : Eˣ, ∃ j : J0,
          unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) a * (j : GeneralLinearGroup d K) = g) :
    embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ∈
      CharacterNormalizer61.normalizer H θ :=
  (hfull _).mpr ⟨ActualLocalUnitDecomposition.uniformizerUnit E, 1, by simp [embeddedUniformizer]⟩

/-- The actual constructed extension domain is the full normalizer of the same theta. -/
theorem extendedSubgroup_eq_full_normalizer (hK : Continuous (algebraMap K E))
    (hJ : J0 ≤ chainGroup K E n d e)
    (hu : ∀ u : 𝒪[E]ˣ,
      unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) (unitEmbedding E u) ∈ J0)
    (hfull : ∀ g : GeneralLinearGroup d K,
      g ∈ CharacterNormalizer61.normalizer H θ ↔
        ∃ a : Eˣ, ∃ j : J0,
          unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) a * (j : GeneralLinearGroup d K) = g) :
    extendedSubgroup (compactGroup K E n d e H θ)
      (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e))
      (uniformizer_normalizes_compactGroup K E n d e H θ
        (uniformizer_mem_full_normalizer K E n d e H θ J0 hfull)) =
      CharacterNormalizer61.normalizer H θ := by
  let C := compactGroup K E n d e H θ
  let t := embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e)
  let ht := uniformizer_normalizes_compactGroup K E n d e H θ
    (uniformizer_mem_full_normalizer K E n d e H θ J0 hfull)
  have hC := compactGroup_eq_of_full_normalizer K E n d e H θ J0 hK hJ hu hfull
  apply le_antisymm
  · rw [extendedSubgroup_eq_sup]
    exact sup_le inf_le_left (Subgroup.zpowers_le.mpr
      (uniformizer_mem_full_normalizer K E n d e H θ J0 hfull))
  · intro g hg
    obtain ⟨a, j, he⟩ := (hfull g).mp hg
    obtain ⟨r, k, hr⟩ := field_product_normalForm K E d
      (scalarMatrixEmbedding K E n d e) J0 hu a j
    rw [← he, hr]
    exact (extendedSubgroup C t ht).mul_mem
      ((extendedSubgroup C t ht).zpow_mem (generator_mem C t ht) r)
      (le_extendedSubgroup C t ht (hC.symm ▸ k.property))

end PaperXI.ActualCharacterIdentification61
