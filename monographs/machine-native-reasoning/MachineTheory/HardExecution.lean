import MachineTheory.HardInquiry
import MachineTheory.RecipientExecution

/-!
# Execution and fixed-recipient specialization

The interpreter receives an actual state only as the environment simulation.
A controller chooses its root experiment in advance, then branches solely on its
report. The stored plan has no hidden-state selector. These exact semantics do
not verify arbitrary host code or assert physical fidelity of a supplied table.
-/
namespace Komorebi.MachineTheory.HardInquiry
open Finset
variable {X E O C R : Type}

structure Receipt (X E O C R : Type) where
  finalState : X
  artifact : C
  cost : R → ℕ
  history : List (E × O)

namespace Model

/-- A primitive execution receipt is extended by the experiment just performed. -/
def prepend (M : Model X E O C R) (e : E) (o : O) (r : Receipt X E O C R) : Receipt X E O C R :=
  { r with cost := fun j => M.stepCost e j + r.cost j, history := (e,o) :: r.history }

/-- This interpreter has no support argument and never selects using a hidden case label. -/
def execute (M : Model X E O C R) (charge : C → X → R → ℕ) :
    (h : ℕ) → Tree E O C h → X → Option (Receipt X E O C R)
  | 0, c, x => some ⟨x,c,charge c x,[]⟩
  | _+1, .inl c, x => some ⟨x,c,charge c x,[]⟩
  | h+1, .inr (e,k), x => if M.permitted e x then
      (k (M.observe e x)).bind (fun t =>
        (M.execute charge h t (M.next e x)).map (M.prepend e (M.observe e x)))
    else none

variable [DecidableEq X] [Fintype O] [DecidableEq O]

/-- Actual terminal work is maximized over the SAME possible post-action states. -/
def ChargesBounded (M : Model X E O C R) (charge : C → X → R → ℕ) : Prop :=
  ∀ c V x, x ∈ V → ∀ r, charge c x r ≤ M.terminalCost c V r

/-- Online bounds cover every actual execution, including the terminal recipient work. -/
theorem execution_sound (M : Model X E O C R) (charge : C → X → R → ℕ)
    (hc : M.ChargesBounded charge) (h : ℕ) (V : Finset X) (t : Tree E O C h)
    (hv : M.Valid h V t) (x : X) (hx : x ∈ V) :
    ∃ r, M.execute charge h t x = some r ∧ M.accept r.finalState r.artifact = true ∧
      r.cost ≤ (M.profile h V t).1 ∧ r.history.length ≤ h := by
  induction h generalizing V x with
  | zero =>
    exact ⟨⟨x,t,charge t x,[]⟩,rfl,hv.2 x hx,hc t V x hx,le_rfl⟩
  | succ h ih =>
    cases t with
    | inl c => exact ⟨⟨x,c,charge c x,[]⟩,rfl,hv.2 x hx,hc c V x hx,Nat.zero_le _⟩
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have hp := hv.1.2 x hx
      have hn := M.actual_next_mem hx e
      cases he : k (M.observe e x) with
      | none =>
        have hz : M.update V e (M.observe e x) = ∅ := by simpa only [he] using hv.2 (M.observe e x)
        rw [hz] at hn
        exact False.elim (Finset.notMem_empty _ hn)
      | some child =>
        have hh : M.Valid h (M.update V e (M.observe e x)) child := by simpa only [he] using hv.2 (M.observe e x)
        obtain ⟨r,hr,ha,hcost,hhist⟩ := ih _ child hh _ hn
        refine ⟨M.prepend e (M.observe e x) r, ?_, ha, ?_, Nat.succ_le_succ hhist⟩
        · simp only [execute,hp,ite_true,he,Option.bind_some,hr,Option.map_some]
        · intro j
          change M.stepCost e j + r.cost j ≤ M.stepCost e j + _
          apply Nat.add_le_add_left
          apply (hcost j).trans
          have hl := Finset.le_sup (s := (univ : Finset O))
            (f := fun o => (optional ((k o).map (M.profile h (M.update V e o)))).1 j)
            (mem_univ (M.observe e x))
          simpa only [he,Option.map_some,optional,Option.getD_some] using hl

/-- Literal node count, separate from execution and from the number of visited nodes. -/
def records : (h : ℕ) → Tree E O C h → ℕ
  | 0, _ => 1
  | _+1, .inl _ => 1
  | h+1, .inr (_,k) => 1 + ∑ o, ((k o).map (records h)).getD 0

omit [DecidableEq X] [DecidableEq O] in
 theorem records_pos (h : ℕ) (t : Tree E O C h) : 1 ≤ records h t := by
  cases h with
  | zero => exact le_rfl
  | succ h => cases t with
    | inl _ => exact le_rfl
    | inr _ => exact Nat.le_add_right _ _

theorem profile_records (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h) :
    (M.profile h V t).2 = records h t := by
  induction h generalizing V with
  | zero => rfl
  | succ h ih =>
    cases t with
    | inl _ => rfl
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      change 1 + _ = 1 + _
      congr 1
      apply Finset.sum_congr rfl
      intro o _
      cases he : k o with
      | none => simp [he,optional]
      | some child => simpa only [he,Option.map_some,optional,Option.getD_some] using ih (M.update V e o) child

