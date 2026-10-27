import PaperX.GeneralRecoveryBoundary
open PaperX.GeneralRecoveryBoundary PaperX.AffineMonodromy PaperX.ReconstructionExamples
open PaperX.LogarithmicRecovery PaperX.MonodromyReconstruction
example : recoverN 1 (reconstruct (absorbed (chain ℚ 6) chosenCocycle) chosenCocycle u) =
    (absorbed (chain ℚ 6) chosenCocycle).N := by
  rw [iff_false_intro recovery_without_original_sample_fails]
