import KomorebiLSM.EllipsoidDiscovery
set_option autoImplicit false
open Komorebi.LSM.EllipsoidDiscovery
/-- A central anchor cannot fix a boundary scale. -/
example : quadratic (normalizedMetric (1 : Matrix (Fin 1) (Fin 1) ℝ) 0) 0=1 := by
  norm_num [quadratic,normalizedMetric]