/-- A concrete model using per-case terminal costs satisfies the required bound. -/
def withTerminalCharges (M : Model X E O C R) (charge : C → X → R → ℕ) : Model X E O C R :=
  { M with terminalCost := fun c V r => V.sup (fun x => charge c x r) }

omit [DecidableEq X] [Fintype O] [DecidableEq O] in
 theorem withTerminalCharges_bound (M : Model X E O C R) (charge : C → X → R → ℕ) :
    (M.withTerminalCharges charge).ChargesBounded charge := by
  intro c V x hx r
  exact Finset.le_sup (f := fun x => charge c x r) hx

variable [Fintype E] [Fintype C] [Fintype R]

instance profileLE : DecidableRel ((· ≤ ·) : Profile R → Profile R → Prop) :=
  fun p q => inferInstanceAs (Decidable ((∀ r, p.1 r ≤ q.1 r) ∧ p.2 ≤ q.2))

/-- A computable finite reducer with the same mathematical Pareto definition. -/
def prune (s : Finset (Profile R)) : Finset (Profile R) :=
  s.filter (fun p => ∀ q ∈ s, q ≤ p → p ≤ q)

omit [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O] [Fintype C] in
 theorem prune_eq_frontier (s : Finset (Profile R)) : prune s = HardPareto.frontier s := by
  ext p
  simp only [prune,mem_filter,HardPareto.mem_frontier]

/-- Executable finite profile recurrence, with no heuristic deletion. -/
def compute (M : Model X E O C R) : ℕ → Finset X → Finset (Profile R)
  | 0, V => prune (M.stops V)
  | h+1, V => prune (M.backup (M.compute h) V)

theorem compute_eq_solve (M : Model X E O C R) (h : ℕ) : M.compute h = M.solve h := by
  induction h with
  | zero => funext V; exact prune_eq_frontier _
  | succ h ih => funext V; simp only [compute,solve,ih,prune_eq_frontier]

theorem computed_budget_iff (M : Model X E O C R) (h : ℕ) (V : Finset X) (b : Profile R) :
    (∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t ≤ b) ↔
      ∃ p ∈ M.compute h V, p ≤ b := by
  rw [M.compute_eq_solve]
  exact M.joint_budget_iff h V b

/-- A witness for hard budgets also certifies all recipient outputs on actual executions. -/
theorem budget_execution (M : Model X E O C R) (charge : C → X → R → ℕ)
    (hc : M.ChargesBounded charge) (h : ℕ) (V : Finset X) (b : Profile R)
    (hb : ∃ p ∈ M.compute h V, p ≤ b) :
    ∃ t : Tree E O C h, M.Valid h V t ∧ records h t ≤ b.2 ∧
      ∀ x ∈ V, ∃ r, M.execute charge h t x = some r ∧
        M.accept r.finalState r.artifact = true ∧ r.cost ≤ b.1 ∧ r.history.length ≤ h := by
  obtain ⟨t,ht,hp⟩ := (M.computed_budget_iff h V b).mpr hb
  refine ⟨t,ht,?_,?_⟩
  · rw [← M.profile_records h V t]
    exact hp.2
  · intro x hx
    obtain ⟨r,hr,ha,hc,hh⟩ := M.execution_sound charge hc h V t ht x hx
    exact ⟨r,hr,ha,hc.trans hp.1,hh⟩

end Model

namespace AudienceBridge
variable {I : Type} {B Y : I → Type}
variable [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O]
  [Fintype C] [Fintype R]

/-- The fixed installed audience, not a newly designed decoder, defines terminal success. -/
noncomputable def attach (M : Model X E O C R)
    (A : RecipientExecution.Audience X C I B Y) : Model X E O C R := by
  classical
  exact { M with accept := fun x c => decide (A.Accepts x c) }

omit [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O] [Fintype C] [Fintype R] in
 theorem attached_accept (M : Model X E O C R)
    (A : RecipientExecution.Audience X C I B Y) (x : X) (c : C) :
    (attach M A).accept x c = true ↔ A.Accepts x c := by
  classical
  simp [attach]

omit [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O] [Fintype C] [Fintype R] in
/-- A single attained record over a current support requires a common artifact. -/
theorem terminal_common (M : Model X E O C R) (A : RecipientExecution.Audience X C I B Y)
    (V : Finset X) (c : C) :
    (attach M A).Terminal V c ↔ V.Nonempty ∧ ∀ x ∈ V, A.Accepts x c := by
  simp only [Model.Terminal,attached_accept]

/-- Core 5.1 instantiated with Block06's unchanged fixed-recipient acceptance. -/
theorem recipient_inquiry (M : Model X E O C R)
    (A : RecipientExecution.Audience X C I B Y) (h : ℕ) (V : Finset X) (b : Profile R) :
    (∃ t : Tree E O C h, (attach M A).Valid h V t ∧ (attach M A).profile h V t ≤ b) ↔
      ∃ p ∈ (attach M A).solve h V, p ≤ b :=
  (attach M A).joint_budget_iff h V b

end AudienceBridge
end Komorebi.MachineTheory.HardInquiry
