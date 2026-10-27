module
public import QuantifierWitness
open Komorebi.LogicalResolution.RelationalWitness
-- Vertex one has no successor. This proposed witness must not be accepted.
example : successorQuery.Holds system edge (fun _ => (1 : Fin 3)) := by
  exact (successorQuery_holds 1).mpr rfl
