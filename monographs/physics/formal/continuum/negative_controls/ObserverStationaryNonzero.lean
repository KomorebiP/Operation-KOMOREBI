import KomorebiPhysics.Relativistic3DObserverDefect

open KomorebiPhysics.Relativistic3DLorentzKinematics
open KomorebiPhysics.Relativistic3DObserverDefect

example (m : ℝ) (k : Vec3) : observerDefect m k zero 1 = 1 := by
  rw [observerDefect_zero_velocity]
