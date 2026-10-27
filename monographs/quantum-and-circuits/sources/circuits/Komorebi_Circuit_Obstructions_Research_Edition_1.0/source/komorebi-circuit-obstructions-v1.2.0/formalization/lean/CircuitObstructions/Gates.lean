import Std

/-!
# Legal classical NOT/CNOT/Toffoli circuits

Only classical Boolean gates are represented. Constructor proofs enforce distinct
control and target wires. A circuit may target or control any wire at any step.
No intermediate workspace-cleanness or output-passivity restriction is imposed.
-/
namespace CircuitObstructions

abbrev State (W : Type) := W → Bool

def write {W : Type} [DecidableEq W] (s : State W) (t : W) (b : Bool) : State W :=
  fun i => if i = t then b else s i

@[simp] theorem write_same {W : Type} [DecidableEq W] (s : State W) (t : W) (b : Bool) :
    write s t b t = b := by simp [write]

@[simp] theorem write_other {W : Type} [DecidableEq W] (s : State W) (t i : W)
    (b : Bool) (h : i ≠ t) : write s t b i = s i := by simp [write, h]

@[simp] theorem xor_cancel_right (a b : Bool) : Bool.xor (Bool.xor a b) b = a := by
  cases a <;> cases b <;> rfl

@[simp] theorem xor_cancel_left (a b : Bool) : Bool.xor a (Bool.xor a b) = b := by
  cases a <;> cases b <;> rfl

theorem xor_commute (a b : Bool) : Bool.xor a b = Bool.xor b a := by
  cases a <;> cases b <;> rfl

theorem xor_true_iff_ne (a b : Bool) : Bool.xor a b = true ↔ a ≠ b := by
  cases a <;> cases b <;> decide

inductive Gate (W : Type) where
  | not (target : W)
  | cnot (control target : W) (distinct : control ≠ target)
  | toffoli (control₁ control₂ target : W)
      (controls_distinct : control₁ ≠ control₂)
      (first_distinct : control₁ ≠ target)
      (second_distinct : control₂ ≠ target)

def Gate.eval {W : Type} [DecidableEq W] : Gate W → State W → State W
  | .not t, s => write s t (!s t)
  | .cnot c t _, s => write s t (Bool.xor (s t) (s c))
  | .toffoli a b t _ _ _, s => write s t (Bool.xor (s t) (s a && s b))

theorem Gate.eval_involutive {W : Type} [DecidableEq W] (g : Gate W) (s : State W) :
    g.eval (g.eval s) = s := by
  cases g with
  | not t =>
      funext i
      by_cases h : i = t
      · subst i; simp [Gate.eval]
      · simp [Gate.eval, write, h]
  | cnot c t hct =>
      funext i
      by_cases h : i = t
      · subst i; simp [Gate.eval, hct]
      · simp [Gate.eval, write, h]
  | toffoli a b t hab hat hbt =>
      funext i
      by_cases h : i = t
      · subst i; simp [Gate.eval, hat, hbt]
      · simp [Gate.eval, write, h]

theorem Gate.eval_injective {W : Type} [DecidableEq W] (g : Gate W)
    {s t : State W} (h : g.eval s = g.eval t) : s = t := by
  have hh := congrArg g.eval h
  simpa only [g.eval_involutive] using hh

abbrev Circuit (W : Type) := List (Gate W)

def run {W : Type} [DecidableEq W] : Circuit W → State W → State W
  | [], s => s
  | g :: gs, s => run gs (g.eval s)

@[simp] theorem run_nil {W : Type} [DecidableEq W] (s : State W) :
    run ([] : Circuit W) s = s := rfl

@[simp] theorem run_cons {W : Type} [DecidableEq W] (g : Gate W) (gs : Circuit W)
    (s : State W) : run (g :: gs) s = run gs (g.eval s) := rfl

theorem run_append {W : Type} [DecidableEq W] (p q : Circuit W) (s : State W) :
    run (p ++ q) s = run q (run p s) := by
  induction p generalizing s with
  | nil => rfl
  | cons g gs ih => exact ih (g.eval s)

@[simp] theorem run_reverse_run {W : Type} [DecidableEq W]
    (c : Circuit W) (s : State W) : run c.reverse (run c s) = s := by
  induction c generalizing s with
  | nil => rfl
  | cons g gs ih =>
      simp only [List.reverse_cons, run_append, run_cons, run_nil]
      rw [ih, Gate.eval_involutive]

@[simp] theorem run_run_reverse {W : Type} [DecidableEq W]
    (c : Circuit W) (s : State W) : run c (run c.reverse s) = s := by
  simpa only [List.reverse_reverse] using run_reverse_run c.reverse s

theorem run_injective {W : Type} [DecidableEq W] (c : Circuit W)
    {s t : State W} (h : run c s = run c t) : s = t := by
  have hh := congrArg (run c.reverse) h
  simpa only [run_reverse_run] using hh

def Gate.toffoliCost {W : Type} : Gate W → Nat
  | .toffoli _ _ _ _ _ _ => 1
  | _ => 0

def toffoliCount {W : Type} (c : Circuit W) : Nat :=
  (c.map Gate.toffoliCost).sum

theorem toffoliCount_append {W : Type} (p q : Circuit W) :
    toffoliCount (p ++ q) = toffoliCount p + toffoliCount q := by
  simp [toffoliCount]

theorem toffoliCount_reverse {W : Type} (c : Circuit W) :
    toffoliCount c.reverse = toffoliCount c := by
  simp [toffoliCount, List.map_reverse]

end CircuitObstructions
