import KomorebiLSM.SequentialLowerCertificate

open MeasureTheory Komorebi.LSM.SequentialLowerCertificate

-- A test with value two lies outside [0,1] and can exceed the TV distance.
example : |(∫ x : ℝ, (if x = 0 then (2 : ℝ) else 0) ∂Measure.dirac (0 : ℝ)) -
    (∫ x : ℝ, (if x = 0 then (2 : ℝ) else 0) ∂Measure.dirac (1 : ℝ))| ≤
      lawTV (Measure.dirac (0 : ℝ)) (Measure.dirac (1 : ℝ)) := by
  rw [lawTV_dirac_eq_one 0 1 (by norm_num)]
  norm_num [integral_dirac]
