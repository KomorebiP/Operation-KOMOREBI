import AVOC.SemanticSearchBudget
import AVOC.SynthesisPromotion

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

/-- Declared all-input query tariff, computed from cached sizes before the query.
This is distinct from the one-time semantic library construction charge. -/
def queryFee (reference : Program) (entries : List Entry) : Nat :=
  (entries.map (fun e => 8*(nodes reference+e.size+1))).sum

/-- Use the unchanged v0.25 contract/promotion authority. Search and query charges
are removed before credit is made available to the promotion check. -/
def submitBank {total : Nat} (search : PaidRun total) (reference : Program) (calls : Nat) :
    Submission reference calls (search.remaining - queryFee reference search.bank.entries) :=
  submit reference calls (search.remaining - queryFee reference search.bank.entries)
    (select reference reference (codes search.bank.entries))

theorem bank_submission_semantics {total : Nat} (search : PaidRun total)
    (reference : Program) (calls : Nat) :
    Equivalent (submitBank search reference calls).journal.current.active reference :=
  submission_contract _ _ _ _

theorem bank_submission_replay {total : Nat} (search : PaidRun total)
    (reference : Program) (calls : Nat) :
    DurableUpgrade.replay
      (authority reference calls (search.remaining-queryFee reference search.bank.entries))
      (DurableUpgrade.initial reference)
      (submitBank search reference calls).commands =
      .ok (submitBank search reference calls).journal :=
  submission_replays _ _ _ _

theorem bank_submission_total_cost {total : Nat} (search : PaidRun total)
    (reference : Program) (calls : Nat)
    (hq : queryFee reference search.bank.entries ≤ search.remaining) :
    search.work.charge + queryFee reference search.bank.entries +
      (submitBank search reference calls).journal.current.evaluationSpent +
      (submitBank search reference calls).journal.current.switchSpent ≤ total := by
  have hs := search.conserved
  have hp := submission_budget reference calls
    (search.remaining - queryFee reference search.bank.entries)
    (select reference reference (codes search.bank.entries))
  change (submitBank search reference calls).journal.current.evaluationSpent +
    (submitBank search reference calls).journal.current.switchSpent ≤
    search.remaining - queryFee reference search.bank.entries at hp
  omega

end Komorebi.AVOC.SemanticSynthesis
