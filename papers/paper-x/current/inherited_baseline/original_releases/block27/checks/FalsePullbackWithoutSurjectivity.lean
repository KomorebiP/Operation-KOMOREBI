import PaperX.SurjectivePullbackBoundary

open PaperX.SurjectivePullbackBoundary

-- Deliberately false: forgetting surjectivity would allow descent of this
-- actual restricted equivalence between inequivalent irreducible representations.
example : Nonempty (Representation.Equiv (signRepresentation.comp collapsedMap)
    (trivialRepresentation.comp collapsedMap)) →
    Nonempty (signRepresentation.Equiv trivialRepresentation) := by
  rw [iff_true_intro collapsed_pullbacks_equivalent,
    iff_false_intro representations_not_equivalent]
  simp only [true_implies]
