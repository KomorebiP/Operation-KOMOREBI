import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : first2 (returnFamily false () ((returnFamily true () - returnFamily false ()) (1, 0))) = 0 := by
  norm_num [returnFamily, shift2, swap2, first2]
