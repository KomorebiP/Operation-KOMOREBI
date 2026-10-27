import KomorebiRepair.BranchGenerated.Inputs02

-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase008
def wireU : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def U : Mat 2 3 := decodeWireMatrix wireU
def wireW : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def W : Mat 2 3 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {}
def node0 : BranchTree 0 2 := .bound
def tree : BranchTree 0 2 := node0
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase008
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase009
def wireU : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(-2, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def node0 : BranchTree 2 2 := .separator Y0
def wireY1 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 2)]])
def Y1 : Mat 1 2 := decodeWireMatrix wireY1
def node1 : BranchTree 2 2 := .separator Y1
def node2 : BranchTree 2 2 := .bound
def node3 : BranchTree 2 2 := .split 1 node1 node2
def node4 : BranchTree 2 2 := .split 0 node0 node3
def tree : BranchTree 2 2 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireY0 ∧ WireMatrixValid wireY1 := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 2 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase009
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase010
def wireU : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(-2, 1)]])
def U : Mat 2 1 := decodeWireMatrix wireU
def wireW : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 0) := {}
def node0 : BranchTree 2 0 := .bound
def tree : BranchTree 2 0 := node0
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 0), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase010
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase011
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def node0 : BranchTree 2 0 := .separator Y0
def tree : BranchTree 2 0 := node0
theorem certificate_encoding_valid : WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 0), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end BranchCase011