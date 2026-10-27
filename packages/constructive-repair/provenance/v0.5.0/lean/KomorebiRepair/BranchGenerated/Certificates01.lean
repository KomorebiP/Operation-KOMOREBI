import KomorebiRepair.BranchGenerated.Inputs01

-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase004
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(1, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def node0 : BranchTree 3 2 := .bound
def node1 : BranchTree 3 2 := .bound
def node2 : BranchTree 3 2 := .bound
def node3 : BranchTree 3 2 := .split 1 node1 node2
def node4 : BranchTree 3 2 := .split 0 node0 node3
def tree : BranchTree 3 2 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase004
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase005
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 2 1 := (Matrix.of ![![(-1, 1)], ![(1, 1)]])
def W : Mat 2 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0, 1}
def node0 : BranchTree 3 2 := .inadmissible
def node1 : BranchTree 3 2 := .inadmissible
def node2 : BranchTree 3 2 := .bound
def node3 : BranchTree 3 2 := .split 1 node1 node2
def node4 : BranchTree 3 2 := .split 0 node0 node3
def tree : BranchTree 3 2 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 2 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase005
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase006
def node0 : BranchTree 3 2 := .inadmissible
def tree : BranchTree 3 2 := node0
theorem certificate_encoding_valid : True := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 2), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end BranchCase006
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase007
def wireU : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 1 0 := decodeWireMatrix wireU
def wireW : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def W : Mat 2 0 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {}
def node0 : BranchTree 3 2 := .bound
def tree : BranchTree 3 2 := node0
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase007