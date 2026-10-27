import KomorebiRepair.MenuGenerated.Inputs05

-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase020
def wireU : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 2 := decodeWireMatrix wireU
def wireW : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 2 := decodeWireMatrix wireW
def chosen : Finset (Fin 0) := {}
def blocks : List (SeparationBlock 0 0) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 0), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase020
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase021
def wireU : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def U : Mat 2 3 := decodeWireMatrix wireU
def wireW : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def W : Mat 3 3 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {}
def blocks : List (SeparationBlock 0 3) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 3), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase021
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase022
def wireU : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 1 := decodeWireMatrix wireU
def wireW : WireMatrix 3 1 := (Matrix.of ![![(-123, 128)], ![(87, 64)], ![(-35, 32)]])
def W : Mat 3 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {0, 1, 2}
def wireY0 : WireMatrix 1 4 := (Matrix.of ![![(12, 41), (-28, 41), (0, 1), (32, 123)]])
def Y0 : Mat 1 4 := decodeWireMatrix wireY0
def wireY1 : WireMatrix 1 4 := (Matrix.of ![![(4, 35), (12, 35), (0, 1), (32, 35)]])
def Y1 : Mat 1 4 := decodeWireMatrix wireY1
def blocks : List (SeparationBlock 4 3) := [({1, 2}, Y0), ({0, 1}, Y1)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 3), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 4 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase022
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase023
def wireU : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 1 0 := decodeWireMatrix wireU
def wireW : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def W : Mat 3 0 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {0}
def blocks : List (SeparationBlock 3 3) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 3), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 1 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase023