import AVOC.GuardedPolicyRegret

namespace Komorebi.AVOC.Retry

/-- A single unresolved operation. `true` means resolved, not mathematically proved.
After an unresolved outcome, only `afterFault` changes the operational state. -/
structure Model (S : Type*) where
  enabled : S → Bool
  resolve : S → ℚ
  resolve_nonneg : ∀ s, 0 ≤ resolve s
  resolve_le_one : ∀ s, resolve s ≤ 1
  cost : S → ℚ
  gain : S → ℚ
  afterFault : S → S

def immediate {S : Type*} (m : Model S) (s : S) : ℚ :=
  m.resolve s * m.gain s - m.cost s

/-- Exact executable fault-inclusive expected net value. Ties abandon. -/
def retryValue {S : Type*} (m : Model S) : Nat → S → ℚ
  | 0, _ => 0
  | n + 1, s => if m.enabled s then
      max 0 (immediate m s + (1 - m.resolve s) * retryValue m n (m.afterFault s))
    else 0

def trialValue {S : Type*} (m : Model S) (n : Nat) (s : S) : ℚ :=
  immediate m s + (1 - m.resolve s) * retryValue m n (m.afterFault s)

def choose {S : Type*} (m : Model S) : Nat → S → Bool
  | 0, _ => false
  | n + 1, s => m.enabled s && decide (0 < trialValue m n s)

/-- None is the terminal state. False action is abandonment; true is a new attempt. -/
def system {S : Type*} (m : Model S) : Guarded.System (Option S) Bool Bool where
  actions st := match st with
    | none => {false}
    | some s => if m.enabled s then {false, true} else {false}
  actions_nonempty st := by cases st with
    | none => simp
    | some s => cases h : m.enabled s <;> simp [h]
  prob st a o := match st, a with
    | some s, true => if o then m.resolve s else 1 - m.resolve s
    | _, _ => if o then 0 else 1
  prob_nonneg st a o := by
    cases st with
    | none => cases a <;> cases o <;> norm_num
    | some s =>
      cases a with
      | false => cases o <;> norm_num
      | true => cases o with
        | false => exact sub_nonneg.mpr (m.resolve_le_one s)
        | true => exact m.resolve_nonneg s
  prob_sum_one st a := by
    cases st with
    | none => cases a <;> simp
    | some s => cases a <;> simp
  step st a o := match st, a, o with
    | some s, true, false => some (m.afterFault s)
    | _, _, _ => none
  reward st a := match st, a with
    | some s, true => immediate m s
    | _, _ => 0

variable {S : Type*} (m : Model S)

@[simp] theorem retryValue_zero (s : S) : retryValue m 0 s = 0 := rfl

theorem retryValue_nonneg (n : Nat) (s : S) : 0 ≤ retryValue m n s := by
  cases n with
  | zero => exact le_rfl
  | succ n => unfold retryValue; split <;> first | exact le_max_left _ _ | exact le_rfl

theorem disabled_value (n : Nat) (s : S) (h : m.enabled s = false) :
    retryValue m n s = 0 := by cases n <;> simp [retryValue, h]

theorem terminal_value (n : Nat) : Guarded.value (system m) n none = 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [Guarded.value_eq_q_of_optimal (system m) n none false (by simp [system])]
      · change (0 : ℚ) + (∑ o : Bool, (if o then 0 else 1) *
            Guarded.value (system m) n none) = 0
        simp [ih]
      · intro a ha
        have h : a = false := by simpa [system] using ha
        subst a; exact le_rfl

theorem abandon_q (n : Nat) (st : Option S) :
    Guarded.qValue (system m) n st false = 0 := by
  cases st <;>
    change (0 : ℚ) + (∑ o : Bool, (if o then 0 else 1) *
      Guarded.value (system m) n none) = 0
  all_goals simp [terminal_value]

theorem retry_q (n : Nat) (s : S) :
    Guarded.qValue (system m) n (some s) true =
      immediate m s + (1 - m.resolve s) * Guarded.value (system m) n (some (m.afterFault s)) := by
  change immediate m s + (∑ o : Bool, (if o then m.resolve s else 1 - m.resolve s) *
    Guarded.value (system m) n (if o then none else some (m.afterFault s))) = _
  simp [terminal_value]

theorem guarded_value_eq (n : Nat) (s : S) :
    Guarded.value (system m) n (some s) = retryValue m n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      by_cases he : m.enabled s = true
      · have ht : Guarded.qValue (system m) n (some s) true = trialValue m n s := by
          rw [retry_q, ih]; rfl
        change Guarded.value (system m) (n + 1) (some s) = _
        simp only [retryValue, he, ↓reduceIte]
        change Guarded.value (system m) (n + 1) (some s) = max 0 (trialValue m n s)
        apply le_antisymm
        · obtain ⟨a, ha, hm⟩ := Guarded.optimal_action_exists (system m) n (some s)
          rw [Guarded.value_eq_q_of_optimal (system m) n (some s) a ha hm]
          cases a
          · rw [abandon_q]; exact le_max_left _ _
          · rw [ht]; exact le_max_right _ _
        · apply max_le
          · have h := Guarded.q_le_value (system m) n (some s) false (by simp [system,he])
            simpa only [abandon_q] using h
          · rw [← ht]; exact Guarded.q_le_value (system m) n (some s) true (by simp [system,he])
      · have hf : m.enabled s = false := Bool.eq_false_iff.mpr he
        rw [Guarded.value_eq_q_of_optimal (system m) n (some s) false (by simp [system,hf])]
        · simp [abandon_q, retryValue,hf]
        · intro a ha
          have h : a = false := by simpa [system,hf] using ha
          subst a; exact le_rfl

