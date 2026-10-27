import AVOC.HistoryState
import AVOC.OpenWorld
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Every rational belief on the one-point world is uniquely determined. -/
theorem unitBelief_unique (b : RationalBelief Unit) : b = diracBelief () := by
  apply RationalBelief.ext
  intro u
  cases u
  have hs := b.sum_one
  simpa using hs

/-- A fair observation channel carrying no information about the one-point world. -/
def unitFairBoolChannel : RationalChannel Unit Bool where
  prob _ _ := 1 / 2
  nonneg := by intro _ _; norm_num
  sum_one := by intro _; rw [Fintype.sum_bool]; norm_num

/-- Minimal certified Bayesian research system used to witness transcript
compression. -/
def transcriptCompressionSystem :
    CertifiedBayesianResearchSystem Unit Unit Bool Unit where
  actions := {()}
  actions_nonempty := by simp
  experiment _ := unitFairBoolChannel
  reward _ _ := 1
  certStep _ _ _ := ()

/-- Initial one-world certified state. -/
def transcriptInitialState : CertifiedResearchState Unit Unit where
  belief := diracBelief ()
  cert := ()

/-- Two genuinely different raw observation histories. -/
def transcriptTrue : ResearchHistory Unit Bool :=
  .snoc .root () true

def transcriptFalse : ResearchHistory Unit Bool :=
  .snoc .root () false

/-- The two raw transcripts are syntactically different. -/
theorem transcriptTrue_ne_transcriptFalse : transcriptTrue ≠ transcriptFalse := by
  intro h
  cases h

/-- Despite their raw difference, the compiled Bayesian/certification states are
identical because neither observation distinguishes the only possible world. -/
theorem transcript_compiled_states_equal :
    compileHistory transcriptCompressionSystem transcriptInitialState transcriptTrue =
      compileHistory transcriptCompressionSystem transcriptInitialState transcriptFalse := by
  apply CertifiedResearchState.ext
  · exact (unitBelief_unique _).trans (unitBelief_unique _).symm
  · rfl

/-- Hence every finite-horizon future value is identical for the two distinct
raw transcripts. -/
theorem transcript_future_values_equal (n : ℕ) :
    historyHorizonValue transcriptCompressionSystem transcriptInitialState n transcriptTrue =
      historyHorizonValue transcriptCompressionSystem transcriptInitialState n transcriptFalse := by
  exact equal_compiled_history_implies_equal_value
    transcriptCompressionSystem transcriptInitialState n transcriptTrue transcriptFalse
    transcript_compiled_states_equal

end Komorebi.AVOC
