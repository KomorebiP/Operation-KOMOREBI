module
public import StandardContracts
public import QuantifierWitness
open Komorebi.LogicalResolution
open RelationalWitness
example : Standard.rank standardQuery = 1 := standard_query_rank
example (x : Fin 3) : successorQuery.Holds system edge (fun _ => x) ↔ x=0 := successorQuery_holds x
