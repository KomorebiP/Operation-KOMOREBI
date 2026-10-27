import KomorebiPadic.BudgetedPartitionInvariant

/-!
# Canonical completion, exact visit counts, and certified public results

Completed queue output is literally Block15's complete depth-first partition.
The exact visit total is 2*leaf-count-1; every partial run spends its quota or
stops at that total. Proof-only references to the complete partition do not
force a full traversal when evaluating the bounded executable.
-/
namespace KomorebiPadic

/-- Refinement is the identity on an already sealed list. -/
theorem refinePlateauLeaves_eq_self_of_sealed (p extra : ℕ) (ls : List PlateauLeaf)
    (hs : ∀ l ∈ ls, l.label.isSome = true) : refinePlateauLeaves p extra ls = ls := by
  induction ls with
  | nil => rfl
  | cons l ls ih =>
    have hl := hs l (by simp)
    have ht : ∀ k ∈ ls, k.label.isSome = true := fun k hk => hs k (by simp [hk])
    have hi := ih ht
    simpa only [refinePlateauLeaves, List.flatMap_cons, hl, ↓reduceIte,
      List.singleton_append] using congrArg (List.cons l) hi

/-- Once sufficient depth is supplied, more depth changes nothing. -/
theorem adaptiveDecompose_stable_after_completion (p fuel extra : ℕ)
    {b : ParameterBox} (hb : b.Valid) (hf : b.span < fuel) :
    adaptiveDecompose p (fuel + extra) b = adaptiveDecompose p fuel b := by
  rw [← refinePlateauLeaves_adaptiveDecompose]
  exact refinePlateauLeaves_eq_self_of_sealed p extra _
    (fun _ hl => adaptiveDecompose_complete p fuel hb hf hl)

theorem adaptiveDecompose_eq_complete_of_enough_depth (p fuel : ℕ)
    {b : ParameterBox} (hb : b.Valid) (hf : b.span < fuel) :
    adaptiveDecompose p fuel b = completeDecompose p b := by
  calc
    adaptiveDecompose p fuel b = adaptiveDecompose p (fuel + (b.span + 1)) b :=
      (adaptiveDecompose_stable_after_completion p fuel (b.span + 1) hb hf).symm
    _ = adaptiveDecompose p ((b.span + 1) + fuel) b := by rw [Nat.add_comm fuel]
    _ = completeDecompose p b :=
      adaptiveDecompose_stable_after_completion p (b.span + 1) fuel hb (by omega)

/-- The complete inherited procedure unfolds to the same seal-or-split rule. -/
theorem completeDecompose_equation (p : ℕ) {b : ParameterBox} (hb : b.Valid) :
    completeDecompose p b =
      if rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi then
        [sealedPlateauLeaf p b]
      else completeDecompose p b.split.1 ++ completeDecompose p b.split.2 := by
  change adaptiveDecompose p (b.span + 1) b = _
  rw [adaptiveDecompose]
  split
  · rfl
  · rename_i hc
    have hv := parameterBox_split_valid_and_decreases hb
      (parameterBox_span_pos_of_failed_check p hb hc)
    rw [adaptiveDecompose_eq_complete_of_enough_depth p b.span hv.1 hv.2.2.1,
      adaptiveDecompose_eq_complete_of_enough_depth p b.span hv.2.1 hv.2.2.2]

/-- Mathematical full expansion of a checkpoint; not executed by the budgeted runner. -/
def rectangleQueueExpansion (p : ℕ) (s : RectangleQueueState) : List PlateauLeaf :=
  s.sealed ++ s.pending.flatMap (completeDecompose p)

/-- A single step preserves the complete ordered future partition. -/
theorem rectangleQueueStep_expansion (p : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) :
    rectangleQueueExpansion p (rectangleQueueStep p s) = rectangleQueueExpansion p s := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => rfl
  | cons b bs =>
    have hb := hv b (by simp)
    have he := completeDecompose_equation p hb
    by_cases hc : rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi = true
    · simp only [hc, ↓reduceIte] at he
      simp [rectangleQueueStep, hc, rectangleQueueExpansion, he, List.append_assoc]
    · simp only [hc] at he
      simp [rectangleQueueStep, hc, rectangleQueueExpansion, he, List.append_assoc]

theorem runRectangleQueue_expansion (p n : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) :
    rectangleQueueExpansion p (runRectangleQueue p n s) = rectangleQueueExpansion p s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    by_cases he : s.pending = []
    · rw [runRectangleQueue_empty p _ he]
    · simp only [runRectangleQueue, he, ↓reduceIte]
      exact (ih (rectangleQueueStep_pending_valid p hv)).trans (rectangleQueueStep_expansion p hv)

