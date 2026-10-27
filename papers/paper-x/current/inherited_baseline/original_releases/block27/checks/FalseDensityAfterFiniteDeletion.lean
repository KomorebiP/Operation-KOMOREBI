import PaperX.FiniteAvoidanceBoundary

open PaperX.FiniteAvoidanceBoundary PaperX.CompletionExamples

example : DenseRange (fun p : ℕ × C2 => p.2 * sample p.1 * p.2⁻¹) →
    DenseRange (fun p : Remaining × C2 =>
      p.2 * remainingSample p.1 * p.2⁻¹) := by
  rw [iff_true_intro sample_conjugacy_dense,
    iff_false_intro remaining_conjugacy_not_dense]
  simp only [true_implies]
