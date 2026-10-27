import PaperX.SurjectivePullbackBoundary

open PaperX.CompletionExamples PaperX.SurjectivePullbackBoundary
open PaperX.ProfiniteSeparation

example : signRepresentation.IsIrreducible := inferInstance
example : trivialRepresentation.IsIrreducible := inferInstance
example : ¬ Function.Surjective collapsedMap := collapsedMap_not_surjective
example : ¬ Nonempty (signRepresentation.Equiv trivialRepresentation) :=
  representations_not_equivalent
example : Nonempty (Representation.Equiv (signRepresentation.comp collapsedMap)
    (trivialRepresentation.comp collapsedMap)) := collapsed_pullbacks_equivalent
example : QuotientCoverage (fun g : C2 => (quotientSamples g).1) :=
  projected_samples_coverage
example : ¬ QuotientCoverage quotientSamples := quotient_samples_coverage_fails
