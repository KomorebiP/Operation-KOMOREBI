import KomorebiPhysics.DomainExamples
open KomorebiPhysics.DomainExamples
example : atlas.current state 0 1 = 2 := by
  rw [exact_current.1]
  norm_num
