module
public import PolynomialCountControls
@[expose] public section
open Komorebi.PolynomialCountControls

-- Invalid: the prescribed-lower-residue count cannot count every root modulo four.
example : Nat.card {y : Fin 1 → ZMod 4 //
    ∀ i, (4 : ℤ) ∣ MvPolynomial.eval (fun k => ((y k).val : ℤ)) (zeroSystem i)} = 2 := by
  exact unrestricted_zero_root_count
