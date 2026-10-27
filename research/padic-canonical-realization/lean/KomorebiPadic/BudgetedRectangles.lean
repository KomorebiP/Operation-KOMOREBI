import KomorebiPadic.QueueBudgetGeometry

/-!
# A globally budgeted, restartable depth-first work queue

A visit processes exactly one pending rectangle. An empty queue stops immediately.
Sealed leaves are never sent back through the corner compiler. The budget counts
visited rectangles, not internal arithmetic, memory traffic, or wall time.
-/
namespace KomorebiPadic

structure RectangleQueueState where
  pending : List ParameterBox
  sealed : List PlateauLeaf
  visited : ℕ
  deriving DecidableEq, Repr

def initialRectangleQueue (b : ParameterBox) : RectangleQueueState := ⟨[b], [], 0⟩

/-- Chronological sealed leaves followed by every pending box as unresolved. -/
def RectangleQueueState.leaves (s : RectangleQueueState) : List PlateauLeaf :=
  s.sealed ++ s.pending.map unresolvedPlateauLeaf

def RectangleQueueState.PendingValid (s : RectangleQueueState) : Prop :=
  ∀ b ∈ s.pending, b.Valid

/-- One real visit; the empty queue is an absorbing state. -/
def rectangleQueueStep (p : ℕ) (s : RectangleQueueState) : RectangleQueueState :=
  match s.pending with
  | [] => s
  | b :: bs =>
    if rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi then
      ⟨bs, s.sealed ++ [sealedPlateauLeaf p b], s.visited + 1⟩
    else
      ⟨b.split.1 :: b.split.2 :: bs, s.sealed, s.visited + 1⟩

/-- Fuel is a global visit quota. Exhaustion returns the entire live state. -/
def runRectangleQueue (p : ℕ) : ℕ → RectangleQueueState → RectangleQueueState
  | 0, s => s
  | n + 1, s =>
    if s.pending = [] then s else runRectangleQueue p n (rectangleQueueStep p s)

def budgetedDecompose (p budget : ℕ) (b : ParameterBox) : RectangleQueueState :=
  runRectangleQueue p budget (initialRectangleQueue b)

/-- No pending node is visited, and no compiler call occurs, at budget zero. -/
theorem budgetedDecompose_zero (p : ℕ) (b : ParameterBox) :
    budgetedDecompose p 0 b = initialRectangleQueue b := rfl

theorem rectangleQueueStep_empty (p : ℕ) {s : RectangleQueueState}
    (he : s.pending = []) : rectangleQueueStep p s = s := by
  simp [rectangleQueueStep, he]

theorem runRectangleQueue_empty (p n : ℕ) {s : RectangleQueueState}
    (he : s.pending = []) : runRectangleQueue p n s = s := by
  cases n <;> simp [runRectangleQueue, he]

/-- Exact restart equality includes queue order, sealed labels, and visit counters. -/
theorem runRectangleQueue_add (p n extra : ℕ) (s : RectangleQueueState) :
    runRectangleQueue p extra (runRectangleQueue p n s) =
      runRectangleQueue p (n + extra) s := by
  induction n generalizing s with
  | zero => simp [runRectangleQueue]
  | succ n ih =>
    by_cases he : s.pending = []
    · simp [runRectangleQueue_empty p _ he]
    · rw [Nat.succ_add]
      simp only [runRectangleQueue, he, ↓reduceIte]
      exact ih (rectangleQueueStep p s)

/-- Each nonempty step increments the actual visit counter by exactly one. -/
theorem rectangleQueueStep_visited (p : ℕ) {s : RectangleQueueState}
    (hn : s.pending ≠ []) : (rectangleQueueStep p s).visited = s.visited + 1 := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => exact (hn rfl).elim
  | cons b bs => simp only [rectangleQueueStep]; split <;> rfl

/-- A run spends no more than its requested additional global budget. -/
theorem runRectangleQueue_visited_bounds (p n : ℕ) (s : RectangleQueueState) :
    s.visited ≤ (runRectangleQueue p n s).visited ∧
      (runRectangleQueue p n s).visited ≤ s.visited + n := by
  induction n generalizing s with
  | zero => simp [runRectangleQueue]
  | succ n ih =>
    by_cases he : s.pending = []
    · simp [runRectangleQueue_empty p _ he]
    · simp only [runRectangleQueue, he, ↓reduceIte]
      have hv := rectangleQueueStep_visited p he
      have hi := ih (rectangleQueueStep p s)
      omega

