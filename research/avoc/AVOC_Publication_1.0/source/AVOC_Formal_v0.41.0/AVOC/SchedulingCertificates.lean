import AVOC.ScheduleCompletion

namespace Komorebi.AVOC.Scheduling

variable {P : Type*} [PartialOrder P] [DecidableEq P]

/-- Actual proof obligations, separate from the dependency-order bookkeeping. -/
def Certified (claim : P → Prop) (K : Finset P) : Prop :=
  ∀ x ∈ K, claim x

/-- A local proof rule supplies the conclusion from proofs of all prerequisites. -/
def LocalRule (claim : P → Prop) (x : P) : Prop :=
  (∀ y, y < x → claim y) → claim x

omit [DecidableEq P] in
theorem ready_with_rule_proves {claim : P → Prop} {K : Finset P} {x : P}
    (hK : Certified claim K) (hx : Ready K x) (hr : LocalRule claim x) : claim x := by
  apply hr
  intro y hy
  exact hK y (hx.2 y hy)

omit [PartialOrder P] in
theorem certified_insert {claim : P → Prop} {K : Finset P} {x : P}
    (hK : Certified claim K) (hx : claim x) : Certified claim (insert x K) := by
  intro y hy
  rcases Finset.mem_insert.mp hy with he | hy
  · simpa [he] using hx
  · exact hK y hy

theorem checked_step_preserves {claim : P → Prop} {K : Finset P} {x : P}
    (hi : IsIdeal K) (hc : Certified claim K)
    (hr : Ready K x) (hp : LocalRule claim x) :
    IsIdeal (insert x K) ∧ Certified claim (insert x K) :=
  ⟨ideal_insert hi hr,certified_insert hc (ready_with_rule_proves hc hr hp)⟩

theorem checked_batch_preserves [Fintype P] {claim : P → Prop} {K B : Finset P}
    (hi : IsIdeal K) (hc : Certified claim K)
    (hr : B ⊆ frontier K) (hp : ∀ x ∈ B, LocalRule claim x) :
    IsIdeal (K ∪ B) ∧ Certified claim (K ∪ B) := by
  refine ⟨frontier_batch_ideal hi hr,?_⟩
  intro x hx
  rcases Finset.mem_union.mp hx with hx | hx
  · exact hc x hx
  · exact ready_with_rule_proves hc (mem_frontier.mp (hr hx)) (hp x hx)

theorem legal_rules_certify {claim : P → Prop} {K : Finset P} {xs : List P}
    (hc : Certified claim K) (hl : Legal K xs)
    (hp : ∀ x ∈ xs, LocalRule claim x) : Certified claim (K ∪ xs.toFinset) := by
  induction xs generalizing K with
  | nil => simpa using hc
  | cons x xs ih =>
    have hnew := certified_insert hc (ready_with_rule_proves hc hl.1 (hp x (by simp)))
    have ht := ih hnew hl.2 (fun y hy => hp y (List.mem_cons_of_mem x hy))
    simpa [List.toFinset_cons,Finset.insert_union,Finset.union_insert] using ht

theorem certified_completion [Fintype P] {claim : P → Prop} {K : Finset P} {xs : List P}
    (hc : Certified claim K) (hl : Legal K xs)
    (hp : ∀ x ∈ xs, LocalRule claim x)
    (hdone : K ∪ xs.toFinset = Finset.univ) : ∀ x, claim x := by
  have hf := legal_rules_certify hc hl hp
  rw [hdone] at hf
  intro x
  exact hf x (Finset.mem_univ x)

/-- Readiness does not prove a claim: the single task is ready even when its
intended proposition is False. There is then no local certificate to admit it. -/
theorem ready_does_not_imply_truth :
    Ready (∅ : Finset (Fin 1)) 0 ∧ ¬ (False : Prop) := by
  constructor
  · constructor
    · simp
    · intro y hy
      have hlt : y.val < 0 := hy
      omega
  · exact not_false

end Komorebi.AVOC.Scheduling
