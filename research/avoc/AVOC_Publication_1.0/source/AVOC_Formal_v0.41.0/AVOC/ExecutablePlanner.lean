import AVOC.GuardedModelError
import Mathlib.Algebra.BigOperators.Group.List.Basic

namespace Komorebi.AVOC.ExecutablePlanner

/-- Executable enumeration and transition interface. No classical choice occurs
in the evaluator. Runtime functions must themselves be executable. -/
structure Model (S A O : Type*) where
  actions : S → List A
  observations : List O
  prob : S → A → O → ℚ
  step : S → A → O → S
  reward : S → A → ℚ

structure Candidate (A : Type*) where
  action : A
  score : ℚ
  work : Nat
  deriving Repr

structure Result (A : Type*) where
  score : ℚ
  choice : Option A
  work : Nat
  deriving Repr

/-- First wins ties. All candidates have already been evaluated. -/
def best {A : Type*} : List (Candidate A) → Option (Candidate A)
  | [] => none
  | c :: cs =>
      match best cs with
      | none => some c
      | some d => if d.score ≤ c.score then some c else some d

/-- One action backup. Every recursive child is evaluated once and shared
between its numeric contribution and the explicit work counter. -/
def actionEval {S A O : Type*} (m : Model S A O) (next : S → Result A)
    (s : S) (a : A) : Candidate A :=
  let children := m.observations.map (fun o =>
    let r := next (m.step s a o)
    (m.prob s a o * r.score, 1 + r.work))
  ⟨a, m.reward s a + (children.map Prod.fst).sum,
    1 + (children.map Prod.snd).sum⟩

/-- One state backup. The cost convention is one unit per state visit,
action backup and observation edge. It is not a wall-time/bit-complexity bound. -/
def backupEval {S A O : Type*} (m : Model S A O) (next : S → Result A)
    (s : S) : Result A :=
  let rows := (m.actions s).map (actionEval m next s)
  let winner := best rows
  ⟨(winner.map Candidate.score).getD 0, winner.map Candidate.action,
    1 + (rows.map Candidate.work).sum⟩

/-- Exact zero-terminal-value finite lookahead. Horizon is structurally decreasing. -/
def evaluate {S A O : Type*} (m : Model S A O) : Nat → S → Result A
  | 0, _ => ⟨0, none, 1⟩
  | n + 1, s => backupEval m (evaluate m n) s

variable {S A O : Type*}

@[simp] theorem evaluate_zero (m : Model S A O) (s : S) :
    evaluate m 0 s = ⟨0, none, 1⟩ := rfl

@[simp] theorem actionEval_action (m : Model S A O) (next : S → Result A)
    (s : S) (a : A) : (actionEval m next s a).action = a := rfl

@[simp] theorem actionEval_score (m : Model S A O) (next : S → Result A)
    (s : S) (a : A) :
    (actionEval m next s a).score = m.reward s a +
      (m.observations.map (fun o => m.prob s a o * (next (m.step s a o)).score)).sum := by
  simp [actionEval, List.map_map, Function.comp_def]

@[simp] theorem actionEval_work (m : Model S A O) (next : S → Result A)
    (s : S) (a : A) :
    (actionEval m next s a).work = 1 +
      (m.observations.map (fun o => 1 + (next (m.step s a o)).work)).sum := by
  simp [actionEval, List.map_map, Function.comp_def]

theorem best_none_iff (xs : List (Candidate A)) : best xs = none ↔ xs = [] := by
  cases xs with
  | nil => simp [best]
  | cons c cs =>
      cases h : best cs <;> simp [best, h]
      split <;> simp

theorem best_spec (xs : List (Candidate A)) (hne : xs ≠ []) :
    ∃ c, best xs = some c ∧ c ∈ xs ∧ ∀ d ∈ xs, d.score ≤ c.score := by
  induction xs with
  | nil => contradiction
  | cons c cs ih =>
      cases h : best cs with
      | none =>
          have hz : cs = [] := (best_none_iff cs).mp h
          subst cs
          exact ⟨c, rfl, by simp, by simp⟩
      | some d =>
          have hn : cs ≠ [] := by intro hz; subst cs; simp [best] at h
          obtain ⟨e, he, hem, heb⟩ := ih hn
          have hed : e = d := Option.some.inj (he.symm.trans h)
          subst e
          by_cases hle : d.score ≤ c.score
          · refine ⟨c, by simp [best, h, hle], by simp, ?_⟩
            intro f hf
            rcases List.mem_cons.mp hf with rfl | hf
            · exact le_rfl
            · exact le_trans (heb f hf) hle
          · refine ⟨d, by simp [best, h, hle], by simp [hem], ?_⟩
            intro f hf
            rcases List.mem_cons.mp hf with rfl | hf
            · exact le_of_lt (lt_of_not_ge hle)
            · exact heb f hf

