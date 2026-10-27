module
public import AffinePairControls

@[expose] public section
open Komorebi.AffinePair Komorebi.AffinePairControls

example : HasJointLift 2 1 oneId oneId (fun _ => 0) (fun _ => 2) (fun _ => 0) := by
  exact two_individual_lifts
