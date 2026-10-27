import AVOC.ExecutablePlanner
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Algebra.Order.Field.Basic

set_option linter.unusedSectionVars false

namespace Komorebi.AVOC.AdaptiveProbe

/-- A finite catalogue of possible workloads.  A probe has a deterministic
Boolean outcome in each world, a nonnegative fee, and a common terminal benefit
when it succeeds.  The benefit is operational value (for example avoided search
cost), not mathematical truth. -/
structure Model (Ω P : Type*) where
  detects : P → Ω → Bool
  fee : P → ℚ
  fee_nonneg : ∀ p, 0 ≤ fee p
  benefit : ℚ
  benefit_nonneg : 0 ≤ benefit

variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]

/-- The posterior is represented by the nonempty set of catalogue worlds still
consistent with all observed failures.  This is an exact uniform-catalogue
model. Duplicate catalogue entries may encode integer weights. -/
structure State (Ω P : Type*) [DecidableEq Ω] [DecidableEq P] where
  worlds : Finset Ω
  worlds_nonempty : worlds.Nonempty
  remaining : List P
  remaining_nodup : remaining.Nodup
  done : Bool

inductive Action (P : Type*) where
  | stop
  | probe (p : P)
  deriving Repr, DecidableEq

def successWorlds (m : Model Ω P) (s : State Ω P) (p : P) : Finset Ω :=
  s.worlds.filter (fun w => m.detects p w)

def failureWorlds (m : Model Ω P) (s : State Ω P) (p : P) : Finset Ω :=
  s.worlds.filter (fun w => !(m.detects p w))

@[simp] theorem successWorlds_subset (m : Model Ω P) (s : State Ω P) (p : P) :
    successWorlds m s p ⊆ s.worlds := Finset.filter_subset _ _

@[simp] theorem failureWorlds_subset (m : Model Ω P) (s : State Ω P) (p : P) :
    failureWorlds m s p ⊆ s.worlds := Finset.filter_subset _ _

theorem worlds_card_pos (s : State Ω P) : 0 < s.worlds.card :=
  Finset.card_pos.mpr s.worlds_nonempty

/-- Exact success probability under the uniform distribution on the currently
consistent catalogue worlds. -/
def successProb (m : Model Ω P) (s : State Ω P) (p : P) : ℚ :=
  (successWorlds m s p).card / s.worlds.card

theorem successProb_nonneg (m : Model Ω P) (s : State Ω P) (p : P) :
    0 ≤ successProb m s p := by
  unfold successProb
  exact div_nonneg (by positivity) (by positivity)

theorem successProb_le_one (m : Model Ω P) (s : State Ω P) (p : P) :
    successProb m s p ≤ 1 := by
  unfold successProb
  have hc : (successWorlds m s p).card ≤ s.worlds.card :=
    Finset.card_le_card (successWorlds_subset m s p)
  have hd : (0 : ℚ) < s.worlds.card := by exact_mod_cast worlds_card_pos s
  apply (div_le_iff₀ hd).2
  have hcq : ((successWorlds m s p).card : ℚ) ≤ (s.worlds.card : ℚ) := by
    exact_mod_cast hc
  simpa using hcq

theorem failure_card_add_success_card (m : Model Ω P) (s : State Ω P) (p : P) :
    (failureWorlds m s p).card + (successWorlds m s p).card = s.worlds.card := by
  classical
  have hu : failureWorlds m s p ∪ successWorlds m s p = s.worlds := by
    ext w
    by_cases hw : w ∈ s.worlds
    · cases hdet : m.detects p w <;> simp [failureWorlds, successWorlds, hw, hdet]
    · simp [failureWorlds, successWorlds, hw]
  have hd : Disjoint (failureWorlds m s p) (successWorlds m s p) := by
    refine Finset.disjoint_left.mpr ?_
    intro w hf hs
    have hff := (Finset.mem_filter.mp hf).2
    have hss := (Finset.mem_filter.mp hs).2
    cases h : m.detects p w <;> simp [h] at hff hss
  rw [← hu, Finset.card_union_of_disjoint hd]

