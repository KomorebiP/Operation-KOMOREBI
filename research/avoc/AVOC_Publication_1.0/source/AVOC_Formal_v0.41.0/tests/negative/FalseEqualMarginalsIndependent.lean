import AVOC.ObservationStream
open Komorebi.AVOC.ObservationStream Komorebi.AVOC.CalibrationSchedule
/-- Must fail: equal marginal success probabilities do not imply independence. -/
example : ProductLaw fairBoolLaw 2 (1 / 2) correlatedPair := by
  have hmarginal := correlatedPair_marginal
  apply False.elim
  have hzero := correlatedPair_one_success_mass
  have hcount : eventMass fairBoolLaw
      (fun b => streamCount correlatedPair b = (1 : Fin 3)) = (1 / 2 : ℚ) := by
    rw [hzero]
    norm_num
  rw [hzero] at hcount
  norm_num at hcount
