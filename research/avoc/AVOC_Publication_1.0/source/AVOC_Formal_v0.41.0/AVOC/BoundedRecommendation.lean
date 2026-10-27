import AVOC.PlannerGuarantee

namespace Komorebi.AVOC.ExecutablePlanner

variable {S A O : Type*}

structure Recommendation (A : Type*) where
  depth : Nat
  score : ℚ
  action : A
  work : Nat
  reservation : Nat
  remaining : Nat
  searched : Bool
  deriving Repr

def selectedDepth (ka ko horizon budget : Nat) : Nat :=
  (affordableDepth ka ko budget horizon).getD 0

/-- Preflight either reserves an affordable finite search or returns the supplied
fallback without evaluating a search tree. Remaining credit is actual, not
worst-case, credit. Choosing the depth is not claimed cost-optimal. -/
def recommend (m : Model S A O) (ka ko horizon budget : Nat)
    (fallback : S → A) (s : S) : Recommendation A :=
  match affordableDepth ka ko budget horizon with
  | none => ⟨0,0,fallback s,0,0,budget,false⟩
  | some d =>
      let r := evaluate m d s
      ⟨d,r.score,r.choice.getD (fallback s),r.work,workBound ka ko d,budget-r.work,true⟩

theorem selectedDepth_le (ka ko horizon budget : Nat) : selectedDepth ka ko horizon budget ≤ horizon := by
  cases h : affordableDepth ka ko budget horizon with
  | none => simp [selectedDepth, h]
  | some d => simpa [selectedDepth,h] using (affordableDepth_sound ka ko budget horizon d h).1

theorem recommend_depth (m : Model S A O) (ka ko horizon budget : Nat)
    (fallback : S → A) (s : S) :
    (recommend m ka ko horizon budget fallback s).depth = selectedDepth ka ko horizon budget := by
  cases h : affordableDepth ka ko budget horizon <;> simp [recommend,selectedDepth,h]

theorem recommend_action (m : Model S A O) (ka ko horizon budget : Nat)
    (fallback : S → A) (s : S) :
    (recommend m ka ko horizon budget fallback s).action =
      choose m fallback (selectedDepth ka ko horizon budget) s := by
  cases h : affordableDepth ka ko budget horizon <;> simp [recommend,selectedDepth,choose,h]

/-- Resource theorem for the entire recommendation entrypoint, including the
no-search fallback. Reservation arithmetic/parsing remain outside this work unit. -/
theorem recommend_credit (m : Model S A O) (ka ko horizon budget : Nat)
    (hb : BranchBound m ka ko) (fallback : S → A) (s : S) :
    let r := recommend m ka ko horizon budget fallback s
    r.work ≤ r.reservation ∧ r.reservation ≤ budget ∧ r.work + r.remaining = budget := by
  cases h : affordableDepth ka ko budget horizon with
  | none => simp [recommend,h]
  | some d =>
      have hw := evaluate_work_le m ka ko hb d s
      have hc := (affordableDepth_sound ka ko budget horizon d h).2
      simp only [recommend,h]
      exact ⟨hw,hc,by omega⟩

variable [DecidableEq A] [DecidableEq O] [Fintype O]

theorem recommend_score_exact (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (ka ko horizon budget : Nat) (fallback : S → A) (s : S) :
    (recommend m ka ko horizon budget fallback s).score =
      Guarded.value sys (selectedDepth ka ko horizon budget) s := by
  cases he : affordableDepth ka ko budget horizon with
  | none => simp [recommend,selectedDepth,he]
  | some d => simpa [recommend,selectedDepth,he] using evaluate_exact m sys h d s

theorem recommend_allowed (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (ka ko horizon budget : Nat) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (s : S) :
    (recommend m ka ko horizon budget fallback s).action ∈ sys.actions s := by
  rw [recommend_action]
  exact choose_allowed m sys h fallback hf _ s

theorem recommend_gap (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (ka ko budget n : Nat) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R) (s : S) :
    let r := recommend m ka ko (n + 1) budget fallback s
    Guarded.value sys (n + 1) s - Guarded.qValue sys n s r.action ≤
      2 * ((n + 1 - r.depth : Nat) : ℚ) * R := by
  dsimp only
  rw [recommend_action,recommend_depth]
  exact choose_gap m sys h fallback hf R hr n _ (selectedDepth_le ka ko (n + 1) budget) s

/-- Repeated executable recommendations with a declared per-stage allocation.
Unused credits need not be spent. They are not silently reused in a way that
changes the declared depth schedule. -/
theorem recommendation_policy_regret (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (ka ko : Nat) (caps : Nat → Nat) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R) (n : Nat) (s : S) :
    let selector := fun k t => (recommend m ka ko (k + 1) (caps k) fallback t).action
    0 ≤ Guarded.value sys n s - Guarded.planValue sys s (Guarded.policyPlan sys selector n s) ∧
    Guarded.value sys n s - Guarded.planValue sys s (Guarded.policyPlan sys selector n s) ≤
      Guarded.regretBudget (fun k => 2 * ((k + 1 - selectedDepth ka ko (k + 1) (caps k) : Nat) : ℚ) * R) n := by
  dsimp only
  simp_rw [recommend_action]
  exact lookahead_policy_regret m sys h fallback hf R hr _
    (fun k => selectedDepth_le ka ko (k + 1) (caps k)) n s

end Komorebi.AVOC.ExecutablePlanner
