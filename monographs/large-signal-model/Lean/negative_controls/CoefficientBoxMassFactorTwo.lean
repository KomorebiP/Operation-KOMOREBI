import KomorebiLSM.CoefficientBox3
open Komorebi.LSM.CoefficientBox3
open scoped BigOperators
private noncomputable def v : Spatial := WithLp.toLp 2 ![(3/5:ℝ),3/5]
private def E : Coefficient := fun _ _ => 1

/- Every matrix entry has radius one and the spatial input is inside the unit
disk, but a claimed universal mass bound two is false. -/
example : |(operator E (1,v)).1|≤2 := by
  have hv : ‖v‖≤1 := by
    have hs : ‖v‖^2=(18/25:ℝ) := by
      rw [EuclideanSpace.real_norm_sq_eq]
      norm_num [v,Fin.sum_univ_two]
    nlinarith [norm_nonneg v]
  change |coordinates (operator E (1,v)) (.inl ())|≤2
  rw [coordinates_operator E (1,v) (.inl ())]
  norm_num [coordinates,Fintype.sum_sum_type,Fin.sum_univ_two,v,E]
