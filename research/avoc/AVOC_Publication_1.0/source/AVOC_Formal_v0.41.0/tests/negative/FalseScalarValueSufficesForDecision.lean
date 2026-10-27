import AVOC.QRateDistortionExamples

open Komorebi.AVOC

/-- Deliberately false: the crossed problem has one scalar value code but needs
two exact Q-signature codes because its optimal actions differ. -/
example :
    exactQCodeNumber crossedQ 0 (by norm_num) =
      exactValueCodeNumber crossedValue 0 (by norm_num) := by
  rw [crossedQ_exact_code_number_two, crossedValue_exact_code_number_one]
