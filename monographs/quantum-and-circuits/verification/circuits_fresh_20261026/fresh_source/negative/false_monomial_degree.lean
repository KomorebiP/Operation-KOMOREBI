import CircuitObstructions
open CircuitObstructions
example : DegreeLE (n := 2) 1 (fun x => bprod [0,1] x) := DegreeLE.monomial [0,1] (by decide)
