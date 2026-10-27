import KomorebiRepair.MenuGenerated.Certificates00
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace KomorebiRepair.MenuRejections
def MissingCheaperCover : Bool := checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W (MenuCase000.blocks.take 1)
theorem MissingCheaperCover_rejected : MissingCheaperCover = false := by decide +kernel
def ZeroSeparator : Bool := checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W [({0}, (0 : Mat 1 3)), ({1}, MenuCase000.Y1)]
theorem ZeroSeparator_rejected : ZeroSeparator = false := by decide +kernel
def OverstatedBlock : Bool := checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W [({0, 1}, MenuCase000.Y0)]
theorem OverstatedBlock_rejected : OverstatedBlock = false := by decide +kernel
def WrongCoefficients : Bool := checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U (-MenuCase000.W) MenuCase000.blocks
theorem WrongCoefficients_rejected : WrongCoefficients = false := by decide +kernel
def ExpensiveSingleton : Bool := checkCoveredOptimal MenuCase002.original {0} (0 : Mat 1 1) (!![-1; 0; 0] : Mat 3 1) MenuCase002.blocks
theorem ExpensiveSingleton_rejected : ExpensiveSingleton = false := by decide +kernel
def ForbiddenSelection : Bool := checkCoveredOptimal MenuCase001.original {0, 1} MenuCase000.U MenuCase000.W MenuCase000.blocks
theorem ForbiddenSelection_rejected : ForbiddenSelection = false := by decide +kernel
def BogusNoRepair : Bool := checkCoveredNoRepair MenuCase000.original MenuCase000.blocks
theorem BogusNoRepair_rejected : BogusNoRepair = false := by decide +kernel
def UnselectedColumnUsed : Bool := checkCoveredOptimal MenuCase000.original {0} MenuCase000.U MenuCase000.W MenuCase000.blocks
theorem UnselectedColumnUsed_rejected : UnselectedColumnUsed = false := by decide +kernel
end KomorebiRepair.MenuRejections
