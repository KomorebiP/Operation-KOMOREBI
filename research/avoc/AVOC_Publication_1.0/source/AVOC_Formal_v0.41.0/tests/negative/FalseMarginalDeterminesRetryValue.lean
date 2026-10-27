import AVOC.RetryExamples
open Komorebi.AVOC
example : Retry.retryValue (RetryBayesian.model RetryExamples.persistent) 3 RetryExamples.initial =
    Retry.retryValue (RetryBayesian.model RetryExamples.iid) 3 RetryExamples.initial := by
  rw [RetryExamples.persistent_all_positive_horizons,RetryExamples.iid_three_attempt_value]
  norm_num
