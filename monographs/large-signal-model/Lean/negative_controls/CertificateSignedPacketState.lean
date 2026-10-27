import KomorebiLSM.CertificateLearning

/- The two scalar packets 2*id and -id synthesize id. Complete synthesis
alone cannot make the negative packet of a positive state nonnegative. -/
example : ((2:ℝ)+(-1)=1) ∧ (0≤(-1:ℝ)*1) := by
  norm_num
