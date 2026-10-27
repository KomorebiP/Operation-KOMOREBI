import Mathlib.Data.Matrix.Basic
import Mathlib.Tactic.Push

namespace Komorebi.AVOC.Affine

/-- Exact coefficients for a map R^n -> R^m. Dimensions are part of its type. -/
structure Signature (R : Type*) (n m : Nat) where
  linear : Matrix (Fin m) (Fin n) R
  offset : Fin m → R

variable {R : Type*} [Ring R] {n m k l : Nat}

omit [Ring R] in
@[ext] theorem Signature.ext {f g : Signature R n m}
    (ha : f.linear = g.linear) (hb : f.offset = g.offset) : f = g := by
  cases f; cases g; cases ha; cases hb; rfl

def eval (f : Signature R n m) (x : Fin n → R) : Fin m → R :=
  f.linear.mulVec x + f.offset

def identity (n : Nat) : Signature R n n := ⟨1, 0⟩

/-- `compose g f` executes f first and g second. -/
def compose (g : Signature R m k) (f : Signature R n m) : Signature R n k :=
  ⟨g.linear * f.linear, g.linear.mulVec f.offset + g.offset⟩

def add (f g : Signature R n m) : Signature R n m :=
  ⟨f.linear + g.linear, f.offset + g.offset⟩

@[simp] theorem eval_zero (f : Signature R n m) : eval f 0 = f.offset := by
  simp [eval]

@[simp] theorem eval_identity (x : Fin n → R) : eval (identity n) x = x := by
  simp [eval, identity]

@[simp] theorem eval_compose (g : Signature R m k) (f : Signature R n m)
    (x : Fin n → R) : eval (compose g f) x = eval g (eval f x) := by
  simp [eval, compose, Matrix.mulVec_add, Matrix.mulVec_mulVec, add_assoc]

@[simp] theorem eval_add (f g : Signature R n m) (x : Fin n → R) :
    eval (add f g) x = eval f x + eval g x := by
  simp [eval, add, Matrix.add_mulVec, add_left_comm, add_comm]

/-- Column basis. Including the zero probe recovers the affine offset. -/
def basis (j : Fin n) : Fin n → R := Pi.single j 1

@[simp] theorem eval_basis (f : Signature R n m) (j : Fin n) :
    eval f (basis j) = (fun i => f.linear i j) + f.offset := by
  rw [eval, basis, Matrix.mulVec_single_one]
  rfl

/-- A complete finite probe test, even for infinite coefficient rings. -/
theorem eq_of_zero_basis (f g : Signature R n m)
    (hzero : eval f 0 = eval g 0)
    (hbasis : ∀ j : Fin n, eval f (basis j) = eval g (basis j)) : f = g := by
  have hoff : f.offset = g.offset := by simpa using hzero
  apply Signature.ext _ hoff
  funext i j
  have h := congrFun (hbasis j) i
  simpa [eval_basis, hoff] using h

theorem eq_iff_zero_basis (f g : Signature R n m) :
    f = g ↔ eval f 0 = eval g 0 ∧ ∀ j : Fin n, eval f (basis j) = eval g (basis j) := by
  constructor
  · intro h; subst g; exact ⟨rfl, fun _ => rfl⟩
  · rintro ⟨h0,hb⟩; exact eq_of_zero_basis f g h0 hb

theorem eq_iff_eval (f g : Signature R n m) :
    f = g ↔ ∀ x, eval f x = eval g x := by
  constructor
  · intro h; subst g; intro x; rfl
  · intro h; exact eq_of_zero_basis f g (h 0) (fun j => h (basis j))

theorem mismatch_witness {f g : Signature R n m} (h : f ≠ g) :
    eval f 0 ≠ eval g 0 ∨ ∃ j : Fin n, eval f (basis j) ≠ eval g (basis j) := by
  by_contra hn
  push Not at hn
  exact h (eq_of_zero_basis f g hn.1 hn.2)

@[simp] theorem compose_identity (f : Signature R n m) : compose (identity m) f = f := by
  apply (eq_iff_eval _ _).2; intro x; simp

@[simp] theorem identity_compose (f : Signature R n m) : compose f (identity n) = f := by
  apply (eq_iff_eval _ _).2; intro x; simp

theorem compose_assoc (f : Signature R n m) (g : Signature R m k)
    (h : Signature R k l) : compose h (compose g f) = compose (compose h g) f := by
  apply (eq_iff_eval _ _).2; intro x; simp

/-- Exact finite coefficient comparison, not random testing. -/
def check [DecidableEq R] (f g : Signature R n m) : Bool :=
  decide (f.linear = g.linear ∧ f.offset = g.offset)

theorem check_iff [DecidableEq R] (f g : Signature R n m) :
    check f g = true ↔ ∀ x, eval f x = eval g x := by
  rw [check, decide_eq_true_eq]
  constructor
  · rintro ⟨ha,hb⟩; exact (eq_iff_eval _ _).1 (Signature.ext ha hb)
  · intro h; have he := (eq_iff_eval _ _).2 h; subst g; exact ⟨rfl,rfl⟩

def checkProbes [DecidableEq R] (f g : Signature R n m) : Bool :=
  decide (eval f 0 = eval g 0 ∧ ∀ j : Fin n, eval f (basis j) = eval g (basis j))

theorem checkProbes_iff [DecidableEq R] (f g : Signature R n m) :
    checkProbes f g = true ↔ ∀ x, eval f x = eval g x := by
  rw [checkProbes, decide_eq_true_eq, ← eq_iff_zero_basis, eq_iff_eval]

theorem probe_count (n : Nat) :
    (List.cons (0 : Fin n → R) (List.ofFn (fun j => basis (R:=R) j))).length = n + 1 := by
  simp

end Komorebi.AVOC.Affine
