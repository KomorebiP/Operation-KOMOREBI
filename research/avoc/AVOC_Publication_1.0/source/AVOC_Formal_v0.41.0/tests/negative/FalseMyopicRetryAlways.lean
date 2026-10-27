import AVOC.RetryExamples
open Komorebi.AVOC
example : Retry.retryValue RetryExamples.improving 2 false = 0 := by
  rw [RetryExamples.improving_two_steps_worthwhile]
  norm_num
