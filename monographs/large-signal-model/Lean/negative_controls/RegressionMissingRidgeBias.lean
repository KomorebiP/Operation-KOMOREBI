import KomorebiLSM.RegressionConfidence
open Matrix Komorebi.LSM.RegressionConfidence
open scoped BigOperators
/- With no observations, the actual ridge estimator is zero and a nonzero
true parameter still has a regularization error. The noise radius alone fails. -/
example :
    weightedNorm (ridgeMatrix (I := Fin 1) 1 (fun _ _ => 0) 0)
      (ridgeEstimate 1 (fun _ _ => 0) (fun _ => 0) 0-(fun _ => 1)) ≤
      weightedNorm (ridgeMatrix (I := Fin 1) 1 (fun _ _ => 0) 0)⁻¹
        (responseVector (fun _ _ => 0) (fun _ => 0) 0) := by
  norm_num [ridgeMatrix,designGram,ridgeEstimate,responseVector,weightedNorm,dotProduct,
    Fin.sum_univ_succ]
