import AVOC.SynthesisPromotion

namespace Komorebi.AVOC.SynthesisExamples
open Synthesis

def pairReference : Program := .neg (.disjunction (.neg (.variable .first)) (.neg (.variable .second)))
def pairCompact : Program := .conjunction (.variable .first) (.variable .second)
def guardReference : Program := .neg (.disjunction (.neg (.variable .first))
  (.disjunction (.neg (.variable .second)) (.neg (.variable .third))))
def guardCompact : Program := .conjunction (.variable .first)
  (.conjunction (.variable .second) (.variable .third))

theorem pair_equivalent : Equivalent pairCompact pairReference := by
  intro s; rcases s with ⟨a,b,c⟩
  cases a <;> cases b <;> rfl

theorem guard_equivalent : Equivalent guardCompact guardReference := by
  intro s; rcases s with ⟨a,b,c⟩
  cases a <;> cases b <;> cases c <;> rfl

theorem pair_strictly_smaller : nodes pairCompact = 3 ∧ nodes pairReference = 6 := by decide

theorem guard_strictly_smaller : nodes guardCompact = 5 ∧ nodes guardReference = 9 := by decide

theorem layer_cardinality : poolSize 1 = 85 ∧ poolSize 2 = 21845 := by decide

theorem protected_function_not_constant : check (.literal true) pairReference = false := by decide

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
theorem pair_generated_replacement : synthesize pairReference 1 85 10000 = pairCompact := by decide

theorem zero_credit_retains_reference : synthesize pairReference 2 21845 0 = pairReference := by
  exact (insufficient_generation_no_search _ _ _ _ (by decide)).1

theorem zero_credit_no_search_charge : searchSpent pairReference 2 21845 0 = 0 := by
  exact (insufficient_generation_no_search _ _ _ _ (by decide)).2

theorem pair_search_charge : searchSpent pairReference 1 85 10000 = 6890 := by decide

/-- Semantic checking is not limited to the inputs observed on a workload. -/
theorem generated_pair_every_input (s : Input) :
    run (synthesize pairReference 1 85 10000) s = (s.first && s.second) := by
  rw [pair_generated_replacement]
  rfl

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
theorem pair_campaign_promotes :
    (campaign pairReference 10000 100000 1 85 10000).accepted.journal.current.active = pairCompact := by decide

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
theorem pair_campaign_net :
    (campaign pairReference 10000 100000 1 85 10000).net = 23029 := by decide

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
theorem better_program_unprofitable_search :
    (campaign pairReference 1 100000 1 85 10000).net = -6968 := by decide

end Komorebi.AVOC.SynthesisExamples
