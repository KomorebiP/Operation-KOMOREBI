import AVOC.RobustQuoteRuntime
namespace Komorebi.AVOC.Affine.RobustQuoteNegative
open Komorebi.AVOC.Affine.Staged
open Komorebi.AVOC.Affine.RobustQuote

/-- MUST fail: an infrastructure fault is not a negative model report. -/
example {n m : Nat} (md : QModel n m) :
    reportOf (.inspectWarm) (Outcome.fault : Outcome md) = some false := by
  rfl
end Komorebi.AVOC.Affine.RobustQuoteNegative
