import AVOC.ExecutablePlanner

namespace Komorebi.AVOC.ExecutablePlanner

variable {S A O X : Type*}

/-- Conservative work reservation, not a bit-operation or wall-clock bound. -/
def workBound (maxActions maxObservations : Nat) : Nat → Nat
  | 0 => 1
  | n + 1 => 1 + maxActions * (1 + maxObservations * (1 + workBound maxActions maxObservations n))

structure BranchBound (m : Model S A O) (maxActions maxObservations : Nat) : Prop where
  actions : ∀ s, (m.actions s).length ≤ maxActions
  observations : m.observations.length ≤ maxObservations

theorem sum_map_bound (xs : List X) (f : X → Nat) (B : Nat)
    (h : ∀ x ∈ xs, f x ≤ B) : (xs.map f).sum ≤ xs.length * B := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      have hx := h x (by simp)
      have ht := ih (fun y hy => h y (by simp [hy]))
      simp only [List.map_cons, List.sum_cons, List.length_cons]
      nlinarith

@[simp] theorem backupEval_work (m : Model S A O) (next : S → Result A) (s : S) :
    (backupEval m next s).work =
      1 + ((m.actions s).map (fun a => (actionEval m next s a).work)).sum := by
  simp [backupEval, List.map_map, Function.comp_def]

theorem action_work_bound (m : Model S A O) (next : S → Result A)
    (B ko : Nat) (hn : ∀ s, (next s).work ≤ B)
    (ho : m.observations.length ≤ ko) (s : S) (a : A) :
    (actionEval m next s a).work ≤ 1 + ko * (1 + B) := by
  rw [actionEval_work]
  have hx := sum_map_bound m.observations
    (fun o => 1 + (next (m.step s a o)).work) (1 + B)
    (fun o _ => Nat.add_le_add_left (hn _) 1)
  have hm := Nat.mul_le_mul_right (1 + B) ho
  omega

/-- The counter in the actual evaluator stays within its preflight reservation. -/
theorem evaluate_work_le (m : Model S A O) (ka ko : Nat)
    (hb : BranchBound m ka ko) (n : Nat) (s : S) :
    (evaluate m n s).work ≤ workBound ka ko n := by
  induction n generalizing s with
  | zero => exact le_rfl
  | succ n ih =>
      change (backupEval m (evaluate m n) s).work ≤ _
      rw [backupEval_work, workBound]
      have hw := action_work_bound m (evaluate m n) (workBound ka ko n) ko ih hb.observations s
      have hs := sum_map_bound (m.actions s)
        (fun a => (actionEval m (evaluate m n) s a).work)
        (1 + ko * (1 + workBound ka ko n)) (fun a _ => hw a)
      have hm := Nat.mul_le_mul_right (1 + ko * (1 + workBound ka ko n)) (hb.actions s)
      omega

/-- Largest depth up to a requested cap whose conservative reservation fits.
The short scan/reservation arithmetic is outside the evaluator work convention. -/
def affordableDepth (ka ko budget : Nat) : Nat → Option Nat
  | 0 => if workBound ka ko 0 ≤ budget then some 0 else none
  | h + 1 => if workBound ka ko (h + 1) ≤ budget then some (h + 1)
      else affordableDepth ka ko budget h

theorem affordableDepth_sound (ka ko budget horizon depth : Nat)
    (h : affordableDepth ka ko budget horizon = some depth) :
    depth ≤ horizon ∧ workBound ka ko depth ≤ budget := by
  induction horizon with
  | zero =>
      simp only [affordableDepth] at h
      split at h
      · have he : 0 = depth := Option.some.inj h
        subst depth; exact ⟨le_rfl, by assumption⟩
      · contradiction
  | succ n ih =>
      simp only [affordableDepth] at h
      split at h
      · have he : n + 1 = depth := Option.some.inj h
        subst depth; exact ⟨le_rfl, by assumption⟩
      · obtain ⟨hd, hw⟩ := ih h
        exact ⟨Nat.le_trans hd (Nat.le_succ n), hw⟩

theorem affordableDepth_maximal (ka ko budget horizon depth k : Nat)
    (h : affordableDepth ka ko budget horizon = some depth)
    (hk : k ≤ horizon) (hw : workBound ka ko k ≤ budget) : k ≤ depth := by
  induction horizon with
  | zero =>
      have hd := (affordableDepth_sound ka ko budget 0 depth h).1
      omega
  | succ n ih =>
      simp only [affordableDepth] at h
      split at h
      · have he : n + 1 = depth := Option.some.inj h
        omega
      · have hkn : k ≤ n := by
          by_contra hh
          have he : k = n + 1 := by omega
          subst k; contradiction
        exact ih h hkn

/-- A failed reservation performs no recursive evaluation. A successful one
returns the actual result and remaining abstract work credit. -/
def runReserved (m : Model S A O) (ka ko depth budget : Nat) (s : S) :
    Option (Result A × Nat) :=
  if workBound ka ko depth ≤ budget then
    let r := evaluate m depth s
    some (r, budget - r.work)
  else none

theorem runReserved_success (m : Model S A O) (ka ko depth budget : Nat) (s : S)
    (hb : BranchBound m ka ko) (hw : workBound ka ko depth ≤ budget) :
    ∃ r remaining, runReserved m ka ko depth budget s = some (r, remaining) ∧
      r = evaluate m depth s ∧ r.work + remaining = budget ∧ r.work ≤ budget := by
  have hc := (evaluate_work_le m ka ko hb depth s).trans hw
  refine ⟨evaluate m depth s, budget - (evaluate m depth s).work,
    by simp [runReserved, hw], rfl, ?_, hc⟩
  omega

theorem runReserved_reject (m : Model S A O) (ka ko depth budget : Nat) (s : S)
    (h : budget < workBound ka ko depth) :
    runReserved m ka ko depth budget s = none := by
  simp [runReserved, Nat.not_le.mpr h]

/-- Separate repeated planning allocations cannot overspend their aggregate
abstract planning credits. Physical task fees are a different ledger. -/
theorem planning_trace_budget (used caps : List Nat)
    (h : List.Forall₂ (· ≤ ·) used caps) : used.sum ≤ caps.sum := by
  induction h with
  | nil => exact le_rfl
  | cons hhead _ ih => simpa using Nat.add_le_add hhead ih

end Komorebi.AVOC.ExecutablePlanner
