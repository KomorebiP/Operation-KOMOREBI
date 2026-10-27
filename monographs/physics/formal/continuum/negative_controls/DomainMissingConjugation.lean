import KomorebiPhysics.DomainExamples
open KomorebiPhysics.DomainExamples
example : atlas.amplitude state 1 0 = atlas.amplitude state 0 1 := by
  simp only [reverse_without_conjugation_false]
