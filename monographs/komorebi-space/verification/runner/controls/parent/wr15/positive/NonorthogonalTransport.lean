import KomorebiSpace.CoordinateBasisChange

set_option autoImplicit false
open Matrix KomorebiSpace.CoordinateCovector

private def C : Matrix (Fin 2) (Fin 2) ℝ := !![2, 1; 0, 1]

-- An actual shear-and-scale change, which is invertible and not orthogonal.
-- The computed equation covector is (2,1), with raw squared norm 5,
-- while its inverse-Gram certificate still equals the original value 1.
example :
    normalResidual ((0 : Matrix (Fin 2) (Fin 2) ℝ) * C) (Cᵀ * 1 * C) 1 (C⁻¹ *ᵥ ![1, 0]) 0 =
      (![2, 1] : Fin 2 → ℝ) ∧
    dotProduct (![2, 1] : Fin 2 → ℝ)
      ((Cᵀ * 1 * C)⁻¹ *ᵥ ![2, 1]) = 1 ∧
    dotProduct (![2, 1] : Fin 2 → ℝ) ![2, 1] = 5 := by
  have hC : IsUnit C := C.isUnit_iff_isUnit_det.mpr (by
    norm_num [C, Matrix.det_fin_two])
  have hq : Cᵀ *ᵥ (![1, 0] : Fin 2 → ℝ) = ![2, 1] := by
    ext i
    fin_cases i <;> norm_num [C, Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  have hbase : normalResidual (0 : Matrix (Fin 2) (Fin 2) ℝ) 1 1 ![1, 0] 0 =
      ![1, 0] := by simp [normalResidual]
  constructor
  · rw [normalResidual_basis_change _ _ _ hC, hbase, hq]
  constructor
  · rw [← hq]
    simpa [dotProduct, Fin.sum_univ_two] using
      inverse_gram_quadratic_basis_change (1 : Matrix (Fin 2) (Fin 2) ℝ) C hC ![1, 0]
  · norm_num [dotProduct, Fin.sum_univ_two]
