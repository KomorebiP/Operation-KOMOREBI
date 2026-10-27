import KomorebiRepair.BranchGenerated.Inputs04

-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase016
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(-1, 1)]])
def W : Mat 3 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 3) := {0, 2}
def node0 : BranchTree 3 3 := .inadmissible
def node1 : BranchTree 3 3 := .inadmissible
def node2 : BranchTree 3 3 := .bound
def node3 : BranchTree 3 3 := .split 1 node1 node2
def node4 : BranchTree 3 3 := .split 2 node0 node3
def node5 : BranchTree 3 3 := .inadmissible
def node6 : BranchTree 3 3 := .bound
def node7 : BranchTree 3 3 := .split 1 node5 node6
def node8 : BranchTree 3 3 := .bound
def node9 : BranchTree 3 3 := .split 2 node7 node8
def node10 : BranchTree 3 3 := .split 0 node4 node9
def tree : BranchTree 3 3 := node10
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 3), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 5 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase016
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase017
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def node0 : BranchTree 2 4 := .separator Y0
def tree : BranchTree 2 4 := node0
theorem certificate_encoding_valid : WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 4), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end BranchCase017
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase018
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 24 1 := (Matrix.of ![![(-1, 1)], ![(-1, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def W : Mat 24 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 24) := {0, 1}
def wireY0 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def Y0 : Mat 1 3 := decodeWireMatrix wireY0
def node0 : BranchTree 3 24 := .separator Y0
def wireY1 : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (0, 1), (1, 1)]])
def Y1 : Mat 1 3 := decodeWireMatrix wireY1
def node1 : BranchTree 3 24 := .separator Y1
def node2 : BranchTree 3 24 := .bound
def node3 : BranchTree 3 24 := .split 1 node1 node2
def node4 : BranchTree 3 24 := .split 0 node0 node3
def tree : BranchTree 3 24 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 24), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 5 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase018
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase019
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def node0 : BranchTree 2 24 := .separator Y0
def tree : BranchTree 2 24 := node0
theorem certificate_encoding_valid : WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 24), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end BranchCase019