/-- This contract concerns enumeration and model correspondence. It does not
claim that a real LLM or filesystem has the declared transition law. -/
structure Realizes [DecidableEq A] [DecidableEq O] [Fintype O]
    (m : Model S A O) (sys : Guarded.System S A O) : Prop where
  actions_iff : ∀ s a, a ∈ m.actions s ↔ a ∈ sys.actions s
  observations_nodup : m.observations.Nodup
  observations_full : m.observations.toFinset = Finset.univ
  prob_eq : m.prob = sys.prob
  step_eq : m.step = sys.step
  reward_eq : m.reward = sys.reward

variable [DecidableEq A] [DecidableEq O] [Fintype O]

theorem observation_sum (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (f : O → ℚ) :
    (m.observations.map f).sum = ∑ o, f o := by
  rw [← List.sum_toFinset f h.observations_nodup, h.observations_full]

theorem actionEval_exact (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (next : S → Result A) (n : Nat)
    (hn : ∀ s, (next s).score = Guarded.value sys n s) (s : S) (a : A) :
    (actionEval m next s a).score = Guarded.qValue sys n s a := by
  rw [actionEval_score, observation_sum m sys h]
  simp only [h.prob_eq, h.step_eq, h.reward_eq, hn, Guarded.qValue, Guarded.expectation]

theorem backupEval_correct (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (next : S → Result A) (n : Nat)
    (hn : ∀ s, (next s).score = Guarded.value sys n s) (s : S) :
    (backupEval m next s).score = Guarded.value sys (n + 1) s ∧
    ∃ a, (backupEval m next s).choice = some a ∧ a ∈ sys.actions s ∧
      ∀ b ∈ sys.actions s, Guarded.qValue sys n s b ≤ Guarded.qValue sys n s a := by
  have hnon : (m.actions s).map (actionEval m next s) ≠ [] := by
    obtain ⟨a, ha⟩ := sys.actions_nonempty s
    have hm : actionEval m next s a ∈ (m.actions s).map (actionEval m next s) :=
      List.mem_map.mpr ⟨a, (h.actions_iff s a).mpr ha, rfl⟩
    intro he; rw [he] at hm; simp at hm
  obtain ⟨c, hc, hcm, hmax⟩ := best_spec _ hnon
  obtain ⟨a, ha, hca⟩ := List.mem_map.mp hcm
  subst c
  have ham := (h.actions_iff s a).mp ha
  have hm : ∀ b ∈ sys.actions s, Guarded.qValue sys n s b ≤ Guarded.qValue sys n s a := by
    intro b hb
    have hh := hmax (actionEval m next s b)
      (List.mem_map.mpr ⟨b, (h.actions_iff s b).mpr hb, rfl⟩)
    simpa only [actionEval_exact m sys h next n hn] using hh
  constructor
  · simp only [backupEval, hc, Option.map_some, Option.getD_some]
    rw [actionEval_exact m sys h next n hn]
    exact (Guarded.value_eq_q_of_optimal sys n s a ham hm).symm
  · exact ⟨a, by simp [backupEval, hc], ham, hm⟩

/-- The executed evaluator, not a separate idealized optimizer, agrees with the
existing constrained Bellman semantics at its declared lookahead depth. -/
theorem evaluate_exact (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (n : Nat) (s : S) :
    (evaluate m n s).score = Guarded.value sys n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih => exact (backupEval_correct m sys h (evaluate m n) n ih s).1

theorem evaluate_choice_optimal (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (n : Nat) (s : S) :
    ∃ a, (evaluate m (n + 1) s).choice = some a ∧ a ∈ sys.actions s ∧
      ∀ b ∈ sys.actions s, Guarded.qValue sys n s b ≤ Guarded.qValue sys n s a :=
  (backupEval_correct m sys h (evaluate m n) n (evaluate_exact m sys h n) s).2

end Komorebi.AVOC.ExecutablePlanner
