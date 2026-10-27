import KomorebiLSM.LorentzBaseNorm

/-! Exact mass preservation alone does not imply base-norm contraction.
This linear spatial dilation leaves the genuine Lorentz cone. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousTVMassWithoutPositivity
open LorentzBaseNorm

def dilation : State →ₗ[ℝ] State where
  toFun z := ![z 0,2*z 1,2*z 2]
  map_add' := by
    intro x y
    ext i
    fin_cases i <;> simp <;> ring
  map_smul' := by
    intro a x
    ext i
    fin_cases i <;> simp <;> ring

theorem preserves_mass (z : State) : RotationModel.mass (dilation z)=RotationModel.mass z := rfl

example : coneInstance.value (dilation RotationModel.initial)≤coneInstance.value RotationModel.initial := by
  norm_num [value_eq_sqrt,dilation,RotationModel.initial,Matrix.cons_val_two,Matrix.vecHead,Matrix.vecTail]

end Komorebi.LSM.ContinuousTVMassWithoutPositivity
