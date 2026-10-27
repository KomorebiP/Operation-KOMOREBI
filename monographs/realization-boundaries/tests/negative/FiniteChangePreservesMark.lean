/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) :
    ∃ e : pairedGroup a ≃+ pairedGroup b,
      e (markedElement (pairedSelector a)) = markedElement (pairedSelector b) := by
  exact (pairedGroup_isomorphic_iff a b).mpr h
