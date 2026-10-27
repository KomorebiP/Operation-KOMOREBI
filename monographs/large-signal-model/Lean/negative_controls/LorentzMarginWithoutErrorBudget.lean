import KomorebiLSM.RobustOrientedMargin
import KomorebiLSM.LorentzBoundaryFragility

/-! A valid zero-margin map and bounded spatial error do not suffice when the
margin fails to cover that error. The actual boundary image leaves the cone. -/
open Komorebi.LSM LorentzCylinder RobustOrientedMargin LorentzBoundaryFragility

example : (0 : ℝ)≤sigma (ContinuousLinearMap.id ℝ (State ℝ)) := by
  apply (le_sigma_iff _ _).mpr
  intro v hv
  change 0≤1-‖v‖
  linarith

example (v : ℝ) : |(outwardPerturbation 1 (1 : ℝ) (1,v)).1|≤0 ∧
    ‖(outwardPerturbation 1 (1 : ℝ) (1,v)).2‖≤1 := by
  rw [outwardPerturbation_normalized]
  norm_num

example : ((ContinuousLinearMap.id ℝ (State ℝ))+outwardPerturbation 1 (1 : ℝ)) (1,1)∈cone := by
  simp only [mem_cone,add_apply,ContinuousLinearMap.id_apply,outwardPerturbation_normalized,
    Prod.fst_add,Prod.snd_add]
  norm_num
