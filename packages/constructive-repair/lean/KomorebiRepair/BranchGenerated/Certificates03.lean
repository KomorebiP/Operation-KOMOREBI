import KomorebiRepair.BranchGenerated.Inputs03

-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase012
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-2, 1), (-3, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 2 2 := (Matrix.of ![![(-1, 1), (0, 1)], ![(0, 1), (-1, 1)]])
def W : Mat 2 2 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def node0 : BranchTree 3 2 := .separator Y0
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (0, 1), (1, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def node1 : BranchTree 3 2 := .separator Y1
def node2 : BranchTree 3 2 := .bound
def node3 : BranchTree 3 2 := .split 1 node1 node2
def node4 : BranchTree 3 2 := .split 0 node0 node3
def tree : BranchTree 3 2 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 6 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase012
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase013
def wireU : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(-2, 1)]])
def U : Mat 2 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(0, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {1}
def node0 : BranchTree 2 2 := .inadmissible
def node1 : BranchTree 2 2 := .bound
def node2 : BranchTree 2 2 := .split 0 node0 node1
def node3 : BranchTree 2 2 := .bound
def node4 : BranchTree 2 2 := .split 1 node2 node3
def tree : BranchTree 2 2 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 1 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase013
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase014
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 3 1 := (Matrix.of ![![(-1, 1)], ![(0, 1)], ![(0, 1)]])
def W : Mat 3 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {0}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def node0 : BranchTree 3 3 := .separator Y0
def node1 : BranchTree 3 3 := .bound
def node2 : BranchTree 3 3 := .split 2 node0 node1
def node3 : BranchTree 3 3 := .bound
def node4 : BranchTree 3 3 := .split 1 node2 node3
def node5 : BranchTree 3 3 := .bound
def node6 : BranchTree 3 3 := .split 0 node4 node5
def tree : BranchTree 3 3 := node6
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 3), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 3 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase014
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase015
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(-1, 1)]])
def W : Mat 3 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {2}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def node0 : BranchTree 3 3 := .separator Y0
def node1 : BranchTree 3 3 := .bound
def node2 : BranchTree 3 3 := .split 2 node0 node1
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (-1, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def node3 : BranchTree 3 3 := .separator Y1
def node4 : BranchTree 3 3 := .bound
def node5 : BranchTree 3 3 := .split 1 node3 node4
def node6 : BranchTree 3 3 := .bound
def node7 : BranchTree 3 3 := .split 2 node5 node6
def node8 : BranchTree 3 3 := .split 0 node2 node7
def tree : BranchTree 3 3 := node8
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 3), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 4 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase015