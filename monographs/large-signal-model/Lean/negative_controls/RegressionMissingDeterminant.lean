import KomorebiLSM.RegressionConfidence
open MeasureTheory Matrix Komorebi.LSM.RegressionConfidence
open scoped BigOperators
noncomputable def actualMixture : ℝ :=
  ∫ q : Fin 1 → ℝ,Real.exp ((q ⬝ᵥ (0 : Fin 1 → ℝ))/(1 : ℝ)-
    (q ⬝ᵥ (designGram (fun _ _ => 1) 1 *ᵥ q))/2)∂gaussianPrior 1
/- The actual normalized prior and one nonzero design give a determinant
factor sqrt(1/2), even at zero score. Omitting it would incorrectly give one. -/
example : actualMixture^2=1 := by
  have h := gaussian_ridge_mixture (I := Fin 1) 1 1 (by norm_num) (by norm_num)
    (fun _ _ => 1) 1 (0 : Fin 1 → ℝ)
  change actualMixture = _ at h
  norm_num [ridgeMatrix,designGram,weightedNorm,dotProduct,Matrix.det_fin_one,Matrix.vecMulVec_apply,
    Fin.sum_univ_succ] at h
  rw [h,inv_pow,Real.sq_sqrt (by norm_num)]
  norm_num
