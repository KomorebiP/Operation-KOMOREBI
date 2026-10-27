import AVOC.PlannerGuarantee
import AVOC.ArtifactWorkflowSource

namespace Komorebi.AVOC.WorkflowPlanner

open ArtifactWorkflow

variable {Ω P C O : Type*} [Fintype Ω] [Fintype O] [PartialOrder P]
  [DecidableEq P] [DecidableLT P] [DecidableEq C]

/-- The same total rational Bayes formula without an unnecessary noncomputable
annotation. Its agreement with the inherited definition is definitional. -/
def update (b : RationalBelief Ω) (E : RationalChannel Ω Bool) (d : Bool) : RationalBelief Ω :=
  if h : 0 < predictiveProb b E d then bayesUpdate b E d h else b

omit [PartialOrder P] [DecidableEq P] [DecidableLT P] [DecidableEq C] in
theorem update_eq (b : RationalBelief Ω) (E : RationalChannel Ω Bool) (d : Bool) :
    update b E d = bayesUpdateTotal b E d := rfl

def readyCheck (tasks : List P) (completed : Finset P) (x : P) : Bool :=
  decide (x ∉ completed) && tasks.all (fun y => decide (y < x → y ∈ completed))

omit [DecidableEq C] in
theorem readyCheck_correct (tasks : List P) (ht : ∀ x, x ∈ tasks)
    (completed : Finset P) (x : P) : readyCheck tasks completed x = true ↔ Scheduling.Ready completed x := by
  simp only [readyCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  constructor
  · rintro ⟨hx, hy⟩
    exact ⟨hx, fun y hlt => hy y (ht y) hlt⟩
  · rintro ⟨hx, hy⟩
    exact ⟨hx, fun y _ => hy y⟩

def precheck (p : Protocol Ω P C O) (tasks : List P) (s : State Ω P) : Action P C → Bool
  | .register x _ => readyCheck tasks s.completed x
  | .verify => match s.owner, s.slot.pending with
      | some _, some _ => true
      | _, _ => false
  | .admit => match s.owner, s.slot.pending, s.checked with
      | some x, some t, some r => Binding.validate (p.spec x) t r
      | _, _, _ => false
  | .stop => true

omit [DecidableEq C] in
theorem precheck_correct (p : Protocol Ω P C O) (tasks : List P)
    (ht : ∀ x, x ∈ tasks) (s : State Ω P) (a : Action P C) :
    precheck p tasks s a = true ↔ Precondition p s a := by
  cases a with
  | register x c => exact readyCheck_correct tasks ht s.completed x
  | verify => cases ho : s.owner <;> cases hp : s.slot.pending <;> simp [precheck, Precondition, ho, hp]
  | admit =>
      cases ho : s.owner <;> cases hp : s.slot.pending <;> cases hc : s.checked <;>
        simp [precheck, Precondition, ho, hp, hc]
  | stop => simp [precheck, Precondition]

def allowedCheck (p : Protocol Ω P C O) (tasks : List P) (s : State Ω P) (a : Action P C) : Bool :=
  decide (a = .stop) ||
    (decide (s.halted = false) && decide (fee p s a ≤ s.budget) && precheck p tasks s a)

theorem allowedCheck_correct (p : Protocol Ω P C O) (tasks : List P)
    (ht : ∀ x, x ∈ tasks) (s : State Ω P) (a : Action P C) :
    allowedCheck p tasks s a = true ↔ Allowed p s a := by
  simp only [allowedCheck, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq,
    precheck_correct p tasks ht, Allowed, and_assoc]

def pool (tasks : List P) (candidates : List C) : List (Action P C) :=
  [.stop, .verify, .admit] ++ tasks.flatMap (fun x => candidates.map (Action.register x))

omit [PartialOrder P] [DecidableEq P] [DecidableLT P] [DecidableEq C] in
theorem pool_complete (tasks : List P) (candidates : List C)
    (ht : ∀ x, x ∈ tasks) (hc : ∀ c, c ∈ candidates) (a : Action P C) :
    a ∈ pool tasks candidates := by
  cases a with
  | register x c =>
      apply List.mem_append_right
      apply List.mem_flatMap.mpr
      exact ⟨x, ht x, List.mem_map.mpr ⟨c, hc c, rfl⟩⟩
  | verify => simp [pool]
  | admit => simp [pool]
  | stop => simp [pool]

def step (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) (d : Bool) : State Ω P :=
  match a with
  | .register x c => registerStep p s x c
  | .verify =>
      { charge p s .verify with
        belief := update s.belief (Filtered.reportChannel (p.rawChannel s) (report p s)) d
        checked := if d then currentReceipt p s else none }
  | .admit => admitStep p s
  | .stop => { s with halted := true }

omit [DecidableLT P] [DecidableEq C] in
theorem step_eq (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) (d : Bool) :
    step p s a d = ArtifactWorkflow.step p s a d := by
  cases a <;> rfl

/-- This runs the actual v0.17 staged process, not a parallel Python redefinition.
Enumeration order puts stop first so it wins exact ties. -/
def model (p : Protocol Ω P C O) (tasks : List P) (candidates : List C) :
    ExecutablePlanner.Model (State Ω P) (Action P C) Bool where
  actions s := (pool tasks candidates).filter (allowedCheck p tasks s)
  observations := [false, true]
  prob s a d := predictiveProb s.belief (channel p s a) d
  step := step p
  reward := reward p

omit [PartialOrder P] [DecidableEq P] [DecidableLT P] [DecidableEq C] in
theorem pool_length (tasks : List P) (candidates : List C) :
    (pool tasks candidates).length = 3 + tasks.length * candidates.length := by
  simp [pool, List.length_flatMap]
  omega

/-- A computable catalogue-wide branching cap for reservation. This counts
all report branches, including zero-probability branches. -/
theorem model_branch_bound (p : Protocol Ω P C O) (tasks : List P) (candidates : List C) :
    ExecutablePlanner.BranchBound (model p tasks candidates)
      (3 + tasks.length * candidates.length) 2 := by
  constructor
  · intro s
    have h := List.length_filter_le (allowedCheck p tasks s) (pool tasks candidates)
    simpa only [model, pool_length] using h
  · exact le_rfl

variable [Fintype P] [Fintype C]

theorem model_realizes (p : Protocol Ω P C O) (tasks : List P) (candidates : List C)
    (ht : ∀ x, x ∈ tasks) (hc : ∀ c, c ∈ candidates) :
    ExecutablePlanner.Realizes (model p tasks candidates) (controller p) := by
  constructor
  · intro s a
    simp only [model, List.mem_filter, allowedCheck_correct p tasks ht]
    rw [mem_actions]
    exact and_iff_right (pool_complete tasks candidates ht hc a)
  · change ([false, true] : List Bool).Nodup; decide
  · ext d; cases d <;> simp [model]
  · rfl
  · funext s a d; exact step_eq p s a d
  · rfl

/-- The executable selector inherits the complete source/certification/budget
invariant for every planning-depth schedule, even depth zero. -/
theorem executable_policy_source_safe (p : Protocol Ω P C O) (hp : CatalogueParsed p)
    (tasks : List P) (candidates : List C) (ht : ∀ x, x ∈ tasks) (hc : ∀ c, c ∈ candidates)
    (depth : Nat → Nat) (B n : Nat) (s : State Ω P) (hs : SourceSafe p B s) :
    Guarded.TreeSafe (controller p) (SourceSafe p B) s
      (Guarded.policyPlan (controller p)
        (fun k t => ExecutablePlanner.choose (model p tasks candidates) (fun _ => .stop) (depth k) t) n s) := by
  apply source_bound_approximate_policy_safe p hp _ _ B n s hs
  intro k t
  apply (mem_actions p t _).mp
  exact ExecutablePlanner.choose_allowed _ _ (model_realizes p tasks candidates ht hc)
    (fun _ => .stop) (fun t => (mem_actions p t .stop).mpr (stop_allowed p t)) (depth k) t

/-- Performance of the concrete executable workflow planner, relative to the
same protected-snapshot/public-report model, not a different information regime. -/
theorem executable_policy_regret (p : Protocol Ω P C O)
    (tasks : List P) (candidates : List C) (ht : ∀ x, x ∈ tasks) (hc : ∀ c, c ∈ candidates)
    (R : ℚ) (hr : ∀ s a, Allowed p s a → |reward p s a| ≤ R)
    (depth : Nat → Nat) (hd : ∀ k, depth k ≤ k + 1) (n : Nat) (s : State Ω P) :
    0 ≤ Guarded.value (controller p) n s - Guarded.planValue (controller p) s
      (Guarded.policyPlan (controller p)
        (fun k t => ExecutablePlanner.choose (model p tasks candidates) (fun _ => .stop) (depth k) t) n s) ∧
    Guarded.value (controller p) n s - Guarded.planValue (controller p) s
      (Guarded.policyPlan (controller p)
        (fun k t => ExecutablePlanner.choose (model p tasks candidates) (fun _ => .stop) (depth k) t) n s) ≤
    Guarded.regretBudget (fun k => 2 * ((k + 1 - depth k : Nat) : ℚ) * R) n := by
  apply ExecutablePlanner.lookahead_policy_regret _ _ (model_realizes p tasks candidates ht hc)
    (fun _ => .stop) (fun t => (mem_actions p t .stop).mpr (stop_allowed p t)) R _ depth hd n s
  intro t a ha
  exact hr t a ((mem_actions p t a).mp ha)

end Komorebi.AVOC.WorkflowPlanner
