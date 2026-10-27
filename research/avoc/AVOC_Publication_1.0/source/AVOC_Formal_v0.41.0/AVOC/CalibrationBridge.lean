import AVOC.RobustQuoteCodec

namespace Komorebi.AVOC.Affine.CalibrationBridge

open Komorebi.AVOC
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Action)
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote

variable {n m : Nat}

/-- The chosen action is compared only with distinct feasible competitors.
Comparing its lower bound with its own upper bound would force zero radius. -/
def CompetitorDominance (md : QModel n m) (h : Nat) (s : State md) (a : Action) : Prop :=
  a ∈ LazyStaged.actions (nominal md) s ∧
    ∀ b ∈ LazyStaged.actions (nominal md) s, b ≠ a →
      upperQ md h s b ≤ lowerQ md h s a

theorem competitor_dominance_sound (md : QModel n m) (h : Nat)
    (s : State md) (a : Action) (hd : CompetitorDominance md h s a)
    (r : Realization md) :
    ∀ b ∈ (trueSystem md r).actions s,
      Guarded.qValue (trueSystem md r) h s b ≤
        Guarded.qValue (trueSystem md r) h s a := by
  intro b hb
  by_cases hba : b = a
  · subst b
    exact le_rfl
  · exact (q_between md r h s b).2.trans
      ((hd.2 b hb hba).trans (q_between md r h s a).1)

/-- Exact executable test for the corrected competitor-only certificate. -/
def competitorDominanceCheck (md : QModel n m) (h : Nat)
    (s : State md) (a : Action) : Bool :=
  decide (a ∈ LazyStaged.actions (nominal md) s) &&
    (LazyStaged.actionList (nominal md) s).all (fun b =>
      decide (b = a) || decide
        (RobustQuoteCodec.upperScore md h s b ≤ RobustQuoteCodec.lowerScore md h s a))

theorem competitorDominanceCheck_sound (md : QModel n m) (h : Nat)
    (s : State md) (a : Action) (hc : competitorDominanceCheck md h s a = true) :
    CompetitorDominance md h s a := by
  have hp : decide (a ∈ LazyStaged.actions (nominal md) s) = true ∧
      (LazyStaged.actionList (nominal md) s).all (fun b =>
        decide (b = a) || decide
          (RobustQuoteCodec.upperScore md h s b ≤ RobustQuoteCodec.lowerScore md h s a)) = true := by
    simpa [competitorDominanceCheck] using hc
  refine ⟨of_decide_eq_true hp.1, ?_⟩
  intro b hb hba
  have hm : b ∈ LazyStaged.actionList (nominal md) s :=
    (LazyStaged.mem_actionList (nominal md) s b).2 hb
  have hall := List.all_eq_true.mp hp.2 b hm
  simpa [hba] using hall

theorem checked_competitor_dominance_optimal (md : QModel n m) (h : Nat)
    (s : State md) (a : Action) (hc : competitorDominanceCheck md h s a = true)
    (r : Realization md) :
    ∀ b ∈ (trueSystem md r).actions s,
      Guarded.qValue (trueSystem md r) h s b ≤
        Guarded.qValue (trueSystem md r) h s a :=
  competitor_dominance_sound md h s a (competitorDominanceCheck_sound md h s a hc) r

/-- The old test is sound but can certify only a zero-radius selected action. -/
theorem self_comparison_forces_zero_radius (md : QModel n m) (h : Nat)
    (s : State md) (a : Action) (ha : a ∈ LazyStaged.actions (nominal md) s)
    (hd : ∀ b ∈ LazyStaged.actions (nominal md) s,
      upperQ md h s b ≤ lowerQ md h s a) : localQRadius md h a = 0 := by
  have hh := hd a ha
  have hn := localQRadius_nonneg md h a
  unfold upperQ lowerQ at hh
  linarith

