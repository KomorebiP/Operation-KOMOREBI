import MachineTheory.PrefixScan
import MachineTheory.BinaryDiagnosis

/-!
# A concrete ordered depth-first compiler on the inherited controller type

The full and streaming compilers have identical repair order, experiment order,
left-before-right recursion, permissions, horizons and empty-branch handling.
Only the root-table scan differs. Model acquisition, permission and terminal
checking, list allocation and capacity arithmetic are not free by convention:
the two counters here deliberately meter report reads and capacity tests only.
-/
namespace Komorebi.MachineTheory.OrderedCompiler
open HardInquiry
variable {X E C A B : Type}

structure Run (A : Type) where
  answer : Option A
  reads : ℕ
  checks : ℕ
  deriving Repr, DecidableEq

namespace Run

def fail : Run A := ⟨none,0,0⟩
def pure (a : A) : Run A := ⟨some a,0,0⟩

def bind (r : Run A) (f : A → Run B) : Run B :=
  match r.answer with
  | none => ⟨none,r.reads,r.checks⟩
  | some a => let s := f a; ⟨s.answer,r.reads+s.reads,r.checks+s.checks⟩

def map (f : A → B) (r : Run A) : Run B :=
  ⟨r.answer.map f,r.reads,r.checks⟩

/-- Same result and no more report-table reads; extra predicate work is separate. -/
def Refines (s t : Run A) : Prop := s.answer=t.answer ∧ s.reads≤t.reads

theorem refines_refl (r : Run A) : Refines r r := ⟨rfl,le_rfl⟩

theorem bind_refines (r s : Run A) (f g : A → Run B) (hr : Refines r s)
    (hf : ∀ a, Refines (f a) (g a)) : Refines (bind r f) (bind s g) := by
  rcases hr with ⟨he,hle⟩
  cases ha : r.answer with
  | none => simp only [bind,ha,← he,Refines]; exact ⟨trivial,hle⟩
  | some a =>
    simp only [bind,ha,← he,Refines]
    exact ⟨(hf a).1,Nat.add_le_add hle (hf a).2⟩

theorem map_refines (f : A → B) (r s : Run A) (h : Refines r s) :
    Refines (map f r) (map f s) := by
  exact ⟨congrArg (Option.map f) h.1,h.2⟩

theorem bind_some_iff (r : Run A) (f : A → Run B) (b : B) :
    (bind r f).answer=some b ↔ ∃ a, r.answer=some a ∧ (f a).answer=some b := by
  cases he : r.answer <;> simp [bind,he]

/-- Ordered backtracking retains the first successful result and charges failed attempts. -/
def first (f : A → Run B) : List A → Run B
  | [] => fail
  | a::as =>
      let r := f a
      match r.answer with
      | some b => ⟨some b,r.reads,r.checks⟩
      | none => let s := first f as; ⟨s.answer,r.reads+s.reads,r.checks+s.checks⟩

theorem first_refines (f g : A → Run B) (h : ∀ a, Refines (f a) (g a)) (xs : List A) :
    Refines (first f xs) (first g xs) := by
  induction xs with
  | nil => exact refines_refl _
  | cons a xs ih =>
    have he := (h a).1
    cases ha : (f a).answer with
    | none =>
      simp only [first,ha,← he,Refines]
      exact ⟨ih.1,Nat.add_le_add (h a).2 ih.2⟩
    | some b =>
      simp only [first,ha,← he,Refines]
      exact ⟨trivial,(h a).2⟩

theorem first_some_mem (f : A → Run B) (xs : List A) (b : B)
    (hs : (first f xs).answer=some b) : ∃ a ∈ xs, (f a).answer=some b := by
  induction xs with
  | nil => cases hs
  | cons a xs ih =>
    cases he : (f a).answer with
    | none =>
      have ht : (first f xs).answer=some b := by simpa only [first,he] using hs
      obtain ⟨c,hc,hv⟩ := ih ht
      exact ⟨c,List.mem_cons_of_mem a hc,hv⟩
    | some c =>
      have hc : c=b := Option.some.inj (by simpa only [first,he] using hs)
      exact ⟨a,List.mem_cons_self,by simpa only [hc] using he⟩

theorem first_none_iff (f : A → Run B) (xs : List A) :
    (first f xs).answer=none ↔ ∀ a ∈ xs, (f a).answer=none := by
  induction xs with
  | nil => simp [first,fail]
  | cons a xs ih =>
    cases he : (f a).answer with
    | none => simp [first,he,ih]
    | some b => simp [first,he]

end Run

abbrev Scanner (X : Type) := (X → Bool) → ℕ → List X → PrefixScan.Result X

def fullScanner : Scanner X := fun f C xs => PrefixScan.full f C 0 0 xs
def streamScanner : Scanner X := fun f C xs => PrefixScan.stream f C 0 0 xs

def scanRun (scan : Scanner X) (f : X → Bool) (C : ℕ) (xs : List X) : Run (List X × List X) :=
  let r := scan f C xs
  ⟨r.branches,r.reads,r.checks⟩

