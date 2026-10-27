import PaperX.CyclotomicPrimeCoverage
import PaperX.CofiniteConjugacyCoverage
import Mathlib.NumberTheory.NumberField.Cyclotomic.Basic

variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]
example : DiscreteTopology Gal(L/ℚ) := inferInstance
example : CompactSpace Gal(L/ℚ) := inferInstance
example : TotallyDisconnectedSpace Gal(L/ℚ) := inferInstance
example : IsTopologicalGroup Gal(L/ℚ) := inferInstance
example : NumberField (CyclotomicField 4 ℚ) := inferInstance
set_option backward.isDefEq.respectTransparency false in
example : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) := by
  exact CyclotomicField.isCyclotomicExtension 4 ℚ
