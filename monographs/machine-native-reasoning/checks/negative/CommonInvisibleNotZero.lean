import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : third3 ((goodFamily true () - goodFamily false ()) (0, (0, 1))) = 0 := by
  norm_num [goodFamily, first3, second3, third3]
