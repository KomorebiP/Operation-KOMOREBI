import RealizationBoundaries.RootAlgorithm

/-!
# Oracle traces for the executable finite root solver

Every oracle read appends its prime to a finite trace. Erasing the traces gives
the original finite arithmetic routines. The bounds count oracle requests and
loop candidates, and do not assign unit bit-cost to rational arithmetic,
primality testing, integer division or modular inversion.
-/
set_option autoImplicit false
namespace RealizationBoundaries

/-- One explicit oracle operation, recording its queried coordinate. -/
def tracedSelectorRead (a : Prime → Bool) (p : Prime) : Bool × List Prime :=
  (a p, [p])

def tracedOracleSection (a : Prime → Bool) (r : ℚ) (p : Prime) :
    Coordinate p × List Prime :=
  let q := tracedSelectorRead a p
  (if q.1 then (r : Coordinate p) else 0, q.2)

@[simp] theorem tracedOracleSection_erase (a : Prime → Bool) (r : ℚ) (p : Prime) :
    (tracedOracleSection a r p).1 = oracleSection a r p := rfl

@[simp] theorem tracedOracleSection_trace (a : Prime → Bool) (r : ℚ) (p : Prime) :
    (tracedOracleSection a r p).2 = [p] := rfl

/-- The two section evaluations in the original correction, with their actual reads. -/
def tracedRootCorrectionValue (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m : ℕ) (p : Prime) : Coordinate p × List Prime :=
  let sr := tracedOracleSection a r p
  let st := tracedOracleSection a (r / m) p
  ((m : Coordinate p)⁻¹ * (sr.1 + finiteCodeValue d p - (m : Coordinate p) * st.1),
    sr.2 ++ st.2)

@[simp] theorem tracedRootCorrectionValue_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) (p : Prime) :
    (tracedRootCorrectionValue a r d m p).1 = rootCorrectionValue a r d m p := rfl

@[simp] theorem tracedRootCorrectionValue_trace (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) (p : Prime) :
    (tracedRootCorrectionValue a r d m p).2 = [p, p] := rfl

/-- Single-pass sequencing: preserve each computed value and concatenate its trace. -/
def sequenceRootTrace {α : Type*} : List (α × List Prime) → List α × List Prime
  | [] => ([], [])
  | (x, t) :: xs =>
    let tail := sequenceRootTrace xs
    (x :: tail.1, t ++ tail.2)

@[simp] theorem sequenceRootTrace_erase {α : Type*} (xs : List (α × List Prime)) :
    (sequenceRootTrace xs).1 = xs.map Prod.fst := by
  induction xs with
  | nil => rfl
  | cons x xs ih => cases x; simp [sequenceRootTrace, ih]

theorem sequenceRootTrace_bound {α : Type*} (xs : List (α × List Prime))
    (c : ℕ) (h : ∀ x ∈ xs, x.2.length ≤ c) :
    (sequenceRootTrace xs).2.length ≤ c * xs.length := by
  induction xs with
  | nil => simp [sequenceRootTrace]
  | cons x xs ih =>
    have hx := h x (List.mem_cons_self)
    have ht := ih (fun y hy => h y (List.mem_cons_of_mem _ hy))
    cases x with
    | mk v t =>
      simp only [sequenceRootTrace, List.length_append, List.length_cons]
      dsimp only at hx
      rw [Nat.mul_add, Nat.mul_one]
      omega

def tracedRootCorrectionStep (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m n : ℕ) : ℕ × List Prime :=
  if h : n.Prime then
    let q := tracedRootCorrectionValue a r d m ⟨n, h⟩
    (q.1.val, q.2)
  else (0, [])

def tracedRootCorrectionCode (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    List ℕ × List Prime :=
  sequenceRootTrace (List.ofFn fun i : Fin (rootCorrectionBound r d m) =>
    tracedRootCorrectionStep a r d m i.val)

theorem tracedRootCorrectionCode_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedRootCorrectionCode a r d m).1 = rootCorrectionCode a r d m := by
  simp only [tracedRootCorrectionCode, sequenceRootTrace_erase, List.map_ofFn]
  congr 1
  funext i
  simp only [Function.comp_apply, tracedRootCorrectionStep]
  split <;> rfl

