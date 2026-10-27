import AVOC.RobustQuoteExamples
namespace Komorebi.AVOC.Affine.RobustQuoteNegative
open Komorebi.AVOC.Affine.RobustQuoteExamples

/-- MUST fail: the warm probability interval in the uncertainty example has width 2/5, not zero. -/
example : (2/5 : ℚ) = 0 := by
  norm_num
end Komorebi.AVOC.Affine.RobustQuoteNegative
