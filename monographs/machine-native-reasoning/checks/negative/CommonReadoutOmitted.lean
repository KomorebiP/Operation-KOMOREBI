import MachineTheory.CommonQuotientExamples
open Komorebi.MachineTheory.CommonQuotient
open Komorebi.MachineTheory.CommonQuotient.Examples

-- Deliberately false: this file must be rejected.
example : (LinearMap.id : ℚ →ₗ[ℚ] ℚ) 1 = (0 : ℚ →ₗ[ℚ] ℚ) ((0 : ℚ →ₗ[ℚ] ℚ) 1) := by
  norm_num