/-- Every authentic checkpoint has the same complete future partition as Block15. -/
theorem budgetedDecompose_expansion (p n : ℕ) {b : ParameterBox} (hb : b.Valid) :
    rectangleQueueExpansion p (budgetedDecompose p n b) = completeDecompose p b := by
  have hv : (initialRectangleQueue b).PendingValid := by
    intro c hc
    simp only [initialRectangleQueue, List.mem_singleton] at hc
    subst c
    exact hb
  simpa [budgetedDecompose, rectangleQueueExpansion, initialRectangleQueue] using
    runRectangleQueue_expansion p n hv

/-- Completed outputs agree literally, including leaf order and labels. -/
theorem budgetedDecompose_completed_eq_complete (p n : ℕ) {b : ParameterBox}
    (hb : b.Valid) (he : (budgetedDecompose p n b).pending = []) :
    (budgetedDecompose p n b).leaves = completeDecompose p b := by
  have hh := budgetedDecompose_expansion p n hb
  simpa [rectangleQueueExpansion, RectangleQueueState.leaves, he] using hh

/-- A sufficient budget for all visits, not merely for maximum recursion depth. -/
theorem budgetedDecompose_pending_empty_of_capacity_le (p n : ℕ) {b : ParameterBox}
    (hb : b.Valid) (hn : b.nodeCapacity ≤ n) : (budgetedDecompose p n b).pending = [] := by
  apply runRectangleQueue_complete p n
  · intro c hc
    simp only [initialRectangleQueue, List.mem_singleton] at hc
    subst c
    exact hb
  · simpa [initialRectangleQueue, pendingNodeCapacity] using hn

/-- Exact total real visits of the completed depth-first traversal. -/
def completePartitionVisitCount (p : ℕ) (b : ParameterBox) : ℕ :=
  2 * (completeDecompose p b).length - 1

theorem budgetedDecompose_completed_visited (p n : ℕ) {b : ParameterBox}
    (hb : b.Valid) (he : (budgetedDecompose p n b).pending = []) :
    (budgetedDecompose p n b).visited = completePartitionVisitCount p b := by
  rw [budgetedDecompose_complete_node_count p n b he,
    budgetedDecompose_completed_eq_complete p n hb he]
  rfl

/-- Any partial visit counter is bounded by the exact completed visit count. -/
theorem budgetedDecompose_visited_le_total (p n : ℕ) {b : ParameterBox} (hb : b.Valid) :
    (budgetedDecompose p n b).visited ≤ completePartitionVisitCount p b := by
  have hv := (runRectangleQueue_visited_bounds p b.nodeCapacity (budgetedDecompose p n b)).1
  change (budgetedDecompose p n b).visited ≤
    (runRectangleQueue p b.nodeCapacity (runRectangleQueue p n (initialRectangleQueue b))).visited at hv
  rw [runRectangleQueue_add] at hv
  have hd := budgetedDecompose_pending_empty_of_capacity_le p (n + b.nodeCapacity) hb (by omega)
  exact hv.trans_eq (budgetedDecompose_completed_visited p (n + b.nodeCapacity) hb hd)

/-- The exact budget semantics: visits = min(requested quota, actual total). -/
theorem budgetedDecompose_visited_eq_min (p n : ℕ) {b : ParameterBox} (hb : b.Valid) :
    (budgetedDecompose p n b).visited = min n (completePartitionVisitCount p b) := by
  by_cases he : (budgetedDecompose p n b).pending = []
  · have hx := budgetedDecompose_completed_visited p n hb he
    have hle := budgetedDecompose_visited_le p n b
    rw [hx] at hle ⊢
    exact (Nat.min_eq_right hle).symm
  · have hx := runRectangleQueue_exhausted p n (initialRectangleQueue b) he
    change (budgetedDecompose p n b).visited = 0 + n at hx
    have hle := budgetedDecompose_visited_le_total p n hb
    simp only [Nat.zero_add] at hx
    rw [hx] at hle ⊢
    exact (Nat.min_eq_left hle).symm

/-- A completed checkpoint is equivalent to having supplied the exact total visits. -/
theorem budgetedDecompose_complete_iff (p n : ℕ) {b : ParameterBox} (hb : b.Valid) :
    (budgetedDecompose p n b).pending = [] ↔ completePartitionVisitCount p b ≤ n := by
  constructor
  · intro he
    rw [← budgetedDecompose_completed_visited p n hb he]
    exact budgetedDecompose_visited_le p n b
  · intro htotal
    by_contra hn
    have hx := runRectangleQueue_exhausted p n (initialRectangleQueue b) hn
    change (budgetedDecompose p n b).visited = 0 + n at hx
    have hs : runRectangleQueue p 1 (budgetedDecompose p n b) =
        rectangleQueueStep p (budgetedDecompose p n b) := by
      simp [runRectangleQueue, hn]
    have hadd : runRectangleQueue p 1 (budgetedDecompose p n b) =
        budgetedDecompose p (n + 1) b := runRectangleQueue_add p n 1 (initialRectangleQueue b)
    have hle := budgetedDecompose_visited_le_total p (n + 1) hb
    rw [← hadd, hs, rectangleQueueStep_visited p hn] at hle
    omega

