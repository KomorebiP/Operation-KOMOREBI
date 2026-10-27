import AVOC.RobustQuoteExamples
namespace Komorebi.AVOC.Affine.RobustQuoteNegative
open Komorebi.AVOC.Affine.RobustQuoteExamples

/-- MUST fail: selected warm installation preserves the unselected cold artifact. -/
example : afterWarm.coldArtifact ≠ exactStart.coldArtifact := by
  rw [warm_install_preserves_unselected.1]
end Komorebi.AVOC.Affine.RobustQuoteNegative