/-- If work remains, every supplied visit unit was actually spent. -/
theorem runRectangleQueue_exhausted (p n : ℕ) (s : RectangleQueueState)
    (hn : (runRectangleQueue p n s).pending ≠ []) :
    (runRectangleQueue p n s).visited = s.visited + n := by
  induction n generalizing s with
  | zero => simp [runRectangleQueue]
  | succ n ih =>
    by_cases he : s.pending = []
    · rw [runRectangleQueue_empty p _ he] at hn
      exact (hn he).elim
    · simp only [runRectangleQueue, he, ↓reduceIte] at hn ⊢
      rw [ih (rectangleQueueStep p s) hn, rectangleQueueStep_visited p he]
      omega

/-- Previously sealed records remain a literal prefix after any further run. -/
theorem runRectangleQueue_sealed_prefix (p n : ℕ) (s : RectangleQueueState) :
    ∃ tail, (runRectangleQueue p n s).sealed = s.sealed ++ tail := by
  induction n generalizing s with
  | zero => exact ⟨[], (List.append_nil _).symm⟩
  | succ n ih =>
    by_cases he : s.pending = []
    · rw [runRectangleQueue_empty p _ he]
      exact ⟨[], (List.append_nil _).symm⟩
    · simp only [runRectangleQueue, he, ↓reduceIte]
      obtain ⟨tail, ht⟩ := ih (rectangleQueueStep p s)
      rcases s with ⟨ps, ls, v⟩
      cases ps with
      | nil => exact (he rfl).elim
      | cons b bs =>
        simp only [rectangleQueueStep] at ht ⊢
        split at ht
        · rename_i hc
          simp only [hc, ↓reduceIte]
          exact ⟨[sealedPlateauLeaf p b] ++ tail, ht.trans (List.append_assoc _ _ _)⟩
        · rename_i hc
          simp only [hc]
          exact ⟨tail, ht⟩

/-- All pending geometry remains valid after one step. -/
theorem rectangleQueueStep_pending_valid (p : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) : (rectangleQueueStep p s).PendingValid := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => exact hv
  | cons b bs =>
    have hb := hv b (by simp)
    have hbs : ∀ c ∈ bs, c.Valid := fun c hc => hv c (by simp [hc])
    simp only [rectangleQueueStep]
    split
    · exact hbs
    · rename_i hc
      have hh := parameterBox_split_valid_and_decreases hb
        (parameterBox_span_pos_of_failed_check p hb hc)
      intro c hm
      simp only [List.mem_cons] at hm
      rcases hm with rfl | rfl | hm
      · exact hh.1
      · exact hh.2.1
      · exact hbs c hm

theorem runRectangleQueue_pending_valid (p n : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) : (runRectangleQueue p n s).PendingValid := by
  induction n generalizing s with
  | zero => exact hv
  | succ n ih =>
    by_cases he : s.pending = []
    · simpa [runRectangleQueue_empty p _ he] using hv
    · simp only [runRectangleQueue, he, ↓reduceIte]
      exact ih (rectangleQueueStep_pending_valid p hv)

/-- A visit removes at least one unit of remaining capacity. -/
theorem rectangleQueueStep_capacity (p : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) (hn : s.pending ≠ []) :
    pendingNodeCapacity (rectangleQueueStep p s).pending + 1 ≤
      pendingNodeCapacity s.pending := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => exact (hn rfl).elim
  | cons b bs =>
    have hb := hv b (by simp)
    simp only [rectangleQueueStep]
    split
    · have hbpos := parameterBox_nodeCapacity_pos b
      simp only [pendingNodeCapacity]
      omega
    · rename_i hc
      have hcapa := parameterBox_split_nodeCapacity hb
        (parameterBox_span_pos_of_failed_check p hb hc)
      simp only [pendingNodeCapacity]
      omega

/-- Visits already spent plus the future capacity never increase. -/
theorem runRectangleQueue_capacity_accounting (p n : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) :
    (runRectangleQueue p n s).visited + pendingNodeCapacity (runRectangleQueue p n s).pending ≤
      s.visited + pendingNodeCapacity s.pending := by
  induction n generalizing s with
  | zero => exact le_rfl
  | succ n ih =>
    by_cases he : s.pending = []
    · simp [runRectangleQueue_empty p _ he]
    · simp only [runRectangleQueue, he, ↓reduceIte]
      have hi := ih (rectangleQueueStep_pending_valid p hv)
      have hc := rectangleQueueStep_capacity p hv he
      have hx := rectangleQueueStep_visited p he
      omega

