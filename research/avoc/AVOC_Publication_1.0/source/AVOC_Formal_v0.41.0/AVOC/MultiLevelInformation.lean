import AVOC.ExecutablePlanner
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Algebra.Order.Field.Basic

set_option linter.unusedSectionVars false

namespace Komorebi.AVOC.MultiLevel

/-- A finite information-acquisition model.  Probe reports are deterministic in
hidden catalogue worlds.  Positive reports certify a rank floor.  Warm reuse
and cold generation are terminal implementation choices whose net payoffs are
model data; they are not themselves proof certificates. -/
structure Model (Ω P : Type*) where
  detects : P → Ω → Bool
  level : P → Nat
  fee : P → ℚ
  fee_nonneg : ∀ p, 0 ≤ fee p
  reuseAvailable : Bool
  reusePayoff : Ω → ℚ
  coldPayoff : Ω → ℚ

variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]

/-- The retained worlds are exactly those consistent with the report history.
`lower_sound` keeps the algebraic certificate separate from catalogue odds. -/
structure State (m : Model Ω P) where
  worlds : Finset Ω
  worlds_nonempty : worlds.Nonempty
  remaining : List P
  remaining_nodup : remaining.Nodup
  lower : Nat
  done : Bool

inductive Action (P : Type*) where
  | stop
  | reuse
  | cold
  | probe (p : P)
  deriving Repr, DecidableEq

/-- Uniform-catalogue expectation. Duplicate catalogue entries may encode
integer weights. -/
def average (m : Model Ω P) (s : State m) (f : Ω → ℚ) : ℚ :=
  (∑ w ∈ s.worlds, f w) / s.worlds.card

@[simp] theorem average_const (m : Model Ω P) (s : State m) (c : ℚ) :
    average m s (fun _ => c) = c := by
  unfold average
  rw [Finset.sum_const]
  have h : (s.worlds.card : ℚ) ≠ 0 := by
    exact_mod_cast Nat.ne_of_gt (Finset.card_pos.mpr s.worlds_nonempty)
  simp [nsmul_eq_mul, h]


def successWorlds (m : Model Ω P) (s : State m) (p : P) : Finset Ω :=
  s.worlds.filter (fun w => m.detects p w)

def failureWorlds (m : Model Ω P) (s : State m) (p : P) : Finset Ω :=
  s.worlds.filter (fun w => !(m.detects p w))

@[simp] theorem successWorlds_subset (m : Model Ω P) (s : State m) (p : P) :
    successWorlds m s p ⊆ s.worlds := Finset.filter_subset _ _

@[simp] theorem failureWorlds_subset (m : Model Ω P) (s : State m) (p : P) :
    failureWorlds m s p ⊆ s.worlds := Finset.filter_subset _ _

theorem worlds_card_pos (s : State m) : 0 < s.worlds.card :=
  Finset.card_pos.mpr s.worlds_nonempty

def successProb (m : Model Ω P) (s : State m) (p : P) : ℚ :=
  (successWorlds m s p).card / s.worlds.card

theorem successProb_nonneg (m : Model Ω P) (s : State m) (p : P) :
    0 ≤ successProb m s p := by
  unfold successProb
  exact div_nonneg (by positivity) (by positivity)

theorem successProb_le_one (m : Model Ω P) (s : State m) (p : P) :
    successProb m s p ≤ 1 := by
  unfold successProb
  have hc : (successWorlds m s p).card ≤ s.worlds.card :=
    Finset.card_le_card (successWorlds_subset m s p)
  have hd : (0 : ℚ) < s.worlds.card := by exact_mod_cast worlds_card_pos s
  apply (div_le_iff₀ hd).2
  have hcq : ((successWorlds m s p).card : ℚ) ≤ (s.worlds.card : ℚ) := by
    exact_mod_cast hc
  simpa using hcq

theorem failure_card_add_success_card (m : Model Ω P) (s : State m) (p : P) :
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

theorem one_sub_successProb (m : Model Ω P) (s : State m) (p : P) :
    1 - successProb m s p = (failureWorlds m s p).card / s.worlds.card := by
  have hsum : ((failureWorlds m s p).card : ℚ) +
      ((successWorlds m s p).card : ℚ) = (s.worlds.card : ℚ) := by
    exact_mod_cast failure_card_add_success_card m s p
  have hd : (s.worlds.card : ℚ) ≠ 0 := by
    exact_mod_cast Nat.ne_of_gt (worlds_card_pos s)
  unfold successProb
  field_simp [hd]
  linarith

/-- Positive report.  Impossible reports use the total-update fallback and do
not upgrade the certified floor. -/
def afterSuccess (m : Model Ω P) (s : State m) (p : P) : State m :=
  let ws := successWorlds m s p
  if h : ws.Nonempty then
    { worlds := ws
      worlds_nonempty := h
      remaining := s.remaining.erase p
      remaining_nodup := s.remaining_nodup.erase _
      lower := max s.lower (m.level p)
      done := false }
  else
    { worlds := s.worlds
      worlds_nonempty := s.worlds_nonempty
      remaining := s.remaining.erase p
      remaining_nodup := s.remaining_nodup.erase _
      lower := s.lower
      done := false }

