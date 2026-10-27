import AVOC.ObservationCensoring

open Komorebi.AVOC Komorebi.AVOC.CalibrationSchedule
  Komorebi.AVOC.ObservationCensoring

/-- Must fail: predictable second-report availability does not preserve the
binomial count law after conditioning on completion by a finite deadline. -/
example :
    eventMass deadlineLaw (fun ω => deadlineComplete ω ∧ deadlineCount ω = 0) /
      eventMass deadlineLaw deadlineComplete = FiniteCalibration.mass 2 0 (1 / 2) := by
  rw [deadline_conditioned_zero_count]
  norm_num [FiniteCalibration.mass]
