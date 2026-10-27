import AVOC.RetryExamples
open Komorebi.AVOC
example : RetryBayesian.mean RetryExamples.persistent
    (RetryBayesian.afterFault RetryExamples.persistent RetryExamples.prior) = 1/2 := by
  rw [RetryExamples.fault_resolve_probability]
  norm_num
