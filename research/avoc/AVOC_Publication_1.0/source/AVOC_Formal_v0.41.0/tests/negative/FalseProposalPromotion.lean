import AVOC

namespace Komorebi.AVOC.Negative

open ClaimStatus

/-- This file MUST fail: proposal-only work is not evidence. -/
def proposalOnlyLedger : EpistemicLedger Bool where
  candidates := ∅
  status := fun _ => .proposal

example : (propose proposalOnlyLedger {true}).status false = .proved := by
  rfl

end Komorebi.AVOC.Negative
