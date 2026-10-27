import KomorebiPhysics.Relativistic3DRegularConnection
open KomorebiPhysics
open Relativistic3DAffineConnection
example (p : Point3) (t : ℝ) :
    HasDerivAt (fun s : ℝ => Real.sin ((shiftX s p).x))
      (Real.cos ((shiftX t p).x)) t := by
  simpa [shiftX] using ((hasDerivAt_id t).const_add p.x).sin
