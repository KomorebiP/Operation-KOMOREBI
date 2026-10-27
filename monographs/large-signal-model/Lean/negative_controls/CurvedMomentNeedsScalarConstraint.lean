import KomorebiLSM.CurvedMomentInstrument
import Mathlib.Tactic
set_option autoImplicit false
open Komorebi.LSM.CurvedMoment

-- The PSD moment matrix alone admits the out-of-interval signal 2.
-- Valid parameters a=0,b=1 give a negative branch mass at u=0.
example : (momentMatrix (curve 2)).PosSemidef := by
  rw [momentMatrix_psd_iff]
  change 0≤(1:ℝ) ∧ 0≤2^2 ∧ 2^2≤1*2^2
  norm_num

example : branch 0 1 0 (curve 2)∈cone := by
  have he : branch 0 1 0 (curve 2)=![-1,0,0] := by
    rw [branch_apply]
    change (1+(0:ℝ)*0*2+1*((3*0^2-1)/2)*2^2)•![1,0,0^2]=![-1,0,0]
    ext i
    fin_cases i <;> norm_num
  rw [he,cone_iff]
  change 0≤(-1:ℝ) ∧ 0≤0 ∧ 0^2≤(-1)*0 ∧ 0≤(-1)
  norm_num
