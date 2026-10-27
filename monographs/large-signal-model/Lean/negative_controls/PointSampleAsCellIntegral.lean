import KomorebiLSM.ContinuousBinnedRecords
open Komorebi.LSM.ContinuousBins

/- The normalized scalar density 3u² has full-bin probability1 and midpoint
operator0. Exact binning integrates events rather than sampling a point. -/
example : cellOperator Komorebi.LSM.UniformIntervalMoments.measure
    (QuadraticExample.instrument.op ()) Set.univ 1 = QuadraticExample.instrument.op () 0 1 := by
  rw [QuadraticExample.full_cell, QuadraticExample.midpoint]
  norm_num
