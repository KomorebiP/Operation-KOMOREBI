import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : third3 (switchedMap initialFamily [(false, ()), (true, ())] initialVector) = 0 := by
  norm_num [switchedMap, wordMap, initialFamily, move12, move23, first3, second3, third3, initialVector]
