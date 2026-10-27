import KomorebiRepair.BranchGenerated.Certificates00
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace KomorebiRepair.BranchRejections
def swapRoot {m q : ℕ} : BranchTree m q → BranchTree m q
  | .split j x y => .split j y x
  | t => t
def FalseRootBound : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W .bound
theorem FalseRootBound_rejected : FalseRootBound = false := by decide +kernel
def AllDeclaredInadmissible : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W .inadmissible
theorem AllDeclaredInadmissible_rejected : AllDeclaredInadmissible = false := by decide +kernel
def ZeroDetector : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.separator (0 : Mat 1 3))
theorem ZeroDetector_rejected : ZeroDetector = false := by decide +kernel
def RepeatedSplit : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.split 0 BranchCase000.tree BranchCase000.tree)
theorem RepeatedSplit_rejected : RepeatedSplit = false := by decide +kernel
def DuplicatedBoundChild : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.split 0 .bound .bound)
theorem DuplicatedBoundChild_rejected : DuplicatedBoundChild = false := by decide +kernel
def SwappedBranches : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (swapRoot BranchCase000.tree)
theorem SwappedBranches_rejected : SwappedBranches = false := by decide +kernel
def WrongCoefficients : Bool := checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U (-BranchCase000.W) BranchCase000.tree
theorem WrongCoefficients_rejected : WrongCoefficients = false := by decide +kernel
def UnselectedDirection : Bool := checkTreeOptimal BranchCase000.original {0} BranchCase000.U BranchCase000.W BranchCase000.tree
theorem UnselectedDirection_rejected : UnselectedDirection = false := by decide +kernel
def ForbiddenSelection : Bool := checkTreeOptimal BranchCase001.original {0,1} BranchCase000.U BranchCase000.W BranchCase000.tree
theorem ForbiddenSelection_rejected : ForbiddenSelection = false := by decide +kernel
def FalseNoRepair : Bool := checkTreeNoRepair BranchCase000.original BranchCase000.tree
theorem FalseNoRepair_rejected : FalseNoRepair = false := by decide +kernel
end KomorebiRepair.BranchRejections
