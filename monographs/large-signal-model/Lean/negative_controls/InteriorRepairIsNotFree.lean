import KomorebiLSM.InteriorRepair

/-! The reference and estimate can be identical while a genuine valid reset
repair has nonzero cost in the actual positive-decomposition base norm. -/
open Komorebi.LSM LorentzCylinder RobustOrientedMargin InteriorRepair MeasureTheory

example : (1, (1 : ℝ))∈(probabilityCone (V := ℝ)).base := by
  rw [mem_base]
  norm_num

example : (1/2 : ℝ)≤sigma (repair (ContinuousLinearMap.id ℝ (State ℝ)) 1 (1/2)) := by
  have hm := repair_margin (ContinuousLinearMap.id ℝ (State ℝ)) (ContinuousLinearMap.id ℝ (State ℝ))
    0 1 (1/2) (by norm_num) (fun _ hz => hz) (fun _ _ => by simp)
  norm_num at hm ⊢
  exact hm

example : (∫ u,(probabilityCone (V := ℝ)).value
    (repair (ContinuousLinearMap.id ℝ (State ℝ)) 1 1 (1,1) -
      (ContinuousLinearMap.id ℝ (State ℝ)) (1,1))∂UniformIntervalMoments.measure)≤0 := by
  simp only [repair,sub_self,zero_smul,one_smul,zero_add]
  rw [resetOperator_normalized]
  have hvec : ((1,0) : State ℝ)-(ContinuousLinearMap.id ℝ (State ℝ)) (1,1)=(0,-1) := by
    apply Prod.ext <;> norm_num
  rw [hvec,value_zero_mass]
  norm_num
