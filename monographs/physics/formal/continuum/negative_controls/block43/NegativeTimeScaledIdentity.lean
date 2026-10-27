import KomorebiPhysics.Relativistic3DFourierPropagator

open KomorebiPhysics.Relativistic3DFourierPropagator

/-- A concrete nonzero four-spinor. -/
def e0 : Spinor := fun j => if j = 0 then 1 else 0

/-- Deliberately false: multiplying the identity generator by `-i` is nonzero. -/
example : timeScaledOperator 1 (1 : SpinorEnd) e0 = 0 := by
  ext j
  fin_cases j <;> simp [e0, timeScaledOperator]
