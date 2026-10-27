import QuantumArithmeticBridge
open Komorebi.QuantumArithmetic

-- Extract one coefficient from the checked full Fourier table.
theorem ramanujan_mode_one_eq_twelve :
    dft12 ramanujanCVector 1 = cRat 12 := by
  have h := congrArg (fun xs : List Cyclo12 => xs.getD 1 cZero) ramanujan_dft_table
  change dft12 ramanujanCVector 1 = cRat 12 at h
  exact h

-- Establish mathematical falsity independently of the historical negative test's evaluator.
theorem ramanujan_mode_one_ne_zero :
    dft12 ramanujanCVector 1 ≠ cRat 0 := by
  rw [ramanujan_mode_one_eq_twelve]
  decide +kernel

#print axioms ramanujan_mode_one_eq_twelve
#print axioms ramanujan_mode_one_ne_zero
