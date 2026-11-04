import KomorebiReader.FactorialLanes

open Komorebi.Reader.FactorialLanes

-- Removing one of the ten factors at n = 1 cannot reconstruct 14!.
example : 24 * (∏ r ∈ Finset.range 9, stepFactorial (5 + r) 1 10) =
    Nat.factorial 14 := by
  decide
