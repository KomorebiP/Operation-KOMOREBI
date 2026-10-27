import PaperX.FiniteAvoidanceBoundary

open PaperX.FiniteAvoidanceBoundary PaperX.CompletionExamples
open PaperX.ProfiniteSeparation

example : Function.Surjective sample := sample_surjective
example : QuotientCoverage sample := sample_quotient_coverage
example : DenseRange (fun p : ℕ × C2 => p.2 * sample p.1 * p.2⁻¹) :=
  sample_conjugacy_dense
example : ¬ QuotientCoverage remainingSample := remaining_quotient_coverage_fails
example : ¬ DenseRange (fun p : Remaining × C2 =>
    p.2 * remainingSample p.1 * p.2⁻¹) := remaining_conjugacy_not_dense
example (n : Remaining) :
    signCharacter (remainingSample n) = trivialCharacter (remainingSample n) :=
  characters_agree_after_deletion n
example : signCharacter ≠ trivialCharacter := characters_differ