theorem one_sub_successProb (m : Model Ω P) (s : State Ω P) (p : P) :
    1 - successProb m s p = (failureWorlds m s p).card / s.worlds.card := by
  have hsum : ((failureWorlds m s p).card : ℚ) +
      ((successWorlds m s p).card : ℚ) = (s.worlds.card : ℚ) := by
    exact_mod_cast (failure_card_add_success_card m s p)
  have hd : (s.worlds.card : ℚ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt (worlds_card_pos s))
  unfold successProb
  field_simp [hd]
  linarith

/-- Total failure update. If failure has zero probability, retain the prior
world set, matching the total-Bayes convention on impossible observations. -/
def afterFailure (m : Model Ω P) (s : State Ω P) (p : P) : State Ω P :=
  let ws := failureWorlds m s p
  if h : ws.Nonempty then
    ⟨ws, h, s.remaining.erase p, s.remaining_nodup.erase _, false⟩
  else
    ⟨s.worlds, s.worlds_nonempty, s.remaining.erase p, s.remaining_nodup.erase _, false⟩

def terminal (s : State Ω P) : State Ω P :=
  ⟨s.worlds, s.worlds_nonempty, [], by simp, true⟩

def actions (s : State Ω P) : Finset (Action P) :=
  if s.done then {.stop}
  else insert .stop (s.remaining.toFinset.image Action.probe)

theorem stop_mem_actions (s : State Ω P) : Action.stop ∈ actions s := by
  by_cases h : s.done <;> simp [actions, h]

theorem probe_mem_actions_iff (s : State Ω P) (p : P) :
    Action.probe p ∈ actions s ↔ s.done = false ∧ p ∈ s.remaining := by
  cases h : s.done
  · simp [actions, h]
  · simp [actions, h]

def probability (m : Model Ω P) (s : State Ω P) (a : Action P) (o : Bool) : ℚ :=
  match a with
  | .stop => if o then 0 else 1
  | .probe p => if o then successProb m s p else 1 - successProb m s p

def step (m : Model Ω P) (s : State Ω P) (a : Action P) (o : Bool) : State Ω P :=
  match a with
  | .stop => terminal s
  | .probe p => if o then terminal s else afterFailure m s p

def reward (m : Model Ω P) (s : State Ω P) : Action P → ℚ
  | .stop => 0
  | .probe p => successProb m s p * m.benefit - m.fee p

theorem probability_nonneg (m : Model Ω P) (s : State Ω P) (a : Action P) (o : Bool) :
    0 ≤ probability m s a o := by
  cases a with
  | stop => cases o <;> norm_num [probability]
  | probe p =>
      cases o with
      | false => simpa [probability] using sub_nonneg.mpr (successProb_le_one m s p)
      | true => simpa [probability] using successProb_nonneg m s p

theorem probability_sum_one (m : Model Ω P) (s : State Ω P) (a : Action P) :
    ∑ o : Bool, probability m s a o = 1 := by
  cases a <;> simp [probability]

def system (m : Model Ω P) : Guarded.System (State Ω P) (Action P) Bool where
  actions := actions
  actions_nonempty s := ⟨.stop, stop_mem_actions s⟩
  prob := probability m
  prob_nonneg := probability_nonneg m
  prob_sum_one := probability_sum_one m
  step := step m
  reward := reward m

/-- Executable action enumeration. -/
def actionList (s : State Ω P) : List (Action P) :=
  if s.done then [.stop]
  else .stop :: (s.remaining.map Action.probe)

@[simp] theorem mem_actionList (s : State Ω P) (a : Action P) :
    a ∈ actionList s ↔ a ∈ actions s := by
  cases h : s.done
  · simp [actionList, actions, h]
  · cases a with
    | stop => simp [actionList, actions, h]
    | probe p => simp [actionList, actions, h]

def executable (m : Model Ω P) : ExecutablePlanner.Model (State Ω P) (Action P) Bool where
  actions := actionList
  observations := [false, true]
  prob := probability m
  step := step m
  reward := reward m

theorem executable_realizes (m : Model Ω P) :
    ExecutablePlanner.Realizes (executable m) (system m) where
  actions_iff := mem_actionList
  observations_nodup := by simp [executable]
  observations_full := by
    ext o
    cases o <;> simp [executable]
  prob_eq := rfl
  step_eq := rfl
  reward_eq := rfl

theorem evaluated_value_exact (m : Model Ω P) (n : Nat) (s : State Ω P) :
    (ExecutablePlanner.evaluate (executable m) n s).score = Guarded.value (system m) n s :=
  ExecutablePlanner.evaluate_exact _ _ (executable_realizes m) n s