theorem scan_refines (f : X → Bool) (C : ℕ) (xs : List X) :
    Run.Refines (scanRun streamScanner f C xs) (scanRun fullScanner f C xs) :=
  ⟨PrefixScan.stream_branches f C 0 0 xs,PrefixScan.stream_reads_le f C 0 0 xs⟩

def stop : (h : ℕ) → C → Tree E Bool C h
  | 0,c => c
  | _+1,c => .inl c

/-- `some none` is an impossible branch; outer `none` means live-branch failure. -/
def child (next : List X → Run A) (xs : List X) : Run (Option A) :=
  if xs.isEmpty then Run.pure none else (next xs).map some

def assemble (h : ℕ) (e : E) (next : List X → Run (Tree E Bool C h))
    (p : List X × List X) : Run (Tree E Bool C (h+1)) :=
  (child next p.1).bind fun l => (child next p.2).bind fun r =>
    Run.pure (.inr (e,fun o => if o then r else l))

def attempt (scan : Scanner X) (M : Model X E Bool C Unit) (h : ℕ)
    (next : List X → Run (Tree E Bool C h)) (xs : List X) (e : E) : Run (Tree E Bool C (h+1)) :=
  if xs.all (M.permitted e) then
    (scanRun scan (M.observe e) (2^h) xs).bind (assemble h e next)
  else Run.fail

/-- The primitive program, not a relation assuming its returned tree is correct. -/
def search (scan : Scanner X) (M : Model X E Bool C Unit) (experiments : List E)
    (repairs : List C) : (h : ℕ) → List X → Run (Tree E Bool C h)
  | 0,xs =>
      if xs.isEmpty then Run.fail else
        match repairs.find? (fun c => xs.all (fun x => M.accept x c)) with
        | some c => Run.pure c
        | none => Run.fail
  | h+1,xs =>
      if xs.isEmpty then Run.fail else
        match repairs.find? (fun c => xs.all (fun x => M.accept x c)) with
        | some c => Run.pure (.inl c)
        | none => Run.first (attempt scan M h (search scan M experiments repairs h) xs) experiments

theorem child_refines (f g : List X → Run A) (h : ∀ xs, Run.Refines (f xs) (g xs)) (xs : List X) :
    Run.Refines (child f xs) (child g xs) := by
  by_cases he : xs.isEmpty
  · simp only [child,he,ite_true]; exact Run.refines_refl _
  · simp only [child,he]; exact Run.map_refines _ _ _ (h xs)

theorem assemble_refines (h : ℕ) (e : E) (f g : List X → Run (Tree E Bool C h))
    (hf : ∀ xs, Run.Refines (f xs) (g xs)) (p : List X × List X) :
    Run.Refines (assemble h e f p) (assemble h e g p) := by
  apply Run.bind_refines _ _ _ _ (child_refines f g hf p.1)
  intro l
  apply Run.bind_refines _ _ _ _ (child_refines f g hf p.2)
  intro r
  exact Run.refines_refl _

/-- Equality includes the literal ordered tree, with no relabeling of equal optima. -/
theorem streaming_preserves_search (M : Model X E Bool C Unit) (experiments : List E)
    (repairs : List C) (h : ℕ) (xs : List X) :
    Run.Refines (search streamScanner M experiments repairs h xs)
      (search fullScanner M experiments repairs h xs) := by
  induction h generalizing xs with
  | zero => exact Run.refines_refl _
  | succ h ih =>
    by_cases he : xs.isEmpty
    · simp only [search,he,ite_true]; exact Run.refines_refl _
    · simp only [search,he]
      cases hr : repairs.find? (fun c => xs.all (fun x => M.accept x c)) with
      | some c => exact Run.refines_refl _
      | none =>
        apply Run.first_refines
        intro e
        by_cases hp : xs.all (M.permitted e)
        · simp only [attempt,hp,ite_true]
          exact Run.bind_refines _ _ _ _ (scan_refines _ _ _)
            (assemble_refines h e _ _ ih)
        · simp only [attempt,hp]; exact Run.refines_refl _

/-- Backtracking and finite-depth failure are identical, including arbitrary changed row orders. -/
theorem same_returned_tree (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) :
    (search streamScanner M es cs h xs).answer = (search fullScanner M es cs h xs).answer :=
  (streaming_preserves_search M es cs h xs).1

theorem no_more_report_reads (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) :
    (search streamScanner M es cs h xs).reads ≤ (search fullScanner M es cs h xs).reads :=
  (streaming_preserves_search M es cs h xs).2

/-- The same fallback is invoked on the same completed failure, never on a timeout. -/
def withFallback (r : Run A) (fallback : Run A) : Run A :=
  match r.answer with
  | some _ => r
  | none => ⟨fallback.answer,r.reads+fallback.reads,r.checks+fallback.checks⟩

theorem same_fallback (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (fallback : Run (Tree E Bool C h)) :
    (withFallback (search streamScanner M es cs h xs) fallback).answer =
      (withFallback (search fullScanner M es cs h xs) fallback).answer := by
  have he := same_returned_tree M es cs h xs
  cases hr : (search fullScanner M es cs h xs).answer <;> simp [withFallback,he,hr]

end Komorebi.MachineTheory.OrderedCompiler
