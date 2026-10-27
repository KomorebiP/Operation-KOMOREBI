import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : first2 (wordMap (returnFamily true) [(), ()] (1, 0)) = 0 := by
  norm_num [wordMap, returnFamily, shift2, swap2, first2]