theorem evaluated_choice_optimal (m : Model Ω P) (n : Nat) (s : State Ω P) :
    ∃ a, (ExecutablePlanner.evaluate (executable m) (n + 1) s).choice = some a ∧
      a ∈ (system m).actions s ∧ ∀ b ∈ (system m).actions s,
        Guarded.qValue (system m) n s b ≤ Guarded.qValue (system m) n s a :=
  ExecutablePlanner.evaluate_choice_optimal
    (executable m) (system m) (executable_realizes m) n s

/-- Extract the executed choice, falling back to stop only at zero depth. -/
def selected (m : Model Ω P) (n : Nat) (s : State Ω P) : Action P :=
  (ExecutablePlanner.evaluate (executable m) (n + 1) s).choice.getD .stop

theorem selected_allowed (m : Model Ω P) (n : Nat) (s : State Ω P) :
    selected m n s ∈ (system m).actions s := by
  obtain ⟨a, ha, ham, _⟩ := evaluated_choice_optimal m n s
  simp [selected, ha, ham]

theorem selected_realizes_value (m : Model Ω P) (n : Nat) (s : State Ω P) :
    Guarded.qValue (system m) n s (selected m n s) = Guarded.value (system m) (n + 1) s := by
  obtain ⟨a, ha, ham, hmax⟩ := evaluated_choice_optimal m n s
  have hs : selected m n s = a := by simp [selected, ha]
  rw [hs]
  exact (Guarded.value_eq_q_of_optimal (system m) n s a ham hmax).symm

def selectedPlan (m : Model Ω P) : (n : Nat) → State Ω P → Guarded.Plan (Action P) Bool n
  | 0, _ => .done
  | n + 1, s => .node (selected m n s)
      (fun o => selectedPlan m n (step m s (selected m n s) o))

theorem selectedPlan_legal (m : Model Ω P) (n : Nat) (s : State Ω P) :
    Guarded.Legal (system m) s (selectedPlan m n s) := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih => exact ⟨selected_allowed m n s, fun o => ih _⟩

theorem selectedPlan_value (m : Model Ω P) (n : Nat) (s : State Ω P) :
    Guarded.planValue (system m) s (selectedPlan m n s) = Guarded.value (system m) n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      change reward m s (selected m n s) +
        (∑ o, probability m s (selected m n s) o *
          Guarded.planValue (system m) (step m s (selected m n s) o)
            (selectedPlan m n (step m s (selected m n s) o))) = _
      simp_rw [ih]
      exact selected_realizes_value m n s

theorem selectedPlan_optimal (m : Model Ω P) (n : Nat) (s : State Ω P)
    (p : Guarded.Plan (Action P) Bool n) (hp : Guarded.Legal (system m) s p) :
    Guarded.planValue (system m) s p ≤ Guarded.planValue (system m) s (selectedPlan m n s) := by
  rw [selectedPlan_value]
  exact Guarded.planValue_le_value (system m) s p hp

/-- A failed probe is not repeated by any legal future action. -/
theorem failed_probe_removed (m : Model Ω P) (s : State Ω P) (p : P) :
    p ∉ (afterFailure m s p).remaining := by
  unfold afterFailure
  dsimp
  split <;> exact s.remaining_nodup.not_mem_erase

/-- A true report is possible exactly when at least one retained catalogue world
makes that probe succeed. -/
theorem successProb_pos_iff (m : Model Ω P) (s : State Ω P) (p : P) :
    0 < successProb m s p ↔ (successWorlds m s p).Nonempty := by
  unfold successProb
  have hd : (0 : ℚ) < s.worlds.card := by exact_mod_cast worlds_card_pos s
  rw [div_pos_iff]
  constructor
  · rintro (hpos | hneg)
    · have : 0 < (successWorlds m s p).card := by exact_mod_cast hpos.1
      exact Finset.card_pos.mp this
    · have hn : ¬ ((successWorlds m s p).card : ℚ) < 0 := not_lt_of_ge (by positivity)
      exact False.elim (hn hneg.1)
  · intro h
    exact Or.inl ⟨by exact_mod_cast Finset.card_pos.mpr h, hd⟩

end Komorebi.AVOC.AdaptiveProbe
