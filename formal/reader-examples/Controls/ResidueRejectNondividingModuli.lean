import KomorebiReader.ResiduePackets

open Komorebi.Reader.ResiduePackets

-- Deliberately false: the zero packet modulo three does not lie in even parity.
example : project 2 0 (project 3 0 (fun _ : ℕ => (1 : ℤ))) 3 =
    project 3 0 (fun _ : ℕ => (1 : ℤ)) 3 := by decide
