import KomorebiLSM.SingularPerturbation
import KomorebiLSM.LeftSingularModes

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- Data-selected left subspace, with the true table's rank as truncation level. -/
noncomputable def learnedLeft (X N : E →L[ℝ] F) : Submodule ℝ F :=
  leadingLeft (X+N).toLinearMap (Module.finrank ℝ X.toLinearMap.range)
    (LinearMap.finrank_range_le X.toLinearMap)

theorem noisy_rank_lower (X N : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ X.toLinearMap.range) (ε : ℝ)
    (hnoise : ‖N‖ ≤ ε) (hsmall : ε < leastPositive X.toLinearMap / 2) :
    Module.finrank ℝ X.toLinearMap.range ≤ Module.finrank ℝ (X+N).toLinearMap.range := by
  have hl := noisy_singular_lower X N ε hnoise (Module.finrank ℝ X.toLinearMap.range-1)
  have hp := leastPositive_pos X.toLinearMap hr
  change leastPositive X.toLinearMap - ε ≤ _ at hl
  have hy : 0 < (X+N).toLinearMap.singularValues (Module.finrank ℝ X.toLinearMap.range-1) := by
    linarith
  have hh := (X+N).toLinearMap.singularValues_pos_iff_lt_finrank_range.mp hy
  omega

theorem learnedLeft_finrank (X N : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ X.toLinearMap.range) (ε : ℝ)
    (hnoise : ‖N‖ ≤ ε) (hsmall : ε < leastPositive X.toLinearMap / 2) :
    Module.finrank ℝ (learnedLeft X N) = Module.finrank ℝ X.toLinearMap.range :=
  leadingLeft_finrank _ _ _ (noisy_rank_lower X N hr ε hnoise hsmall)

theorem learnedLeft_observed_tail (X N : E →L[ℝ] F) (ε : ℝ) (hnoise : ‖N‖ ≤ ε) :
    ‖(learnedLeft X N)ᗮ.starProjection.comp (X+N)‖ ≤ ε := by
  change ‖(leadingLeft (X+N).toLinearMap _ _)ᗮ.starProjection.comp (X+N)‖ ≤ ε
  rw [leadingLeft_tail_norm]
  exact noisy_tail_at_rank X N ε hnoise

/-- The spectral and projection conclusions of P32 now follow from the noisy
operators alone. The estimated subspace and its tail are constructed. -/
theorem finite_table_stability (X N : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ X.toLinearMap.range) (ε : ℝ)
    (hnoise : ‖N‖ ≤ ε) (hsmall : ε < leastPositive X.toLinearMap / 2) :
    leastPositive X.toLinearMap - ε ≤
      (X+N).toLinearMap.singularValues (Module.finrank ℝ X.toLinearMap.range-1) ∧
    (X+N).toLinearMap.singularValues (Module.finrank ℝ X.toLinearMap.range) ≤ ε ∧
    ‖X.toLinearMap.range.starProjection-(learnedLeft X N).starProjection‖ ≤
      2*ε/leastPositive X.toLinearMap ∧
    2*ε/leastPositive X.toLinearMap < 1 := by
  have hε : 0 ≤ ε := (norm_nonneg N).trans hnoise
  refine ⟨noisy_singular_lower X N ε hnoise _, noisy_tail_at_rank X N ε hnoise, ?_⟩
  exact gap_from_observed_tail X N (learnedLeft X N) hr ε hε hsmall
    (learnedLeft_observed_tail X N ε hnoise) hnoise
    (learnedLeft_finrank X N hr ε hnoise hsmall).symm

/-- The zero-padded spectrum also implements the maximum possible rank convention. -/
theorem singularValue_zero_at_max_rank (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : min (Module.finrank ℝ E) (Module.finrank ℝ F) ≤ k) :
    A.singularValues k = 0 := by
  apply A.singularValues_eq_zero_iff_le_finrank_range.mpr
  exact (le_min (LinearMap.finrank_range_le A) (Submodule.finrank_le A.range)).trans hk

end Komorebi.LSM.Spectral
