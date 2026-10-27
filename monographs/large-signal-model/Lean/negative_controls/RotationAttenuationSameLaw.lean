import KomorebiLSM.RotationApproximation
open Komorebi.LSM Komorebi.LSM.RotationApproximation

/- A finite positive certificate for the changed dynamics does not prove that
its law is identical to the original law. -/
example : mass (FiniteInstruments.wordAction (operator 1) [(false,false),(true,false)] initial)=
    mass (FiniteInstruments.wordAction (operator (2/3)) [(false,false),(true,false)] initial) := by
  rw [exact_and_two_thirds_probe.1,exact_and_two_thirds_probe.2]
  norm_num
