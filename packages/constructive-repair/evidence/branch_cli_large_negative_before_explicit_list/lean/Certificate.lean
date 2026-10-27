import Input
-- Certificate contains no replacement problem data.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 5000000
open KomorebiRepair.RationalCertificates
namespace UserBranch
def wireY0 : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (1, 1)]])
def Y0 : Mat 1 2 := decodeWireMatrix wireY0
def node0 : BranchTree 2 24 := .separator Y0
def tree : BranchTree 2 24 := node0
theorem certificate_encoding_valid : WireMatrixValid wireY0 := by decide +kernel
theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel
theorem certified : ∀ T : Finset (Fin 24), original.original.allowed T = true → ¬ Feasible original.original T :=
  checkTreeNoRepair_sound original tree certificate_checked
end UserBranch
