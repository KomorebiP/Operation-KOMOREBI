import KomorebiLSM.SequentialLowerCertificate

/-! Reject the erroneous quarter-L1 normalization: two disjoint point masses
have L1 discrepancy two and probability-convention total variation one. -/
set_option autoImplicit false
open MeasureTheory
open Komorebi.LSM.SequentialLowerCertificate
example : lawTV (Measure.dirac false) (Measure.dirac true)≤(2:ℝ)/4 := by
  rw [lawTV_dirac_eq_one false true (by decide)]
  norm_num
