import QuantumFourierRefutation
open Komorebi.QuantumArithmetic
example : dft12 ramanujanCVector 1 = cRat 0 := by
  rw [ramanujan_mode_one_eq_twelve]
  decide +kernel
