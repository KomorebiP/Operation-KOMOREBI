import KomorebiPhysics.Relativistic3DFullFourierEvolution

open KomorebiPhysics.Relativistic3DFullFourierEvolution

example (f : CoeffL2) (hf : ‖f‖ = 1) : coeffTruncation ∅ f = f := by
  have hzero : coeffTruncation ∅ f = 0 := by
    apply lp.ext
    funext n
    simp
  rw [hzero]
  symm
  apply norm_eq_zero.mp
  rw [hf]
  norm_num
