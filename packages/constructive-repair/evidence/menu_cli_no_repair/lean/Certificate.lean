import Input
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace UserMenu
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def blocks : List (SeparationBlock 2 4) := [({0, 1, 2, 3}, Y0)]
theorem certificate_encoding_valid : WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkCoveredNoRepair original blocks = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 4), original.allowed T = true → ¬ Feasible original T :=
  checkCoveredNoRepair_sound original blocks certificate_checked
end UserMenu
