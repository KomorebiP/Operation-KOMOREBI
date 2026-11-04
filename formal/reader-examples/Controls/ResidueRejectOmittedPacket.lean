import KomorebiReader.ResiduePackets

open Komorebi.Reader.ResiduePackets

-- Deliberately false: omitting the odd packet does not reconstruct coefficient 1.
example : project 2 0 (fun _ : ℕ => (1 : ℤ)) 1 = 1 := by decide
