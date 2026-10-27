module
public import EuclidCost
public import DiscoveryLogic

@[expose] public section
namespace Komorebi.Costed
open Komorebi.Echelon Komorebi.Echelon.Cost
open Komorebi.Discovery Komorebi.Representation.Matrix

/-- Value and an explicitly stipulated high-level unit-operation count.
It is NOT a counter for compiled Lean instructions or elapsed time. -/
abbrev Eval (α : Type) := α × Nat

/-- Count comparison, remainder, quotient, product, subtraction in each nonterminal step. -/
def euclidEval (a b : Nat) : Eval (ℤ × ℤ) :=
  if h : b=0 then ((1,0),1)
  else
    let z := euclidEval b (a%b)
    ((z.1.2, z.1.1 - (a/b:Nat)*z.1.2),z.2+5)
termination_by b
decreasing_by exact Nat.mod_lt _ (Nat.pos_of_ne_zero h)

@[simp] theorem euclidEval_value (a b : Nat) : (euclidEval a b).1=euclidCoeff a b := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hz : b=0
    · subst b; simp [euclidEval]
    · rw [euclidEval,euclidCoeff_step a b hz]
      simp only [hz, ↓reduceDIte]
      rw [ih (a%b) (Nat.mod_lt a (Nat.pos_of_ne_zero hz)) b]

@[simp] theorem euclidEval_units (a b : Nat) :
    (euclidEval a b).2=5*euclidSteps a b+1 := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hz : b=0
    · subst b; simp [euclidEval]
    · rw [euclidEval,euclidSteps_step a b hz]
      simp only [hz, ↓reduceDIte]
      rw [ih (a%b) (Nat.mod_lt a (Nat.pos_of_ne_zero hz)) b]
      omega

/-- Separate recursive gcd, accounting for the separate gcd call in the predecessor. -/
def gcdEval (a b : Nat) : Eval Nat :=
  if h : b=0 then (a,1)
  else let z := gcdEval b (a%b); (z.1,z.2+2)
termination_by b
decreasing_by exact Nat.mod_lt _ (Nat.pos_of_ne_zero h)

@[simp] theorem gcdEval_value (a b : Nat) : (gcdEval a b).1=a.gcd b := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hz : b=0
    · subst b; simp [gcdEval]
    · rw [gcdEval]; simp only [hz, ↓reduceDIte]
      rw [ih (a%b) (Nat.mod_lt a (Nat.pos_of_ne_zero hz)) b]
      exact (Nat.gcd_comm b (a%b)).trans ((Nat.gcd_rec b a).symm.trans (Nat.gcd_comm b a))

@[simp] theorem gcdEval_units (a b : Nat) : (gcdEval a b).2=2*euclidSteps a b+1 := by
  induction b using Nat.strong_induction_on generalizing a with
  | h b ih =>
    by_cases hz : b=0
    · subst b; simp [gcdEval]
    · rw [gcdEval,euclidSteps_step a b hz]; simp only [hz, ↓reduceDIte]
      rw [ih (a%b) (Nat.mod_lt a (Nat.pos_of_ne_zero hz)) b]
      omega

/-- Two absolute values, one sign test and one sign multiplication cost four units. -/
def signedEuclidEval (q a : ℤ) : Eval (ℤ × ℤ) :=
  let z := euclidEval q.natAbs a.natAbs
  ((z.1.1, (if 0≤a then 1 else -1)*z.1.2),z.2+4)

@[simp] theorem signedEuclidEval_value (q a : ℤ) :
    (signedEuclidEval q a).1=smallBezout q a := by
  simp only [signedEuclidEval,euclidEval_value,smallBezout]
  split <;> simp

@[simp] theorem signedEuclidEval_units (q a : ℤ) :
    (signedEuclidEval q a).2=5*euclidSteps q.natAbs a.natAbs+5 := by
  simp [signedEuclidEval]

/-- A scalar dot product, evaluated recursively; multiplication and addition cost one each. -/
def dotEval {R : Type} [Semiring R] : (n : Nat) → (Fin n → R) → (Fin n → R) → Eval R
  | 0,_,_ => (0,0)
  | n+1,u,v =>
    let t := dotEval n (fun i => u i.succ) (fun i => v i.succ)
    (u 0*v 0+t.1,t.2+2)

@[simp] theorem dotEval_value {R : Type} [Semiring R] (n : Nat) (u v : Fin n → R) :
    (dotEval n u v).1=dot u v := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change u 0*v 0+(dotEval n _ _).1=u 0*v 0+fsum n _
    rw [ih]; rfl

@[simp] theorem dotEval_units {R : Type} [Semiring R] (n : Nat) (u v : Fin n → R) :
    (dotEval n u v).2=2*n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [dotEval,ih]; omega

/-- Strict-array cost interpretation: each of the d dot products is evaluated once.
The Lean value uses a function-valued vector. No compiler cost-refinement is assumed. -/
def rowEval {R : Type} [Semiring R] {d : Nat} (A : Mat R d d) (v : Fin d → R) : Eval (Fin d → R) :=
  (fun j => (dotEval d v (fun i => A i j)).1,
   ∑ j : Fin d, (dotEval d v (fun i => A i j)).2)

@[simp] theorem rowEval_value {R : Type} [Semiring R] {d : Nat} (A : Mat R d d) (v : Fin d → R) :
    (rowEval A v).1=rm v A := by
  ext j; simp only [rowEval,dotEval_value]; rfl

@[simp] theorem rowEval_units {R : Type} [Semiring R] {d : Nat} (A : Mat R d d) (v : Fin d → R) :
    (rowEval A v).2=2*d*d := by
  simp [rowEval]; ring

/-- Reconstruct every popped row from its word, matching the predecessor (no row cache). -/
def testEval {R : Type} [CommRing R] {d k o : Nat}
    (A : Fin k → Mat R d d) (O : Mat R o d) : Test k o → Eval (Fin d → R)
  | ([],j) => (O j,0)
  | (a::w,j) =>
    let t := testEval A O (w,j)
    let u := rowEval (A a) t.1
    (u.1,t.2+u.2)

@[simp] theorem testEval_value {R : Type} [CommRing R] {d k o : Nat}
    (A : Fin k → Mat R d d) (O : Mat R o d) (t : Test k o) :
    (testEval A O t).1=testValue (fun a => rowRight (A a)) O t := by
  rcases t with ⟨w,j⟩
  induction w with
  | nil => simp [testEval,testValue]
  | cons a w ih => simp only [testEval,testValue,rowEval_value,ih]; rfl

@[simp] theorem testEval_units {R : Type} [CommRing R] {d k o : Nat}
    (A : Fin k → Mat R d d) (O : Mat R o d) (t : Test k o) :
    (testEval A O t).2=2*d*d*t.1.length := by
  rcases t with ⟨w,j⟩
  induction w with
  | nil => simp [testEval]
  | cons a w ih => simp only [testEval,rowEval_units,ih,List.length_cons]; ring

end Komorebi.Costed
