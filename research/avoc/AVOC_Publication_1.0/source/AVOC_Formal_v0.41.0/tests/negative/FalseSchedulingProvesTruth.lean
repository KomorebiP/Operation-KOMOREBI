import AVOC.SchedulingCertificates
open Komorebi.AVOC.Scheduling
example : False := by
  have h := ready_does_not_imply_truth.1
  assumption
