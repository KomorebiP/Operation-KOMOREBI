import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : ((0, (0, 0)) : V3) = ((0, (0, 1)) : V3) := by
  norm_num
