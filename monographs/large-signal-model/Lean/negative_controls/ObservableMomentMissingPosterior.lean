import KomorebiLSM.ObservableMomentBoundaries

/- A measurable normalized next-state map is not automatically the actual
posterior. The positive identity instrument preserves the left state. -/
set_option autoImplicit false
open MeasureTheory Komorebi.LSM.ObservableMoments Komorebi.LSM.ObservableMoments.Boundaries
example : (∫ _ : Unit,rightState.1∂identityInstrument.kernel () leftState)=
    momentOperator identityInstrument (fun _ : Unit => 1) () leftState.1 := by
  simp only [wrong_accessible_posterior_not_mean]