/-- Negative report.  It refines the catalogue but cannot lower or increase the
certified rank floor. -/
def afterFailure (m : Model Ω P) (s : State m) (p : P) : State m :=
  let ws := failureWorlds m s p
  if h : ws.Nonempty then
    { worlds := ws
      worlds_nonempty := h
      remaining := s.remaining.erase p
      remaining_nodup := s.remaining_nodup.erase _
      lower := s.lower
      done := false }
  else
    { worlds := s.worlds
      worlds_nonempty := s.worlds_nonempty
      remaining := s.remaining.erase p
      remaining_nodup := s.remaining_nodup.erase _
      lower := s.lower
      done := false }

def terminal (s : State m) : State m :=
  { worlds := s.worlds
    worlds_nonempty := s.worlds_nonempty
    remaining := []
    remaining_nodup := by simp
    lower := s.lower
    done := true }


/-- Executable action ordering. Ties prefer stop, then warm reuse, then cold
search, then the supplied probe order. -/
def actionList (m : Model Ω P) (s : State m) : List (Action P) :=
  if s.done then [.stop]
  else
    [.stop] ++ (if m.reuseAvailable then [.reuse] else []) ++ [.cold] ++
      s.remaining.map Action.probe

def actions (m : Model Ω P) (s : State m) : Finset (Action P) :=
  (actionList m s).toFinset

@[simp] theorem mem_actionList (m : Model Ω P) (s : State m) (a : Action P) :
    a ∈ actionList m s ↔ a ∈ actions m s := by simp [actions]

theorem stop_mem_actions (m : Model Ω P) (s : State m) : .stop ∈ actions m s := by
  cases h : s.done <;> simp [actions, actionList, h]

theorem cold_mem_actions_iff (m : Model Ω P) (s : State m) :
    .cold ∈ actions m s ↔ s.done = false := by
  cases h : s.done <;> simp [actions, actionList, h]

theorem reuse_mem_actions_iff (m : Model Ω P) (s : State m) :
    .reuse ∈ actions m s ↔ s.done = false ∧ m.reuseAvailable = true := by
  cases h : s.done <;> cases hr : m.reuseAvailable <;> simp [actions, actionList, h, hr]

theorem probe_mem_actions_iff (m : Model Ω P) (s : State m) (p : P) :
    .probe p ∈ actions m s ↔ s.done = false ∧ p ∈ s.remaining := by
  cases h : s.done <;> cases hr : m.reuseAvailable <;>
    simp [actions, actionList, h, hr]

def probability (m : Model Ω P) (s : State m) (a : Action P) (o : Bool) : ℚ :=
  match a with
  | .probe p => if o then successProb m s p else 1 - successProb m s p
  | _ => if o then 0 else 1

def step (m : Model Ω P) (s : State m) (a : Action P) (o : Bool) : State m :=
  match a with
  | .probe p => if o then afterSuccess m s p else afterFailure m s p
  | _ => terminal s

def reward (m : Model Ω P) (s : State m) : Action P → ℚ
  | .stop => 0
  | .reuse => average m s m.reusePayoff
  | .cold => average m s m.coldPayoff
  | .probe p => -m.fee p

theorem probability_nonneg (m : Model Ω P) (s : State m) (a : Action P) (o : Bool) :
    0 ≤ probability m s a o := by
  cases a with
  | stop => cases o <;> norm_num [probability]
  | reuse => cases o <;> norm_num [probability]
  | cold => cases o <;> norm_num [probability]
  | probe p =>
      cases o with
      | false => simpa [probability] using sub_nonneg.mpr (successProb_le_one m s p)
      | true => simpa [probability] using successProb_nonneg m s p

theorem probability_sum_one (m : Model Ω P) (s : State m) (a : Action P) :
    ∑ o : Bool, probability m s a o = 1 := by
  cases a <;> simp [probability]

def system (m : Model Ω P) : Guarded.System (State m) (Action P) Bool where
  actions := actions m
  actions_nonempty s := ⟨.stop, stop_mem_actions m s⟩
  prob := probability m
  prob_nonneg := probability_nonneg m
  prob_sum_one := probability_sum_one m
  step := step m
  reward := reward m

def executable (m : Model Ω P) : ExecutablePlanner.Model (State m) (Action P) Bool where
  actions := actionList m
  observations := [false,true]
  prob := probability m
  step := step m
  reward := reward m

