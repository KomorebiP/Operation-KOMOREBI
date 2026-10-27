import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately invalid: a theorem for union-of-cell evidence cannot certify a
-- signature in the larger evidence language that splits the cell.
example : splitAlgebra.signature constantTarget {false} =
    splitAlgebra.signature constantTarget {true} := by
  exact (signature_eq_iff_occupancy_eq oneCell constantTarget _ _).mpr
    constant_singletons_same_occupancy
