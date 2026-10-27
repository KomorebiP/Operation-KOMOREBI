import KomorebiLSM.SequentialLowerCertificate

open MeasureTheory Komorebi.LSM.SequentialLowerCertificate

-- The constant-zero test has zero residual under both laws and cannot give an upper bound.
example : |residual 1 (fun _ => 0) (fun _ => 0)| ≤ 0 →
    lawTV (Measure.dirac (0 : ℝ)) (Measure.dirac (1 : ℝ)) ≤ 0 := by
  intro _
  rw [lawTV_dirac_eq_one 0 1 (by norm_num)]
  norm_num