theorem tracedRootCorrectionCode_query_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedRootCorrectionCode a r d m).2.length ≤ 2 * rootCorrectionBound r d m := by
  have hb := sequenceRootTrace_bound
    (List.ofFn fun i : Fin (rootCorrectionBound r d m) =>
      tracedRootCorrectionStep a r d m i.val) 2 (by
        intro x hx
        obtain ⟨i, rfl⟩ := List.mem_ofFn.mp hx
        simp only [tracedRootCorrectionStep]
        split
        · change ([_, _] : List Prime).length ≤ 2
          exact Nat.le_refl 2
        · exact Nat.zero_le 2)
  simpa only [tracedRootCorrectionCode, List.length_ofFn] using hb

/-- Search predicate evaluates the section only at prime divisors of the multiplier. -/
def tracedRootObstructs (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m n : ℕ) : Bool × List Prime :=
  if h : n.Prime then
    if n ∣ m then
      let q := tracedOracleSection a r ⟨n, h⟩
      (decide (q.1 + finiteCodeValue d ⟨n, h⟩ ≠ 0), q.2)
    else (false, [])
  else (false, [])

@[simp] theorem tracedRootObstructs_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m n : ℕ) :
    (tracedRootObstructs a r d m n).1 = rootObstructs a r d m n := by
  by_cases hp : n.Prime <;> by_cases hd : n ∣ m <;>
    simp [tracedRootObstructs, rootObstructs, hp, hd, codedNormalValue,
      tracedOracleSection, tracedSelectorRead, oracleSection]
  exact decide_not

@[simp] theorem tracedRootObstructs_query_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m n : ℕ) :
    (tracedRootObstructs a r d m n).2.length ≤ 1 := by
  by_cases hp : n.Prime <;> by_cases hd : n ∣ m <;>
    simp [tracedRootObstructs, hp, hd, tracedOracleSection, tracedSelectorRead]
  exact Nat.le_refl 1

/-- Short-circuit search: stop after the first successful predicate, retaining all reads. -/
def findRootTrace {α : Type*} (test : α → Bool × List Prime) :
    List α → Option α × List Prime
  | [] => (none, [])
  | x :: xs =>
    let q := test x
    if q.1 then (some x, q.2)
    else
      let tail := findRootTrace test xs
      (tail.1, q.2 ++ tail.2)

@[simp] theorem findRootTrace_erase {α : Type*} (test : α → Bool × List Prime)
    (xs : List α) :
    (findRootTrace test xs).1 = xs.find? (fun x => (test x).1) := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [findRootTrace, List.find?_cons]; split <;> simp_all

theorem findRootTrace_bound {α : Type*} (test : α → Bool × List Prime)
    (xs : List α) (c : ℕ) (h : ∀ x ∈ xs, (test x).2.length ≤ c) :
    (findRootTrace test xs).2.length ≤ c * xs.length := by
  induction xs with
  | nil => simp [findRootTrace]
  | cons x xs ih =>
    have hx := h x (List.mem_cons_self)
    have ht := ih (fun y hy => h y (List.mem_cons_of_mem _ hy))
    simp only [findRootTrace, List.length_cons]
    split
    · change (test x).2.length ≤ c * (xs.length + 1)
      rw [Nat.mul_add, Nat.mul_one]
      omega
    · simp only [List.length_append]
      rw [Nat.mul_add, Nat.mul_one]
      omega

def tracedFirstRootObstruction (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    Option ℕ × List Prime :=
  findRootTrace (tracedRootObstructs a r d m) (List.range (m + 1))

@[simp] theorem tracedFirstRootObstruction_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedFirstRootObstruction a r d m).1 = firstRootObstruction a r d m := by
  simp only [tracedFirstRootObstruction, findRootTrace_erase,
    tracedRootObstructs_erase, firstRootObstruction]

theorem tracedFirstRootObstruction_query_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedFirstRootObstruction a r d m).2.length ≤ m + 1 := by
  simpa only [tracedFirstRootObstruction, List.length_range, one_mul] using
    findRootTrace_bound (tracedRootObstructs a r d m) (List.range (m + 1)) 1
      (fun n _ => tracedRootObstructs_query_bound a r d m n)

def tracedCertifiedRootSolver (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    Except ℕ (ℚ × List ℕ) × List Prime :=
  let search := tracedFirstRootObstruction a r d m
  match search.1 with
  | some p => (.error p, search.2)
  | none =>
    let correction := tracedRootCorrectionCode a r d m
    (.ok (r / m, correction.1), search.2 ++ correction.2)

theorem tracedCertifiedRootSolver_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedCertifiedRootSolver a r d m).1 = certifiedRootSolver a r d m := by
  simp only [tracedCertifiedRootSolver, certifiedRootSolver,
    tracedFirstRootObstruction_erase]
  split <;> simp_all [tracedRootCorrectionCode_erase]

