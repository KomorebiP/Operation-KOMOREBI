import KomorebiLSM
open Komorebi.LSM Komorebi.LSM.PacketTree
-- A right-leaf path remains uncovered when only the left leaf is selected.
example : pathCount (.branch 1 (fun _ => .leaf))
    (fun v => match v with | .inl _ => false | .inr p => decide (p.1 = 0))
    ⟨1, ()⟩ = 1 := by rfl
