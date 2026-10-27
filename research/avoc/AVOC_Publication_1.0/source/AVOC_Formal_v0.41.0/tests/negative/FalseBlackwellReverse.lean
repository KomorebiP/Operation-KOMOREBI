import AVOC.StochasticExamples

namespace Komorebi.AVOC.Negative

/-- A fixed fair-coin garbling from the one uninformative signal. -/
def fairBoolFromUnit : RationalChannel Unit Bool where
  prob _ _ := 1 / 2
  nonneg := by intro; norm_num
  sum_one := by intro; native_decide

/-- DELIBERATELY FALSE. A one-signal experiment cannot be garbled into perfect
Bool observation. This attempted witness must fail at channel equality. -/
example : BlackwellRefines (uninformativeChannel Bool) (identityChannel Bool) := by
  refine ⟨fairBoolFromUnit, ?_⟩
  rfl

end Komorebi.AVOC.Negative
