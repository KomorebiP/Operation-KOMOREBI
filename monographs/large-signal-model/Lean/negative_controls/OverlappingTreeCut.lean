import KomorebiLSM
open Komorebi.LSM.PacketTree Komorebi.LSM.Block2Examples
-- Selecting a parent and its descendants overcounts a full path.
example : pathCount balancedTree (fun _ => true) ⟨0, 0, ()⟩ = 1 := by rfl
