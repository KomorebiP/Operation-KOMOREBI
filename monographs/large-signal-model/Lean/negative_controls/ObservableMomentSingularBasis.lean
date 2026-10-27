import KomorebiLSM.ObservableMomentBoundaries

/- Two coefficient families give exactly the same actual operator density
under the repeated basis; dropping integration-matrix invertibility loses uniqueness. -/
set_option autoImplicit false
open Komorebi.LSM.ObservableMoments.Boundaries
example : firstCoefficients=secondCoefficients := by
  simp only [coefficients_distinct]