/-- Install newly authorized probability bands before a fresh planning episode.
This constructor does not mutate an outstanding durable intent and does not
assert that the supplied probability bands have statistical coverage. -/
def replaceProbabilityBands (md : QModel n m) (warm cold : ProbabilityBand) : QModel n m :=
  { md with
    warm := {
      approved := { md.warm.approved with probability := warm }
      kind_eq := md.warm.kind_eq
      gross_nonneg := md.warm.gross_nonneg }
    cold := {
      approved := { md.cold.approved with probability := cold }
      kind_eq := md.cold.kind_eq
      gross_nonneg := md.cold.gross_nonneg } }

@[simp] theorem replaced_source (md : QModel n m) (w c : ProbabilityBand) :
    (replaceProbabilityBands md w c).source = md.source := rfl

@[simp] theorem replaced_calls (md : QModel n m) (w c : ProbabilityBand) :
    (replaceProbabilityBands md w c).calls = md.calls := rfl

@[simp] theorem replaced_identity (md : QModel n m) (w c : ProbabilityBand) (k : Kind) :
    quoteIdentity (replaceProbabilityBands md w c) k = quoteIdentity md k := by
  cases k <;> rfl

@[simp] theorem replaced_setupBand (md : QModel n m) (w c : ProbabilityBand) (k : Kind) :
    setupBand (replaceProbabilityBands md w c) k = setupBand md k := by
  cases k <;> rfl

@[simp] theorem replaced_grossBand (md : QModel n m) (w c : ProbabilityBand) (k : Kind) :
    grossBand (replaceProbabilityBands md w c) k = grossBand md k := by
  cases k <;> rfl

@[simp] theorem replaced_warm_probability (md : QModel n m) (w c : ProbabilityBand) :
    probBand (replaceProbabilityBands md w c) .warm = w := rfl

@[simp] theorem replaced_cold_probability (md : QModel n m) (w c : ProbabilityBand) :
    probBand (replaceProbabilityBands md w c) .cold = c := rfl

/-- Preserving the provider identity does not preserve the exact authority
record when a probability band changes. Existing intents remain obstructed. -/
theorem changed_band_changes_evidence (md : QModel n m) (w c : ProbabilityBand)
    (hchange : w ≠ probBand md .warm ∨ c ≠ probBand md .cold) :
    RobustQuoteRecovery.evidence (replaceProbabilityBands md w c) ≠
      RobustQuoteRecovery.evidence md := by
  intro he
  rcases hchange with hw | hc
  · have hp := congrArg (fun ev : RobustQuoteRecovery.EvidenceView n m =>
      ev.warm.probability) he
    exact hw hp
  · have hp := congrArg (fun ev : RobustQuoteRecovery.EvidenceView n m =>
      ev.cold.probability) he
    exact hc hp

theorem new_bands_obstruct_old_acknowledgement (md : QModel n m)
    (w c : ProbabilityBand) (checkpoint : RobustQuoteRecovery.Checkpoint md)
    (commit : RobustQuoteRecovery.Commit md) (out : RobustQuote.Outcome md)
    (actual : RobustQuoteRecovery.StoreView md)
    (hauth : commit.intent.quoteEvidence = RobustQuoteRecovery.evidence md)
    (hchange : w ≠ probBand md .warm ∨ c ≠ probBand md .cold) :
    RobustQuoteRecovery.acknowledge md checkpoint commit out actual
      (RobustQuoteRecovery.evidence (replaceProbabilityBands md w c)) =
      .error "quote evidence changed after planning" := by
  apply RobustQuoteRecovery.quote_mutation_rejected
  rw [hauth]
  exact Ne.symm (changed_band_changes_evidence md w c hchange)