def selector (n : Nat) : Option S → Bool
  | none => false
  | some s => choose m (n + 1) s

theorem selector_allowed (n : Nat) (st : Option S) :
    selector m n st ∈ (system m).actions st := by
  cases st with
  | none => simp [selector,system]
  | some s =>
    cases he : m.enabled s
    · simp [selector,choose,system,he]
    · have h := le_or_gt (trialValue m n s) 0
      simpa [selector,choose,system,he] using h

theorem selector_realizes (n : Nat) (st : Option S) :
    Guarded.qValue (system m) n st (selector m n st) = Guarded.value (system m) (n + 1) st := by
  cases st with
  | none => simp [selector,abandon_q,terminal_value]
  | some s =>
    by_cases he : m.enabled s = true
    · by_cases hp : 0 < trialValue m n s
      · simp only [selector,choose,he,hp,decide_true,Bool.and_self]
        rw [retry_q,guarded_value_eq,guarded_value_eq]
        simp only [retryValue,he,↓reduceIte]
        exact (max_eq_right (le_of_lt hp)).symm
      · have hle : trialValue m n s ≤ 0 := le_of_not_gt hp
        simp only [selector,choose,he,hp,decide_false,Bool.true_and]
        rw [abandon_q,guarded_value_eq]
        simp only [retryValue,he,↓reduceIte]
        exact (max_eq_left hle).symm
    · have hf : m.enabled s = false := Bool.eq_false_iff.mpr he
      simp [selector,choose,hf,abandon_q,guarded_value_eq,disabled_value]

def selectedPlan (n : Nat) (st : Option S) : Guarded.Plan Bool Bool n :=
  Guarded.policyPlan (system m) (selector m) n st

theorem selectedPlan_legal (n : Nat) (st : Option S) :
    Guarded.Legal (system m) st (selectedPlan m n st) :=
  Guarded.policyPlan_legal (system m) (selector m) (selector_allowed m) n st

theorem selectedPlan_value (n : Nat) (st : Option S) :
    Guarded.planValue (system m) st (selectedPlan m n st) = Guarded.value (system m) n st := by
  induction n generalizing st with
  | zero => rfl
  | succ n ih =>
    change (system m).reward st (selector m n st) +
      (∑ o, (system m).prob st (selector m n st) o *
        Guarded.planValue (system m) ((system m).step st (selector m n st) o)
          (selectedPlan m n ((system m).step st (selector m n st) o))) = _
    simp_rw [ih]
    exact selector_realizes m n st

theorem all_legal_plans_le_selected (n : Nat) (st : Option S)
    (p : Guarded.Plan Bool Bool n) (hp : Guarded.Legal (system m) st p) :
    Guarded.planValue (system m) st p ≤ Guarded.planValue (system m) st (selectedPlan m n st) := by
  rw [selectedPlan_value]
  exact Guarded.planValue_le_value (system m) st p hp

/-- This condition is essential. It holds for a fixed mixture of persistent
reliability types, not for repairs that can improve the service after a fault. -/
def NoRevival : Prop := ∀ s, immediate m s ≤ 0 → immediate m (m.afterFault s) ≤ 0

theorem no_revival_value_zero (h : NoRevival m) (n : Nat) (s : S)
    (hg : immediate m s ≤ 0) : retryValue m n s = 0 := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      have hz := ih (m.afterFault s) (h s hg)
      simp only [retryValue,hz,mul_zero,add_zero]
      split
      · exact max_eq_left hg
      · rfl

theorem profitable_trial (n : Nat) (s : S) (h : 0 < immediate m s) :
    0 < trialValue m n s := by
  have hz := mul_nonneg (sub_nonneg.mpr (m.resolve_le_one s))
    (retryValue_nonneg m n (m.afterFault s))
  unfold trialValue; linarith

theorem choose_threshold (h : NoRevival m) (n : Nat) (s : S) :
    choose m (n + 1) s = (m.enabled s && decide (0 < immediate m s)) := by
  by_cases hp : 0 < immediate m s
  · simp [choose,hp,profitable_trial m n s hp]
  · have hg : immediate m s ≤ 0 := le_of_not_gt hp
    have hz := no_revival_value_zero m h n (m.afterFault s) (h s hg)
    simp [choose,trialValue,hz,hp]

end Komorebi.AVOC.Retry
