import KomorebiLSM.ObservableMomentBoundaries

/- The actual weighted row norm can be one half while its directional
pairing is one. Omitting the inverse-design directional norm is false. -/
set_option autoImplicit false
open Matrix
open Komorebi.LSM.RegressionConfidence Komorebi.LSM.ObservableMoments.Boundaries
example : |unitDirection ⬝ᵥ unitDirection|≤weightedNorm smallDesign unitDirection := by
  rw [unit_direction_pairing,small_weighted_norm]
  norm_num
