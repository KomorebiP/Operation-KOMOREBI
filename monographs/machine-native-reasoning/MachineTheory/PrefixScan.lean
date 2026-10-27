import Mathlib.Data.List.Count
import Mathlib.Data.Int.Basic

/-!
# Core 6.4: capacity completion and a literal short-circuit root scan

The scan reads one Boolean report per row, retains both ordered sublists on
success, and stops at the first excessive prefix. Counts are natural numbers;
the source's nonnegative integer formulation is supplied separately.
-/
namespace Komorebi.MachineTheory.PrefixScan

/-- A completion assigns every unread row to exactly one of the two branches. -/
def Completable (m C a b : ℕ) : Prop :=
  ∃ u v : ℕ, u + v = m - (a+b) ∧ a+u ≤ C ∧ b+v ≤ C

/-- Core 6.4's numerical iff. Capacity feasibility is not query realizability. -/
theorem completion_iff (m C a b : ℕ) (hread : a+b ≤ m) (hsize : m ≤ 2*C) :
    Completable m C a b ↔ max a b ≤ C := by
  constructor
  · rintro ⟨u,v,_,ha,hb⟩
    omega
  · intro h
    let u := min (m-(a+b)) (C-a)
    refine ⟨u,m-(a+b)-u,?_,?_,?_⟩ <;> dsimp [u] <;> omega

/-- The exact integer statement in the book, including its declared range. -/
theorem integer_completion_iff (m C a b : ℤ) (_hC : 1 ≤ C)
    (_hm : 2 ≤ m) (hsize : m ≤ 2*C) (_ha : 0 ≤ a) (_hb : 0 ≤ b) (hread : a+b ≤ m) :
    (∃ u v : ℤ, 0 ≤ u ∧ 0 ≤ v ∧ u+v=m-a-b ∧ a+u≤C ∧ b+v≤C) ↔ max a b ≤ C := by
  constructor
  · rintro ⟨u,v,hu,hv,_,h1,h2⟩; omega
  · intro h
    refine ⟨min (m-a-b) (C-a),m-a-b-min (m-a-b) (C-a),?_,?_,?_,?_,?_⟩ <;> omega

variable {X : Type}

/-- Preserve original order within each report branch. -/
def prepend (x : X) (o : Bool) (p : List X × List X) : List X × List X :=
  if o then (p.1,x::p.2) else (x::p.1,p.2)

def partition (report : X → Bool) : List X → List X × List X
  | [] => ([],[])
  | x::xs => prepend x (report x) (partition report xs)

/-- Counters refer only to report-table reads and capacity-predicate evaluations. -/
structure Result (X : Type) where
  branches : Option (List X × List X)
  reads : ℕ
  checks : ℕ
  deriving Repr, DecidableEq

def full (report : X → Bool) (C a b : ℕ) (xs : List X) : Result X :=
  let p := partition report xs
  ⟨if max (a+p.1.length) (b+p.2.length) ≤ C then some p else none,xs.length,1⟩

/-- A predicate is tested before another row is read, also at the final prefix. -/
def stream (report : X → Bool) (C a b : ℕ) : List X → Result X
  | [] => ⟨if max a b ≤ C then some ([],[]) else none,0,1⟩
  | x::xs =>
      if max a b ≤ C then
        let o := report x
        let r := if o then stream report C a (b+1) xs else stream report C (a+1) b xs
        ⟨r.branches.map (prepend x o),r.reads+1,r.checks+1⟩
      else ⟨none,0,1⟩

@[simp] theorem partition_nil (report : X → Bool) : partition report [] = ([],[]) := rfl

theorem partition_filters (report : X → Bool) (xs : List X) :
    partition report xs = (xs.filter (fun x => !report x),xs.filter report) := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    simp only [partition,ih,prepend,List.filter_cons]
    cases report x <;> rfl

theorem partition_length (report : X → Bool) (xs : List X) :
    (partition report xs).1.length + (partition report xs).2.length = xs.length := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    simp only [partition,prepend]
    cases report x <;> simp_all <;> omega

/-- The literal streaming scan preserves the full scan's returned ordered branches. -/
theorem stream_branches (report : X → Bool) (C a b : ℕ) (xs : List X) :
    (stream report C a b xs).branches = (full report C a b xs).branches := by
  induction xs generalizing a b with
  | nil => rfl
  | cons x xs ih =>
    by_cases hab : max a b ≤ C
    · cases ho : report x
      · simp only [stream,hab,ite_true,ho,Bool.false_eq_true,ite_false,ih,full,
          partition,prepend,Option.map_ite,
          List.length_cons]
        simp only [Nat.add_assoc,Nat.add_comm]
      · simp only [stream,hab,ite_true,ho,ih,full,partition,prepend,
          Option.map_ite,List.length_cons]
        simp only [Nat.add_assoc,Nat.add_comm]
    · have hn : ¬ max (a+(partition report (x::xs)).1.length)
          (b+(partition report (x::xs)).2.length) ≤ C := by omega
      simp only [stream,hab,ite_false,full,hn]

/-- Early rejection can only omit a suffix of table reads. -/
theorem stream_reads_le (report : X → Bool) (C a b : ℕ) (xs : List X) :
    (stream report C a b xs).reads ≤ xs.length := by
  induction xs generalizing a b with
  | nil => exact Nat.zero_le _
  | cons x xs ih =>
    by_cases hab : max a b ≤ C
    · cases ho : report x <;> simp only [stream,hab,ite_true,ho,Bool.false_eq_true,ite_false]
      · exact Nat.succ_le_succ (ih (a+1) b)
      · exact Nat.succ_le_succ (ih a (b+1))
    · simp only [stream,hab,ite_false]; exact Nat.zero_le _

/-- The added capacity tests are metered; they are not free inference. -/
theorem stream_checks (report : X → Bool) (C a b : ℕ) (xs : List X) :
    (stream report C a b xs).checks = (stream report C a b xs).reads + 1 := by
  induction xs generalizing a b with
  | nil => rfl
  | cons x xs ih =>
    by_cases hab : max a b ≤ C
    · cases ho : report x <;> simp only [stream,hab,ite_true,ho,Bool.false_eq_true,ite_false]
      · rw [ih]
      · rw [ih]
    · simp only [stream,hab,ite_false]

/-- Success cannot be claimed without reading the complete candidate query. -/
theorem successful_reads (report : X → Bool) (C a b : ℕ) (xs : List X)
    (p : List X × List X) (hs : (stream report C a b xs).branches = some p) :
    (stream report C a b xs).reads = xs.length := by
  induction xs generalizing a b p with
  | nil => rfl
  | cons x xs ih =>
    by_cases hab : max a b ≤ C
    · cases ho : report x
      · simp only [stream,hab,ite_true,ho,Bool.false_eq_true,ite_false] at hs ⊢
        obtain ⟨q,hq,_⟩ := Option.map_eq_some_iff.mp hs
        exact congrArg (fun n => n+1) (ih (a+1) b q hq)
      · simp only [stream,hab,ite_true,ho] at hs ⊢
        obtain ⟨q,hq,_⟩ := Option.map_eq_some_iff.mp hs
        exact congrArg (fun n => n+1) (ih a (b+1) q hq)
    · simp only [stream,hab,ite_false] at hs
      cases hs

end Komorebi.MachineTheory.PrefixScan
