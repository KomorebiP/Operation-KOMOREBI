import KomorebiRepair.MenuGenerated.Inputs02

-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase008
def blocks : List (SeparationBlock 3 2) := []
theorem certificate_encoding_valid : True := by decide +kernel
theorem certificate_checked : checkCoveredNoRepair original blocks = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 2), original.allowed T = true → ¬ Feasible original T :=
  checkCoveredNoRepair_sound original blocks certificate_checked
end MenuCase008
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase009
def wireU : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 1 0 := decodeWireMatrix wireU
def wireW : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def W : Mat 2 0 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {}
def blocks : List (SeparationBlock 3 2) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 2), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase009
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase010
def wireU : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def U : Mat 2 3 := decodeWireMatrix wireU
def wireW : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def W : Mat 2 3 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {}
def blocks : List (SeparationBlock 0 2) := []
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 2), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase010
-- Untrusted witnesses; the original matrices and constraints are imported.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace MenuCase011
def wireU : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(-2, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 2)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def wireY1 : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def Y1 : Mat 1 2 := decodeWireMatrix wireY1
def blocks : List (SeparationBlock 2 2) := [({0}, Y0), ({1}, Y1)]
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel
theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧
    ∀ T : Finset (Fin 2), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=
  checkCoveredOptimal_sound original chosen U W blocks certificate_checked
theorem declared_cost : original.cost chosen = 2 := by decide +kernel
theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1
end MenuCase011