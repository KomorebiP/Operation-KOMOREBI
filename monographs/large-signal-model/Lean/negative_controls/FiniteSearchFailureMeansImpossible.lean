import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
example : ¬ ∃ c : Candidate 1 1, Valid (fun _ => 1) (fun _ => 1) (fun _ => 1) c := by
  simp [bounded_failure_not_impossibility.2]