/-- Deterministic model inputs remain supplied membership hypotheses; learning
success probabilities does not establish setup or gross calibration. -/
structure DeterministicRealization (md : QModel n m) where
  warmSetup : Nat
  coldSetup : Nat
  warmGross : ℚ
  coldGross : ℚ
  warmSetup_mem : (setupBand md .warm).Contains warmSetup
  coldSetup_mem : (setupBand md .cold).Contains coldSetup
  warmGross_mem : (grossBand md .warm).Contains warmGross
  coldGross_mem : (grossBand md .cold).Contains coldGross

/-- On the simultaneous coverage event, the learned bands give an exact model
realization. No assumption about membership in the previous probability bands
is needed. -/
def calibratedRealization (md : QModel n m) (w c : ProbabilityBand)
    (d : DeterministicRealization md) (warmP coldP : ℚ)
    (hw : w.Contains warmP) (hc : c.Contains coldP) :
    Realization (replaceProbabilityBands md w c) where
  warm := ⟨d.warmSetup, d.warmGross, warmP,
    d.warmSetup_mem, d.warmGross_mem, hw⟩
  cold := ⟨d.coldSetup, d.coldGross, coldP,
    d.coldSetup_mem, d.coldGross_mem, hc⟩

@[simp] theorem calibrated_warm_probability (md : QModel n m) (w c : ProbabilityBand)
    (d : DeterministicRealization md) (wp cp : ℚ)
    (hw : w.Contains wp) (hc : c.Contains cp) :
    (calibratedRealization md w c d wp cp hw hc).warm.probability = wp := rfl

@[simp] theorem calibrated_cold_probability (md : QModel n m) (w c : ProbabilityBand)
    (d : DeterministicRealization md) (wp cp : ℚ)
    (hw : w.Contains wp) (hc : c.Contains cp) :
    (calibratedRealization md w c d wp cp hw hc).cold.probability = cp := rfl

/-- The contract fixes one quote model and one exact realization for the whole
episode. Its benchmark retains the nominal upper-setup reservation guard.
It does not compare against a controller with a larger exact-cost feasible set,
and it does not assert a regret bound across mid-episode quote changes. -/
def FrozenEpisodeGuarantee (md : QModel n m) (r : Realization md) : Prop :=
  ∀ (h : Nat) (s : State md),
    (lowerValue md h s ≤ Guarded.value (trueSystem md r) h s ∧
      Guarded.value (trueSystem md r) h s ≤ upperValue md h s) ∧
    (∀ a : Action, lowerQ md h s a ≤ Guarded.qValue (trueSystem md r) h s a ∧
      Guarded.qValue (trueSystem md r) h s a ≤ upperQ md h s a) ∧
    (0 ≤ Guarded.value (trueSystem md r) h s -
      Guarded.planValue (trueSystem md r) s
        (Guarded.policyPlan (trueSystem md r) (robustPolicy md) h s) ∧
    Guarded.value (trueSystem md r) h s -
      Guarded.planValue (trueSystem md r) s
        (Guarded.policyPlan (trueSystem md r) (robustPolicy md) h s) ≤
      Guarded.regretBudget (fun k => 2 * globalQRadius md k) h)

theorem frozen_episode_guarantee (md : QModel n m) (r : Realization md) :
    FrozenEpisodeGuarantee md r := by
  intro h s
  exact ⟨value_between md r h s, fun a => q_between md r h s a,
    robust_policy_regret md r h s⟩

/-- Finite-sample simultaneous coverage composes with the deterministic formal
contract by supplying hw and hc. Statistical failure probability is an outer
probability over the data, not a term silently added to the policy reward. -/
theorem calibrated_frozen_episode_guarantee (md : QModel n m) (w c : ProbabilityBand)
    (d : DeterministicRealization md) (wp cp : ℚ)
    (hw : w.Contains wp) (hc : c.Contains cp) :
    FrozenEpisodeGuarantee (replaceProbabilityBands md w c)
      (calibratedRealization md w c d wp cp hw hc) :=
  frozen_episode_guarantee _ _

end Komorebi.AVOC.Affine.CalibrationBridge
