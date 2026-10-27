import KomorebiPhysics.DomainExamples
open KomorebiPhysics.DomainExamples
example : HasDerivAt (fun s => atlas.atlas.energy (localCurve s) 0) 0 0 := by
  have h := actual_packet_derivative
  apply h.congr_deriv
  norm_num
