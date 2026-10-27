import KomorebiRepair.MenuGenerated.Inputs04

-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase016
def wireU : WireMatrix 3 1 := (Matrix.of ![![(10, 19)], ![(11, 38)], ![(4, 57)]])
def U : Mat 3 1 := decodeWireMatrix wireU
def wireW : WireMatrix 4 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def W : Mat 4 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 4) := {1, 3}
def blocks : List (SeparationBlock 3 4) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 4), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 3 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase016
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase017
def wireU : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 2 0 := decodeWireMatrix wireU
def wireW : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def W : Mat 1 0 := decodeWireMatrix wireW
def chosen : Finset (Fin 1) := {}
def blocks : List (SeparationBlock 3 1) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 1), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase017
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase018
def wireU : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 2 := decodeWireMatrix wireU
def wireW : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 2), (1, 6)], ![(0, 1), (0, 1)]])
def W : Mat 3 2 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {1}
def wireY0 : WireMatrix 1 1 := (Matrix.of ![![(2, 3)]])
def Y0 : Mat 1 1 := decodeWireMatrix wireY0
def blocks : List (SeparationBlock 1 3) := [({}, Y0)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 3), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 1 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase018
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase019
def wireU : WireMatrix 2 1 := (Matrix.of ![![(6, 1)], ![(0, 1)]])
def U : Mat 2 1 := decodeWireMatrix wireU
def wireW : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def W : Mat 1 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 1) := {}
def blocks : List (SeparationBlock 1 1) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 1), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase019