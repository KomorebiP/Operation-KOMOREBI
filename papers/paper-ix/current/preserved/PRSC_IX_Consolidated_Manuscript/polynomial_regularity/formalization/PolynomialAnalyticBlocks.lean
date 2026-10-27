module
public import PolynomialAnalyticEvaluation
public import PolynomialBlockInverse

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialAnalyticBlocks
open Matrix
open Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialBlockInverse
open Komorebi.PolynomialAnalyticEvaluation

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜] [CompleteSpace 𝕜]
variable {e k : ℕ}

/-- The actual augmented derivative is a continuous linear equivalence whenever
its solved block is invertible. Its inverse is the explicit triangular block matrix. -/
def upperEquiv (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) :
    (Fin (e+k) → 𝕜) ≃L[𝕜] (Fin (e+k) → 𝕜) := by
  let B := upperBlock J K (1 : 𝕜)
  let C := blockCertificate J⁻¹ K (1 : 𝕜)
  have hdet := (Matrix.isUnit_iff_isUnit_det J).mp hJ
  have hCB : C * B = 1 := by
    simpa only [one_smul] using blockCertificate_mul J⁻¹ J K (1 : 𝕜)
      (by simpa only [one_smul] using Matrix.nonsing_inv_mul J hdet)
  have hBC : B * C = 1 := by
    simpa only [one_smul] using mul_blockCertificate J⁻¹ J K (1 : 𝕜)
      (by simpa only [one_smul] using Matrix.mul_nonsing_inv J hdet)
  refine (LinearEquiv.ofLinearMap B.mulVecLin C.mulVecLin ?_ ?_).toContinuousLinearEquiv
  · apply LinearMap.ext
    intro v
    change B.mulVec (C.mulVec v) = v
    rw [Matrix.mulVec_mulVec, hBC, Matrix.one_mulVec]
  · apply LinearMap.ext
    intro v
    change C.mulVec (B.mulVec v) = v
    rw [Matrix.mulVec_mulVec, hCB, Matrix.one_mulVec]

@[simp] theorem upperEquiv_apply (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) (v : Fin (e+k) → 𝕜) :
    upperEquiv J K hJ v = (upperBlock J K 1).mulVec v := rfl

@[simp] theorem upperEquiv_symm_apply (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) (v : Fin (e+k) → 𝕜) :
    (upperEquiv J K hJ).symm v = (blockCertificate J⁻¹ K 1).mulVec v := rfl

/-- The continuous derivative equivalence is the actual matrix action. -/
theorem upperEquiv_toCLM (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) :
    (upperEquiv J K hJ : (Fin (e+k) → 𝕜) →L[𝕜] (Fin (e+k) → 𝕜)) =
      matrixCLM (upperBlock J K 1) := by
  ext v i
  rfl

/-- Restricting the inverse derivative to parameter targets gives exactly -J⁻¹K. -/
theorem inverse_solved_zero (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) (v : Fin k → 𝕜) :
    solvedPart ((upperEquiv J K hJ).symm (join (0 : Fin e → 𝕜) v)) =
      matrixCLM (-(J⁻¹ * K)) v := by
  rw [upperEquiv_symm_apply]
  simp only [blockCertificate, upperBlock_mulVec_join, Matrix.mulVec_zero,
    zero_add, solvedPart_join]
  rfl

/-- The inverse derivative preserves the prescribed parameter increment exactly. -/
theorem inverse_free_zero (J : Matrix (Fin e) (Fin e) 𝕜)
    (K : Matrix (Fin e) (Fin k) 𝕜) (hJ : IsUnit J) (v : Fin k → 𝕜) :
    freePart ((upperEquiv J K hJ).symm (join (0 : Fin e → 𝕜) v)) = v := by
  rw [upperEquiv_symm_apply]
  simp only [blockCertificate, upperBlock_mulVec_join, freePart_join, one_smul]

end Komorebi.PolynomialAnalyticBlocks