/-- The exact total itself is bounded by 2*area-1. -/
theorem completePartitionVisitCount_le_capacity (p : ℕ) {b : ParameterBox}
    (hb : b.Valid) : completePartitionVisitCount p b ≤ b.nodeCapacity := by
  have he := completeBudgetedDecompose_pending_empty p hb
  rw [← budgetedDecompose_completed_visited p b.nodeCapacity hb he]
  exact budgetedDecompose_visited_le p b.nodeCapacity b

/-- Public domain validation is separate from pending/unresolved status. -/
def checkedBudgetedDecompose (p budget : ℕ) (b : ParameterBox) : Option RectangleQueueState :=
  if p.Prime ∧ b.Valid then some (budgetedDecompose p budget b) else none

theorem checkedBudgetedDecompose_eq_some_iff (p n : ℕ) (b : ParameterBox)
    (s : RectangleQueueState) :
    checkedBudgetedDecompose p n b = some s ↔
      p.Prime ∧ b.Valid ∧ s = budgetedDecompose p n b := by
  simp only [checkedBudgetedDecompose]
  split <;> simp_all [eq_comm]

/-- Proof fields mention complete output only propositionally; bounded evaluation
executes only the bounded queue and does not evaluate its future expansion. -/
structure BudgetedPartitionCertificate (p budget : ℕ) (b : ParameterBox) where
  base_prime : p.Prime
  box_valid : b.Valid
  result : RectangleQueueState
  result_eq : result = budgetedDecompose p budget b
  invariant : RectangleQueueInvariant p b result
  disjoint : result.leaves.Pairwise
    (fun x y => ∀ r h, ¬ (x.box.Contains r h ∧ y.box.Contains r h))
  visit_limit : result.visited ≤ budget
  exact_visits : result.visited = min budget (completePartitionVisitCount p b)
  node_identity : result.visited + 1 = 2 * result.sealed.length + result.pending.length
  completion_iff : result.pending = [] ↔ completePartitionVisitCount p b ≤ budget
  sufficient_budget : b.nodeCapacity ≤ budget → result.pending = []
  completed_output : result.pending = [] → result.leaves = completeDecompose p b
  exact_restart : ∀ extra, runRectangleQueue p extra result = budgetedDecompose p (budget + extra) b
  retain_sealed : ∀ extra, ∃ tail, (runRectangleQueue p extra result).sealed = result.sealed ++ tail
  uniform_envelope : ∀ l ∈ result.leaves, ∀ r h, l.box.Contains r h →
    maximumLayerCompilerTotalTests p r h ≤ maximumLayerCompilerParameterEnvelopeBound p b.rhi b.hlo

def budgetedPartitionCertificate (p budget : ℕ) (b : ParameterBox)
    (hp : p.Prime) (hb : b.Valid) : BudgetedPartitionCertificate p budget b where
  base_prime := hp
  box_valid := hb
  result := budgetedDecompose p budget b
  result_eq := rfl
  invariant := budgetedDecompose_invariant hp budget hb
  disjoint := budgetedDecompose_pairwise_disjoint hp budget hb
  visit_limit := budgetedDecompose_visited_le p budget b
  exact_visits := budgetedDecompose_visited_eq_min p budget hb
  node_identity := budgetedDecompose_node_identity p budget b
  completion_iff := budgetedDecompose_complete_iff p budget hb
  sufficient_budget := budgetedDecompose_pending_empty_of_capacity_le p budget hb
  completed_output := budgetedDecompose_completed_eq_complete p budget hb
  exact_restart := fun extra => runRectangleQueue_add p budget extra (initialRectangleQueue b)
  retain_sealed := fun extra => runRectangleQueue_sealed_prefix p extra _
  uniform_envelope := fun _ hl _ _ hx => budgetedDecompose_uniform_envelope hp hb hl hx

theorem checkedBudgetedDecompose_has_certificate (p budget : ℕ) (b : ParameterBox)
    (s : RectangleQueueState) (hc : checkedBudgetedDecompose p budget b = some s) :
    ∃ c : BudgetedPartitionCertificate p budget b, c.result = s := by
  obtain ⟨hp, hb, rfl⟩ := (checkedBudgetedDecompose_eq_some_iff p budget b s).mp hc
  exact ⟨budgetedPartitionCertificate p budget b hp hb, rfl⟩

end KomorebiPadic
