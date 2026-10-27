import BoundaryConsumers
open Komorebi.PaperICompletion7.ModuleTop Komorebi.PaperICompletion7.LocalResidue
open PaperIBlock07Tests
example : letI := residueDivisionRing DH
    Module.rank (DH ⧸ Ring.jacobson DH) (RadicalTop DH DH) = 2 := by
  let := residueDivisionRing DH
  exact dual_quaternion_residue_dimension_one
