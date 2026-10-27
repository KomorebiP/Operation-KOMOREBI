import KomorebiRepair.MenuGenerated.Inputs00

-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase000
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(1, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (-1, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def blocks : List (SeparationBlock 3 2) := [({0}, Y0), ({1}, Y1)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 2), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 2 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase000
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase001
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (-1, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def blocks : List (SeparationBlock 3 2) := [({0}, Y0), ({1}, Y1)]
theorem certificate_encoding_valid : WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkCoveredNoRepair original blocks = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 2), original.allowed T = true → ¬ Feasible original T :=
  checkCoveredNoRepair_sound original blocks certificate_checked
end MenuCase001
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase002
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(-1, 1)], ![(1, 1)]])
def W : Mat 3 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {1, 2}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (-1, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def blocks : List (SeparationBlock 3 3) := [({1}, Y0), ({2}, Y1)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 3), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 2 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase002
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase003
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
end MenuCase003