theorem executable_realizes (m : Model Ω P) :
    ExecutablePlanner.Realizes (executable m) (system m) where
  actions_iff := mem_actionList m
  observations_nodup := by simp [executable]
  observations_full := by ext o; cases o <;> simp [executable]
  prob_eq := rfl
  step_eq := rfl
  reward_eq := rfl

theorem evaluated_value_exact (m : Model Ω P) (n : Nat) (s : State m) :
    (ExecutablePlanner.evaluate (executable m) n s).score = Guarded.value (system m) n s :=
  ExecutablePlanner.evaluate_exact _ _ (executable_realizes m) n s

theorem evaluated_choice_optimal (m : Model Ω P) (n : Nat) (s : State m) :
    ∃ a, (ExecutablePlanner.evaluate (executable m) (n+1) s).choice = some a ∧
      a ∈ (system m).actions s ∧ ∀ b ∈ (system m).actions s,
        Guarded.qValue (system m) n s b ≤ Guarded.qValue (system m) n s a :=
  ExecutablePlanner.evaluate_choice_optimal
    (executable m) (system m) (executable_realizes m) n s

def selected (m : Model Ω P) (n : Nat) (s : State m) : Action P :=
  (ExecutablePlanner.evaluate (executable m) (n+1) s).choice.getD .stop

theorem selected_allowed (m : Model Ω P) (n : Nat) (s : State m) :
    selected m n s ∈ (system m).actions s := by
  obtain ⟨a,ha,ham,_⟩ := evaluated_choice_optimal m n s
  simp [selected,ha,ham]

theorem selected_realizes_value (m : Model Ω P) (n : Nat) (s : State m) :
    Guarded.qValue (system m) n s (selected m n s) = Guarded.value (system m) (n+1) s := by
  obtain ⟨a,ha,ham,hmax⟩ := evaluated_choice_optimal m n s
  have hs : selected m n s = a := by simp [selected,ha]
  rw [hs]
  exact (Guarded.value_eq_q_of_optimal (system m) n s a ham hmax).symm

def selectedPlan (m : Model Ω P) : (n : Nat) → State m → Guarded.Plan (Action P) Bool n
  | 0, _ => .done
  | n+1, s => .node (selected m n s)
      (fun o => selectedPlan m n (step m s (selected m n s) o))

theorem selectedPlan_legal (m : Model Ω P) (n : Nat) (s : State m) :
    Guarded.Legal (system m) s (selectedPlan m n s) := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih => exact ⟨selected_allowed m n s, fun o => ih _⟩

theorem selectedPlan_value (m : Model Ω P) (n : Nat) (s : State m) :
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

theorem selectedPlan_optimal (m : Model Ω P) (n : Nat) (s : State m)
    (p : Guarded.Plan (Action P) Bool n) (hp : Guarded.Legal (system m) s p) :
    Guarded.planValue (system m) s p ≤ Guarded.planValue (system m) s (selectedPlan m n s) := by
  rw [selectedPlan_value]
  exact Guarded.planValue_le_value (system m) s p hp

theorem positive_report_updates_floor (m : Model Ω P) (s : State m) (p : P)
    (h : (successWorlds m s p).Nonempty) :
    (afterSuccess m s p).lower = max s.lower (m.level p) := by
  simp [afterSuccess,h]

theorem positive_report_level_le (m : Model Ω P) (s : State m) (p : P)
    (h : (successWorlds m s p).Nonempty) : m.level p ≤ (afterSuccess m s p).lower := by
  rw [positive_report_updates_floor m s p h]
  exact Nat.le_max_right _ _

theorem failure_preserves_floor (m : Model Ω P) (s : State m) (p : P) :
    (afterFailure m s p).lower = s.lower := by
  unfold afterFailure; dsimp; split <;> rfl

theorem success_removes_probe (m : Model Ω P) (s : State m) (p : P) :
    p ∉ (afterSuccess m s p).remaining := by
  unfold afterSuccess; dsimp; split <;> exact s.remaining_nodup.not_mem_erase

theorem failure_removes_probe (m : Model Ω P) (s : State m) (p : P) :
    p ∉ (afterFailure m s p).remaining := by
  unfold afterFailure; dsimp; split <;> exact s.remaining_nodup.not_mem_erase

theorem successProb_pos_iff (m : Model Ω P) (s : State m) (p : P) :
    0 < successProb m s p ↔ (successWorlds m s p).Nonempty := by
  unfold successProb
  have hd : (0 : ℚ) < s.worlds.card := by exact_mod_cast worlds_card_pos s
  rw [div_pos_iff]
  constructor
  · rintro (hpos | hneg)
    · have : 0 < (successWorlds m s p).card := by exact_mod_cast hpos.1
      exact Finset.card_pos.mp this
    · exact False.elim ((not_lt_of_ge (by positivity)) hneg.1)
  · intro h
    exact Or.inl ⟨by exact_mod_cast Finset.card_pos.mpr h, hd⟩

end Komorebi.AVOC.MultiLevel
