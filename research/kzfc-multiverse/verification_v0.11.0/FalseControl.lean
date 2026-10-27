import Komorebi.Multiverse.HigherObstructionExample
open Komorebi.Multiverse
example : TN.JointAmalgamable boundaryTriple := by
  exact False.elim (boundaryTriple_not_joint (by assumption))
