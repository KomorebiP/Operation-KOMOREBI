import KomorebiLSM.MeasureTVCalculus
open MeasureTheory
open Komorebi.LSM.SequentialLowerCertificate

/- Common reporting contracts distance, but identity reporting need not reduce it. -/
example : lawTV ((Measure.dirac false).map id) ((Measure.dirac true).map id)=0 := by
  simp only [Measure.map_id]
  rw [lawTV_dirac_eq_one false true (by decide)]
  norm_num
