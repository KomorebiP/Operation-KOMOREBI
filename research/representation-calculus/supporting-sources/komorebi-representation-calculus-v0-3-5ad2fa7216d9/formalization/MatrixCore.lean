import RepresentationCore
import Init.GrindInstances.Ring.Fin

/- Exact matrix semantics using Lean/Std only. No finite state enumeration. -/
namespace Komorebi.Representation.Matrix
open Lean.Grind
universe u v w
variable {R : Type u} [Semiring R]

abbrev Vec (R : Type u) (n : Nat) := Fin n → R
abbrev Mat (R : Type u) (n m : Nat) := Fin n → Fin m → R

def fsum : (n : Nat) → (Fin n → R) → R
  | 0, _ => 0
  | n+1, f => f 0 + fsum n (fun i => f i.succ)

theorem fsum_zero (n : Nat) : fsum n (fun _ => (0 : R)) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [fsum, ih, Semiring.add_zero]

theorem fsum_add (n : Nat) (f g : Fin n → R) :
    fsum n (fun i => f i + g i) = fsum n f + fsum n g := by
  induction n with
  | zero => simp only [fsum, Semiring.add_zero]
  | succ n ih =>
    simp only [fsum, ih]
    grind

theorem fsum_mul_left (n : Nat) (a : R) (f : Fin n → R) :
    fsum n (fun i => a * f i) = a * fsum n f := by
  induction n with
  | zero => simp only [fsum, Semiring.mul_zero]
  | succ n ih => simp only [fsum, ih, Semiring.left_distrib]

theorem fsum_mul_right (n : Nat) (f : Fin n → R) (a : R) :
    fsum n (fun i => f i * a) = fsum n f * a := by
  induction n with
  | zero => simp only [fsum, Semiring.zero_mul]
  | succ n ih => simp only [fsum, ih, Semiring.right_distrib]

theorem fsum_swap (n m : Nat) (f : Fin n → Fin m → R) :
    fsum n (fun i => fsum m (f i)) = fsum m (fun j => fsum n (fun i => f i j)) := by
  induction n with
  | zero => simp only [fsum, fsum_zero]
  | succ n ih =>
    simp only [fsum, ih, fsum_add]

def mv {n m : Nat} (M : Mat R n m) (x : Vec R m) : Vec R n :=
  fun i => fsum m (fun j => M i j * x j)

def mm {n m k : Nat} (M : Mat R n m) (N : Mat R m k) : Mat R n k :=
  fun i j => fsum m (fun a => M i a * N a j)

def eye (n : Nat) : Mat R n n := fun i j => if i = j then 1 else 0

def dot {n : Nat} (a x : Vec R n) : R := fsum n (fun i => a i * x i)

def rm {n m : Nat} (a : Vec R n) (M : Mat R n m) : Vec R m :=
  fun j => fsum n (fun i => a i * M i j)

theorem mv_mm {n m k : Nat} (M : Mat R n m) (N : Mat R m k) (x : Vec R k) :
    mv (mm M N) x = mv M (mv N x) := by
  funext i
  simp only [mv, mm]
  simp only [← fsum_mul_right, Semiring.mul_assoc]
  rw [fsum_swap]
  simp only [fsum_mul_left]

theorem dot_rm {n m : Nat} (a : Vec R n) (M : Mat R n m) (x : Vec R m) :
    dot (rm a M) x = dot a (mv M x) := by
  simp only [dot, rm, mv]
  simp only [← fsum_mul_right, Semiring.mul_assoc]
  rw [fsum_swap]
  simp only [fsum_mul_left]

theorem fsum_indicator (n : Nat) (x : Vec R n) (i : Fin n) :
    fsum n (fun j => if i = j then x j else 0) = x i := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    refine Fin.cases ?_ (fun i => ?_) i
    · have h0 : ∀ j : Fin n, ¬ ((0 : Fin (n+1)) = j.succ) := by
        intro j h; have := congrArg Fin.val h; simp at this
      simp only [fsum, ite_true, h0, ite_false, fsum_zero, Semiring.add_zero]
    · have h0 : ¬ (i.succ = (0 : Fin (n+1))) := by
        intro h; have := congrArg Fin.val h; simp at this
      simp only [fsum, h0, ite_false, Fin.succ_inj]
      rw [Semiring.add_comm, Semiring.add_zero]
      exact ih (fun j => x j.succ) i

theorem mv_eye (n : Nat) (x : Vec R n) : mv (eye n) x = x := by
  funext i
  have h : (fun j => (if i = j then (1 : R) else 0) * x j) =
      (fun j => if i = j then x j else 0) := by
    funext j; split <;> simp only [Semiring.one_mul, Semiring.zero_mul]
  change fsum n (fun j => (if i = j then (1 : R) else 0) * x j) = x i
  rw [h]
  exact fsum_indicator n x i

def linearSystem {d : Nat} {A : Type v} {O : Type w}
    (acts : A → Mat R d d) (obs : O → Vec R d) : System (Vec R d) A O R where
  step := fun a => mv (acts a)
  observe := fun j => dot (obs j)

def wordMatrix {d : Nat} {A : Type v} (acts : A → Mat R d d) : List A → Mat R d d
  | [] => eye d
  | a :: w => mm (wordMatrix acts w) (acts a)

theorem wordMatrix_run {d : Nat} {A : Type v} {O : Type w}
    (acts : A → Mat R d d) (obs : O → Vec R d) (w : List A) (x : Vec R d) :
    mv (wordMatrix acts w) x = run (linearSystem acts obs) w x := by
  induction w generalizing x with
  | nil => exact mv_eye d x
  | cons a w ih =>
    change mv (mm (wordMatrix acts w) (acts a)) x =
      run (linearSystem acts obs) w (mv (acts a) x)
    rw [mv_mm, ih]

def wordRow {d : Nat} {A : Type v} {O : Type w}
    (acts : A → Mat R d d) (obs : O → Vec R d) (w : List A) (j : O) : Vec R d :=
  rm (obs j) (wordMatrix acts w)

theorem wordRow_behavior {d : Nat} {A : Type v} {O : Type w}
    (acts : A → Mat R d d) (obs : O → Vec R d) (w : List A) (j : O) (x : Vec R d) :
    dot (wordRow acts obs w j) x = behavior (linearSystem acts obs) x w j := by
  unfold wordRow
  rw [dot_rm, wordMatrix_run]
  rfl


def unitVector (n : Nat) (i : Fin n) : Vec R n := fun j => if i = j then 1 else 0

theorem dot_unitVector (n : Nat) (a : Vec R n) (i : Fin n) :
    dot a (unitVector n i) = a i := by
  have hh : (fun j => a j * (if i = j then (1 : R) else 0)) =
      (fun j => if i = j then a j else 0) := by
    funext j; split <;> simp only [Semiring.mul_one, Semiring.mul_zero]
  change fsum n (fun j => a j * (if i = j then (1 : R) else 0)) = a i
  rw [hh]
  exact fsum_indicator n a i

theorem covector_ext {n : Nat} (a b : Vec R n)
    (h : ∀ x, dot a x = dot b x) : a = b := by
  funext i
  have hi := h (unitVector n i)
  simpa only [dot_unitVector] using hi


theorem dot_zero {n : Nat} (row : Vec R n) : dot row (fun _ => 0) = 0 := by
  simp only [dot, Semiring.mul_zero, fsum_zero]

end Komorebi.Representation.Matrix
