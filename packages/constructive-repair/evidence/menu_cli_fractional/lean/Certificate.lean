import Input
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace UserMenu
def wireU : WireMatrix 1 1 := (Matrix.of ![![(-1, 2)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 1 1 := (Matrix.of ![![(-5, 4)]])
def W : Mat 1 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 1) := {0}
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (6, 5)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def blocks : List (SeparationBlock 2 1) := [({}, Y0)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 1), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 7 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end UserMenu
