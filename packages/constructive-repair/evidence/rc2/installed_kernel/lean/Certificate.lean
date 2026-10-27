import Input
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace UserBranch
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
end UserBranch
