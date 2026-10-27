import KomorebiLSM.ConvexRepairBracketing

/-! A row with spatial norm greater than one is not cone-positive and cannot
supply the separator lower bound, even at an actually feasible weight. -/
open Komorebi.LSM LorentzCylinder RobustOrientedMargin InteriorRepair ConvexRepairBracketing

example : (0 : ℝ)∈feasibleWeights (fun (_ : Unit) (_ : ℝ) => ContinuousLinearMap.id ℝ (State ℝ)) 0 := by
  apply (feasible_iff_linear _ _ _).mpr
  refine ⟨by constructor <;> norm_num,?_⟩
  intro a u hu v hv
  change 0≤(1-(0 : ℝ))*slack (ContinuousLinearMap.id ℝ (State ℝ) (1,v))+0
  simp only [sub_zero,one_mul,add_zero]
  change 0≤1-‖v‖
  linarith

example : ((0 : ℝ)-separator (2 : ℝ) (1,1))/(1-separator (2 : ℝ) (1,1))≤0 := by
  norm_num [separator,Real.inner_apply]