/-- Certified finite oracle-query bound, without any unit bit-cost claim. -/
theorem tracedCertifiedRootSolver_query_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (tracedCertifiedRootSolver a r d m).2.length ≤
      m + 1 + 2 * rootCorrectionBound r d m := by
  have hs := tracedFirstRootObstruction_query_bound a r d m
  have hc := tracedRootCorrectionCode_query_bound a r d m
  simp only [tracedCertifiedRootSolver]
  split
  · exact hs.trans (Nat.le_add_right _ _)
  · simpa only [List.length_append] using Nat.add_le_add hs hc

/-- The same short-circuit search with an explicit counter of predicate-candidate
visits, including candidates discarded without making an oracle request. -/
def countedFindRootTrace {α : Type*} (test : α → Bool × List Prime) :
    List α → (Option α × List Prime) × ℕ
  | [] => ((none, []), 0)
  | x :: xs =>
    let q := test x
    if q.1 then ((some x, q.2), 1)
    else
      let tail := countedFindRootTrace test xs
      ((tail.1.1, q.2 ++ tail.1.2), tail.2 + 1)

@[simp] theorem countedFindRootTrace_erase {α : Type*} (test : α → Bool × List Prime)
    (xs : List α) : (countedFindRootTrace test xs).1 = findRootTrace test xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    simp only [countedFindRootTrace, findRootTrace]
    split <;> simp_all

theorem countedFindRootTrace_step_bound {α : Type*} (test : α → Bool × List Prime)
    (xs : List α) : (countedFindRootTrace test xs).2 ≤ xs.length := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons x xs ih =>
    simp only [countedFindRootTrace, List.length_cons]
    split
    · change 1 ≤ xs.length + 1
      omega
    · change (countedFindRootTrace test xs).2 + 1 ≤ xs.length + 1
      omega

/-- A counted certified execution: one visit per searched integer, and on success
one correction candidate for each integer below the proved finite bound. -/
def countedCertifiedRootSolver (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    (Except ℕ (ℚ × List ℕ) × List Prime) × ℕ :=
  let search := countedFindRootTrace (tracedRootObstructs a r d m) (List.range (m + 1))
  match search.1.1 with
  | some p => ((.error p, search.1.2), search.2)
  | none =>
    let correction := tracedRootCorrectionCode a r d m
    ((.ok (r / m, correction.1), search.1.2 ++ correction.2),
      search.2 + rootCorrectionBound r d m)

theorem countedCertifiedRootSolver_erase (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (countedCertifiedRootSolver a r d m).1 = tracedCertifiedRootSolver a r d m := by
  simp only [countedCertifiedRootSolver, countedFindRootTrace_erase,
    tracedCertifiedRootSolver, tracedFirstRootObstruction]
  split <;> rfl

theorem countedCertifiedRootSolver_step_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (countedCertifiedRootSolver a r d m).2 ≤ m + 1 + rootCorrectionBound r d m := by
  have hs := countedFindRootTrace_step_bound (tracedRootObstructs a r d m)
    (List.range (m + 1))
  simp only [List.length_range] at hs
  simp only [countedCertifiedRootSolver]
  split
  · exact hs.trans (Nat.le_add_right _ _)
  · exact Nat.add_le_add_right hs _

theorem countedCertifiedRootSolver_query_bound (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (countedCertifiedRootSolver a r d m).1.2.length ≤
      m + 1 + 2 * rootCorrectionBound r d m := by
  rw [countedCertifiedRootSolver_erase]
  exact tracedCertifiedRootSolver_query_bound a r d m

/-- Semantic extraction correspondence composes the trace erasure with the
all-prime ambient correctness theorem for positive multipliers. -/
theorem tracedCertifiedRootSolver_sound (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) (t : ℚ) (e : List ℕ)
    (h : (tracedCertifiedRootSolver a r d m).1 = .ok (t, e)) :
    m • codedNormalValue a t e = codedNormalValue a r d := by
  rw [tracedCertifiedRootSolver_erase] at h
  exact certifiedRootSolver_ok a r d hm t e h

end RealizationBoundaries
