import KomorebiLSM.CertificateLearning

/- The two scalar branch coefficients -1 and 2 have exact total mass one.
That equality cannot replace the nonnegative-entry witness contract. -/
example : ((-1:ℝ)+2=1) ∧ (0≤(-1:ℝ)) := by
  norm_num
