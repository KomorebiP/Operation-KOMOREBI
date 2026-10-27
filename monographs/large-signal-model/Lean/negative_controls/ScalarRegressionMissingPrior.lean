import KomorebiLSM.ScalarRegressionConfidence
open Komorebi.LSM.RegressionConfidence
/- The literal zero-observation scalar ridge estimate is zero. At the true
prior endpoint theta=1, deleting the prior-radius term leaves a false bound. -/
example : |scalarEstimate (fun _ => 0) (fun _ => 0) 0-(1 : ℝ)|≤
    Real.sqrt ((Real.log (scalarV (fun _ => 0) 0)+2*Real.log (1/(1 : ℝ)))/
      scalarV (fun _ => 0) 0) := by
  norm_num [scalarEstimate,scalarV]
