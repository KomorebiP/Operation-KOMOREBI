import KomorebiLSM.DataSelectedGeometry

/-! A normalized Lorentz input has cylinder norm one, but its whole-state
Euclidean norm can be sqrt(2). Replacing that norm by the product max norm fails. -/
open Komorebi.LSM DataSelectedGeometry

def v : EuclideanSpace ℝ (Fin 1) := WithLp.toLp 2 (fun _ => 1)

example : ‖v‖≤1 := by
  have hs : ‖v‖^2=1 := by norm_num [v,EuclideanSpace.real_norm_sq_eq,Fin.sum_univ_succ]
  nlinarith [norm_nonneg v]

example : ‖wholeInput v‖≤1 := by
  have hs : ‖wholeInput v‖^2=2 := by
    rw [whole_norm_sq,wholeInput_mass,wholeInput_spatial]
    norm_num [v,EuclideanSpace.real_norm_sq_eq,Fin.sum_univ_succ]
  have hn : ¬‖wholeInput v‖≤1 := by
    intro h
    nlinarith [norm_nonneg (wholeInput v)]
  rw [iff_false_intro hn]