/-- A global quota at least the remaining capacity guarantees completion. -/
theorem runRectangleQueue_complete (p n : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) (hn : pendingNodeCapacity s.pending ≤ n) :
    (runRectangleQueue p n s).pending = [] := by
  induction n generalizing s with
  | zero =>
    change s.pending = []
    exact (pendingNodeCapacity_eq_zero_iff _).mp (by omega)
  | succ n ih =>
    by_cases he : s.pending = []
    · simpa [runRectangleQueue_empty p _ he] using he
    · simp only [runRectangleQueue, he, ↓reduceIte]
      have hc := rectangleQueueStep_capacity p hv he
      exact ih (rectangleQueueStep_pending_valid p hv) (by omega)

/-- The full-binary-tree accounting law is preserved at every real or idle step. -/
theorem rectangleQueueStep_node_identity (p : ℕ) (s : RectangleQueueState)
    (hi : s.visited + 1 = 2 * s.sealed.length + s.pending.length) :
    (rectangleQueueStep p s).visited + 1 =
      2 * (rectangleQueueStep p s).sealed.length + (rectangleQueueStep p s).pending.length := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => exact hi
  | cons b bs =>
    simp only [rectangleQueueStep]
    split <;> simp only [List.length_append, List.length_cons, List.length_nil] at * <;> omega

theorem runRectangleQueue_node_identity (p n : ℕ) (s : RectangleQueueState)
    (hi : s.visited + 1 = 2 * s.sealed.length + s.pending.length) :
    (runRectangleQueue p n s).visited + 1 =
      2 * (runRectangleQueue p n s).sealed.length + (runRectangleQueue p n s).pending.length := by
  induction n generalizing s with
  | zero => exact hi
  | succ n ih =>
    by_cases he : s.pending = []
    · simpa [runRectangleQueue_empty p _ he] using hi
    · simp only [runRectangleQueue, he, ↓reduceIte]
      exact ih _ (rectangleQueueStep_node_identity p s hi)

theorem budgetedDecompose_visited_le (p n : ℕ) (b : ParameterBox) :
    (budgetedDecompose p n b).visited ≤ n := by
  simpa [budgetedDecompose, initialRectangleQueue] using
    (runRectangleQueue_visited_bounds p n (initialRectangleQueue b)).2

theorem budgetedDecompose_node_identity (p n : ℕ) (b : ParameterBox) :
    (budgetedDecompose p n b).visited + 1 =
      2 * (budgetedDecompose p n b).sealed.length + (budgetedDecompose p n b).pending.length := by
  exact runRectangleQueue_node_identity p n (initialRectangleQueue b) (by simp [initialRectangleQueue])

/-- The worst-case full traversal visits at most 2*area-1 nodes. -/
theorem budgetedDecompose_visited_le_capacity (p n : ℕ) {b : ParameterBox}
    (hb : b.Valid) : (budgetedDecompose p n b).visited ≤ b.nodeCapacity := by
  have hv : (initialRectangleQueue b).PendingValid := by
    intro c hc
    simp only [initialRectangleQueue, List.mem_singleton] at hc
    subst c
    exact hb
  have hi := runRectangleQueue_capacity_accounting p n hv
  simp only [initialRectangleQueue, pendingNodeCapacity, Nat.add_zero, Nat.zero_add] at hi
  exact (Nat.le_add_right _ _).trans hi

/-- Completion is an executable empty-queue test, not a budget-exhaustion test. -/
def rectangleQueueComplete (s : RectangleQueueState) : Bool := s.pending.isEmpty

def completeBudgetedDecompose (p : ℕ) (b : ParameterBox) : RectangleQueueState :=
  budgetedDecompose p b.nodeCapacity b

theorem completeBudgetedDecompose_pending_empty (p : ℕ) {b : ParameterBox}
    (hb : b.Valid) : (completeBudgetedDecompose p b).pending = [] := by
  apply runRectangleQueue_complete p b.nodeCapacity
  · intro c hc
    simp only [initialRectangleQueue, List.mem_singleton] at hc
    subst c
    exact hb
  · simp [initialRectangleQueue, pendingNodeCapacity]

end KomorebiPadic
