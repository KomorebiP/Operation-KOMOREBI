import KomorebiLSM.ConvexMargin
import KomorebiLSM.CoefficientBox3
open Komorebi.LSM Komorebi.LSM.CoefficientBox3
private noncomputable def reset : State →L[ℝ] State :=
  ((LinearMap.fst ℝ ℝ Spatial).smulRight (1,(0 : Spatial))).toContinuousLinearMap

/- Identity and center-reset are both mass-preserving positive operators.
Their affine combination 2I-N retains mass but requires a negative weight
and sends a normalized boundary point outside the cone. -/
example : ((2 : ℝ) • ContinuousLinearMap.id ℝ State-reset)
    (1,PiLp.single 2 (0 : Fin 2) (1 : ℝ))∈LorentzCylinder.cone := by
  norm_num [reset,LorentzCylinder.cone,OrientedEllipsoid.lorentz,norm_smul,PiLp.norm_single]
