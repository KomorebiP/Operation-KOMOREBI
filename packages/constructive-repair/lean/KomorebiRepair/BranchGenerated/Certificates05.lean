import KomorebiRepair.BranchGenerated.Inputs05

-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase020
def wireU : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def U : Mat 0 1 := decodeWireMatrix wireU
def wireW : WireMatrix 24 1 := (Matrix.of ![![(-1, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def W : Mat 24 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 24) := {0}
def node0 : BranchTree 1 24 := .bound
def node1 : BranchTree 1 24 := .bound
def node2 : BranchTree 1 24 := .split 0 node0 node1
def tree : BranchTree 1 24 := node2
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 24), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase020
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase021
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 24 1 := (Matrix.of ![![(-1, 1)], ![(-1, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def W : Mat 24 1 := decodeWireMatrix wireW
def chosen : Finset (Fin 24) := {0, 1}
def node0 : BranchTree 3 24 := .inadmissible
def node1 : BranchTree 3 24 := .inadmissible
def node2 : BranchTree 3 24 := .bound
def node3 : BranchTree 3 24 := .split 1 node1 node2
def node4 : BranchTree 3 24 := .split 0 node0 node3
def tree : BranchTree 3 24 := node4
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 24), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 5 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase021
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase022
def node0 : BranchTree 1 24 := .inadmissible
def tree : BranchTree 1 24 := node0
theorem certificate_encoding_valid : True := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 24), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end BranchCase022
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace BranchCase023
def wireU : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 1 0 := decodeWireMatrix wireU
def wireW : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def W : Mat 2 0 := decodeWireMatrix wireW
def chosen : Finset (Fin 2) := {0}
def node0 : BranchTree 3 2 := .bound
def node1 : BranchTree 3 2 := .bound
def node2 : BranchTree 3 2 := .split 0 node0 node1
def tree : BranchTree 3 2 := node2
theorem certificate_encoding_valid : WireMatrixValid wireU ∧ WireMatrixValid wireW := by decide +kernel
theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel
theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧
    ∀ T : Finset (Fin 2), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=
  checkTreeOptimal_sound original chosen U W tree certificate_checked
theorem declared_cost : original.original.cost chosen = 0 := by decide +kernel
theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1
end BranchCase023