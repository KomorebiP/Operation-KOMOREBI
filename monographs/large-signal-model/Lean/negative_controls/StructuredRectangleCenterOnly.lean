import KomorebiLSM.StructuredRectangle

/-! Checking a convenient center cannot certify the whole returned rectangle.
The rectangle contains the valid center (0,0) and the invalid member (2,0).
That member sends a mass-one curve state to a branch of mass -1. -/
open Komorebi.LSM.CurvedMoment
open Komorebi.LSM.CurvedMoment.StructuredRectangle

def box : Rectangle := ⟨0,2,0,0⟩

example : (0,0)∈box.carrier := by norm_num [Rectangle.carrier,box]
example : (2,0)∈box.carrier := by norm_num [Rectangle.carrier,box]
example : |(0:ℝ)|+|(0:ℝ)|≤1 := by norm_num
example : curve 1∈cone := curve_mem 1 (by norm_num)

example : 0≤mass (branch 2 0 (-1) (curve 1)) := by
  rw [branch_mass]
  norm_num [likelihood,curve,legendre]
