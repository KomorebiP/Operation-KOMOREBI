import KomorebiLSM.DecoderMatrixFormula

set_option autoImplicit false
namespace Komorebi.LSM.FiniteTableP32
open Komorebi.LSM.Spectral Komorebi.LSM.BasisCoordinates
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- P32's basis conditioning, coordinate injection, exact inverse and inverse norm,
for any orthonormal bases of the true and data-selected ranges. The spectral and
projection assertions are `Spectral.finite_table_stability`; the literal matrix
formula is `BasisCoordinates.decoder_matrix_formula`. -/
theorem coordinates_and_decoder (X N : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ X.toLinearMap.range) (ε : ℝ)
    (hnoise : ‖N‖ ≤ ε) (hsmall : ε < leastPositive X.toLinearMap / 2)
    (U : OrthonormalBasis (Fin (Module.finrank ℝ X.toLinearMap.range)) ℝ X.toLinearMap.range)
    (V : OrthonormalBasis (Fin (Module.finrank ℝ X.toLinearMap.range)) ℝ (learnedLeft X N)) :
    Real.sqrt (1-(2*ε/leastPositive X.toLinearMap)^2) ≤
      (cross U V).toEuclideanLin.singularValues (Module.finrank ℝ X.toLinearMap.range-1) ∧
    Function.Injective ((coordinates V).comp X.toLinearMap.range.subtypeL) ∧
    (∀ x : X.toLinearMap.range, decoder U V (coordinates V (x:F)) = (x:F)) ∧
    (∀ y : EuclideanSpace ℝ (Fin (Module.finrank ℝ X.toLinearMap.range)),
      coordinates V (decoder U V y) = y) ∧
    ‖decoder U V‖ ≤ (Real.sqrt (1-(2*ε/leastPositive X.toLinearMap)^2))⁻¹ := by
  obtain ⟨_,_,hg,hs⟩ := finite_table_stability X N hr ε hnoise hsmall
  have hε : 0 ≤ ε := (norm_nonneg N).trans hnoise
  have hδ : 0 ≤ 2*ε/leastPositive X.toLinearMap :=
    div_nonneg (mul_nonneg (by norm_num) hε) (leastPositive_pos X.toLinearMap hr).le
  exact ⟨cross_min_singular U V hr _ hδ hs hg,
    coordinates_injective V _ hδ hs hg,
    decoder_coordinates U V _ hδ hs hg,
    coordinates_decoder U V _ hδ hs hg,
    decoder_norm_bound U V _ hδ hs hg⟩

end Komorebi.LSM.FiniteTableP32
