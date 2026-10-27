import AVOC.SynthesisExamples
import AVOC.RetryEvaluation

namespace Komorebi.AVOC.SynthesisRetry
open Synthesis SynthesisExamples

/-- The three symbolic inputs are precomputed. This does not price computing the
Bayesian probability, gain, or resource guard. -/
def flags {S : Type} (m : Retry.Model S) (n : Nat) (s : S) : Input :=
  ⟨decide (0 < n), m.enabled s, decide (0 < Retry.immediate m s)⟩

theorem reference_is_retry_threshold {S : Type} (m : Retry.Model S)
    (h : Retry.NoRevival m) (n : Nat) (s : S) :
    run guardReference (flags m n s) = Retry.choose m n s := by
  rw [← guard_equivalent (flags m n s)]
  cases n with
  | zero => rfl
  | succ n =>
    rw [Retry.choose_threshold m h n s]
    rfl

/-- A generated candidate is equivalent for every applicable model/state/horizon,
not merely a finite list of sampled rational probabilities. -/
theorem generated_retry_decision {S : Type} (m : Retry.Model S)
    (h : Retry.NoRevival m) (n : Nat) (s : S) (depth limit credit : Nat) :
    run (synthesize guardReference depth limit credit) (flags m n s) =
      Retry.choose m n s := by
  rw [synthesis_sound guardReference depth limit credit (flags m n s)]
  exact reference_is_retry_threshold m h n s

theorem promoted_generated_retry_decision {S : Type} (m : Retry.Model S)
    (h : Retry.NoRevival m) (n : Nat) (s : S) (calls total depth limit credit : Nat) :
    run (campaign guardReference calls total depth limit credit).accepted.journal.current.active
        (flags m n s) = Retry.choose m n s := by
  rw [campaign_active_sound (campaign guardReference calls total depth limit credit) (flags m n s)]
  exact reference_is_retry_threshold m h n s

theorem generated_guard_work_bound (depth limit credit : Nat) (s : Input) :
    (runCount (synthesize guardReference depth limit credit) s).2 ≤ 9 := by
  rw [runCount_visits]
  exact synthesis_work_nondegrading guardReference depth limit credit

end Komorebi.AVOC.SynthesisRetry
