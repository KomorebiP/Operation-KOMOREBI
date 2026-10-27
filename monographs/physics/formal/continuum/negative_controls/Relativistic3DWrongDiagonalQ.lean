import KomorebiPhysics.Relativistic3DAnisotropy
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DAnisotropy
-- Intentionally false: the diagonal quartic anisotropy cannot be discarded.
example :
    anisotropyQ 0 (diagCoord 1) (diagCoord 1) (diagCoord 1) = 0 := by
  rw [anisotropyQ_diagonal]
