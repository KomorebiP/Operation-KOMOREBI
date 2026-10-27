import KomorebiPadic.FiniteCompiler

/-!
# Exact suffix-window branch and bound

A descending scan of costs `visible a + carry a` may stop as soon as the
current best complete cost is no larger than the visible cost at the current
index.  Antitonicity of `visible` says that every still earlier index has at
least that visible cost, while the natural-valued carry is nonnegative.
Consequently the unvisited prefix cannot improve the minimum.

The second half of this file instantiates the generic theorem with the exact
radix representatives from Block 05 and proves that the executable suffix
compiler returns `minRadixBarrierCost`.
-/

namespace KomorebiPadic

/-- A cost split into a monotone visible lower bound and a nonnegative carry. -/
def splitCost (visible carry : ℕ → ℕ) (a : ℕ) : ℕ :=
  visible a + carry a

/-- Full descending scan of indices `n-1, ..., 0`, starting from `best`. -/
def fullDescendingScanAux (cost : ℕ → ℕ) : ℕ → ℕ → ℕ
  | 0, best => best
  | n + 1, best => fullDescendingScanAux cost n (min best (cost n))

/-- Descending scan with exact visible-cost early termination. -/
def suffixWindowScanAux (visible carry : ℕ → ℕ) : ℕ → ℕ → ℕ
  | 0, best => best
  | n + 1, best =>
      if best ≤ visible n then
        best
      else
        suffixWindowScanAux visible carry n
          (min best (splitCost visible carry n))

/-- Cost plus the number of representatives whose complete costs were evaluated. -/
structure SuffixWindowResult where
  cost : ℕ
  tested : ℕ
  deriving Repr, DecidableEq

/-- Instrumented suffix scan.  A stopped index contributes only a visible-bound
comparison and is not counted as a complete representative evaluation. -/
def suffixWindowResultAux (visible carry : ℕ → ℕ) : ℕ → ℕ → ℕ → SuffixWindowResult
  | 0, best, tested => ⟨best, tested⟩
  | n + 1, best, tested =>
      if best ≤ visible n then
        ⟨best, tested⟩
      else
        suffixWindowResultAux visible carry n
          (min best (splitCost visible carry n)) (tested + 1)

/-- Instrumented suffix-window scan initialized at the final index `A`. -/
def suffixWindowResult (visible carry : ℕ → ℕ) (A : ℕ) : SuffixWindowResult :=
  suffixWindowResultAux visible carry A (splitCost visible carry A) 1

/-- The instrumented scan has the same cost projection as the cost-only scan. -/
theorem suffixWindowResultAux_cost
    (visible carry : ℕ → ℕ) (n best tested : ℕ) :
    (suffixWindowResultAux visible carry n best tested).cost =
      suffixWindowScanAux visible carry n best := by
  induction n generalizing best tested with
  | zero => rfl
  | succ n ih =>
      rw [suffixWindowResultAux, suffixWindowScanAux]
      by_cases hstop : best ≤ visible n
      · simp [hstop]
      · simp [hstop]
        exact ih (min best (splitCost visible carry n)) (tested + 1)

/-- The scan never decreases the already-counted representative total. -/
theorem suffixWindowResultAux_tested_lower
    (visible carry : ℕ → ℕ) (n best tested : ℕ) :
    tested ≤ (suffixWindowResultAux visible carry n best tested).tested := by
  induction n generalizing best tested with
  | zero => exact Nat.le_refl tested
  | succ n ih =>
      rw [suffixWindowResultAux]
      by_cases hstop : best ≤ visible n
      · simp [hstop]
      · simp [hstop]
        exact (Nat.le_succ tested).trans
          (ih (min best (splitCost visible carry n)) (tested + 1))

/-- At most one complete representative is added per remaining scan index. -/
theorem suffixWindowResultAux_tested_upper
    (visible carry : ℕ → ℕ) (n best tested : ℕ) :
    (suffixWindowResultAux visible carry n best tested).tested ≤ tested + n := by
  induction n generalizing best tested with
  | zero => simp [suffixWindowResultAux]
  | succ n ih =>
      rw [suffixWindowResultAux]
      by_cases hstop : best ≤ visible n
      · simp [hstop]
      · simp [hstop]
        have h := ih (min best (splitCost visible carry n)) (tested + 1)
        omega

/-- The initialized scan evaluates between one and all `A+1` representatives. -/
theorem suffixWindowResult_tested_bounds
    (visible carry : ℕ → ℕ) (A : ℕ) :
    1 ≤ (suffixWindowResult visible carry A).tested ∧
      (suffixWindowResult visible carry A).tested ≤ A + 1 := by
  constructor
  · exact suffixWindowResultAux_tested_lower visible carry A
      (splitCost visible carry A) 1
  · simpa [suffixWindowResult, Nat.add_comm] using
      suffixWindowResultAux_tested_upper visible carry A
        (splitCost visible carry A) 1

/-- Full scan initialized at the final index `A`. -/
def fullDescendingScan (cost : ℕ → ℕ) (A : ℕ) : ℕ :=
  fullDescendingScanAux cost A (cost A)

/-- Suffix-window scan initialized at the final index `A`. -/
def suffixWindowScan (visible carry : ℕ → ℕ) (A : ℕ) : ℕ :=
  suffixWindowScanAux visible carry A (splitCost visible carry A)

/-- If the current best is below every remaining cost, a full scan is inert. -/
theorem fullDescendingScanAux_eq_of_le
    (cost : ℕ → ℕ) {n best : ℕ}
    (h : ∀ i : ℕ, i < n → best ≤ cost i) :
    fullDescendingScanAux cost n best = best := by
  induction n generalizing best with
  | zero => rfl
  | succ n ih =>
      rw [fullDescendingScanAux]
      have hlast : best ≤ cost n := h n (Nat.lt_succ_self n)
      rw [Nat.min_eq_left hlast]
      apply ih
      intro i hi
      exact h i (Nat.lt_trans hi (Nat.lt_succ_self n))

/-- A descending minimum scan never increases its initial best. -/
theorem fullDescendingScanAux_le_best
    (cost : ℕ → ℕ) (n best : ℕ) :
    fullDescendingScanAux cost n best ≤ best := by
  induction n generalizing best with
  | zero => exact Nat.le_refl best
  | succ n ih =>
      rw [fullDescendingScanAux]
      exact (ih (min best (cost n))).trans (Nat.min_le_left _ _)

/-- The scan result is below every cost that it has scanned. -/
theorem fullDescendingScanAux_le_cost_of_lt
    (cost : ℕ → ℕ) {n best i : ℕ} (hi : i < n) :
    fullDescendingScanAux cost n best ≤ cost i := by
  induction n generalizing best with
  | zero => omega
  | succ n ih =>
      rw [fullDescendingScanAux]
      by_cases hin : i < n
      · exact ih hin
      · have hieq : i = n := by omega
        subst i
        exact (fullDescendingScanAux_le_best cost n (min best (cost n))).trans
          (Nat.min_le_right _ _)

/-- The scan result is attained either by the initial best or by a scanned index. -/
theorem fullDescendingScanAux_attained
    (cost : ℕ → ℕ) (n best : ℕ) :
    fullDescendingScanAux cost n best = best ∨
      ∃ i : ℕ, i < n ∧ fullDescendingScanAux cost n best = cost i := by
  induction n generalizing best with
  | zero => exact Or.inl rfl
  | succ n ih =>
      rw [fullDescendingScanAux]
      rcases ih (min best (cost n)) with hbest | ⟨i, hi, hcost⟩
      · by_cases hle : best ≤ cost n
        · left
          simpa [Nat.min_eq_left hle] using hbest
        · right
          refine ⟨n, Nat.lt_succ_self n, ?_⟩
          have hcostle : cost n ≤ best := by omega
          simpa [Nat.min_eq_right hcostle] using hbest
      · right
        exact ⟨i, Nat.lt_trans hi (Nat.lt_succ_self n), hcost⟩

/-- A fully initialized scan returns one of the costs in `0, ..., A`. -/
theorem fullDescendingScan_mem_image_range
    (cost : ℕ → ℕ) (A : ℕ) :
    fullDescendingScan cost A ∈ (Finset.range (A + 1)).image cost := by
  unfold fullDescendingScan
  rcases fullDescendingScanAux_attained cost A (cost A) with hA | ⟨i, hi, hcost⟩
  · apply Finset.mem_image.2
    exact ⟨A, by simp, hA.symm⟩
  · apply Finset.mem_image.2
    exact ⟨i, by simp; omega, hcost.symm⟩

/-- A fully initialized scan is below every cost in `0, ..., A`. -/
theorem fullDescendingScan_le_cost
    (cost : ℕ → ℕ) {A i : ℕ} (hi : i ≤ A) :
    fullDescendingScan cost A ≤ cost i := by
  unfold fullDescendingScan
  rcases lt_or_eq_of_le hi with hlt | heq
  · exact fullDescendingScanAux_le_cost_of_lt cost hlt
  · subst i
    exact fullDescendingScanAux_le_best cost A (cost A)

/-- The full descending scan computes the finite minimum exactly. -/
theorem fullDescendingScan_eq_minImage
    (cost : ℕ → ℕ) (A : ℕ) :
    fullDescendingScan cost A =
      ((Finset.range (A + 1)).image cost).min'
        (by
          refine ⟨cost A, ?_⟩
          exact Finset.mem_image.2 ⟨A, by simp, rfl⟩) := by
  apply Nat.le_antisymm
  · have hmem := Finset.min'_mem ((Finset.range (A + 1)).image cost)
      (by
        refine ⟨cost A, ?_⟩
        exact Finset.mem_image.2 ⟨A, by simp, rfl⟩)
    rw [Finset.mem_image] at hmem
    rcases hmem with ⟨i, hi, hvalue⟩
    rw [← hvalue]
    apply fullDescendingScan_le_cost cost
    simpa using hi
  · exact Finset.min'_le _ _ (fullDescendingScan_mem_image_range cost A)

/-- Once the current best is below the visible bound at `n`, every index
`i ≤ n` has total cost at least the current best. -/
theorem splitCost_ge_best_of_visible_stop
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible)
    {n best i : ℕ} (hstop : best ≤ visible n) (hi : i ≤ n) :
    best ≤ splitCost visible carry i := by
  have hvis : visible n ≤ visible i := hvisible hi
  unfold splitCost
  omega

/-- The visible-bound stopping test certifies that scanning the entire
remaining prefix would leave the current best unchanged. -/
theorem visibleStop_fullScan_exact
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible)
    {n best : ℕ} (hstop : best ≤ visible n) :
    fullDescendingScanAux (splitCost visible carry) (n + 1) best = best := by
  apply fullDescendingScanAux_eq_of_le
  intro i hi
  exact splitCost_ge_best_of_visible_stop visible carry hvisible hstop
    (Nat.le_of_lt_succ hi)

/-- Generic exactness theorem for visible-cost suffix pruning. -/
theorem suffixWindowScanAux_eq_fullDescendingScanAux
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible)
    (n best : ℕ) :
    suffixWindowScanAux visible carry n best =
      fullDescendingScanAux (splitCost visible carry) n best := by
  induction n generalizing best with
  | zero => rfl
  | succ n ih =>
      rw [suffixWindowScanAux]
      by_cases hstop : best ≤ visible n
      · simp only [hstop]
        have hremaining : ∀ i : ℕ, i < n + 1 →
            best ≤ splitCost visible carry i := by
          intro i hi
          have hin : i ≤ n := Nat.le_of_lt_succ hi
          have hvis : visible n ≤ visible i := hvisible hin
          unfold splitCost
          omega
        exact (fullDescendingScanAux_eq_of_le
          (splitCost visible carry) hremaining).symm
      · simp only [hstop]
        rw [fullDescendingScanAux]
        exact ih (min best (splitCost visible carry n))

/-- The initialized suffix scan equals the initialized full scan. -/
theorem suffixWindowScan_eq_fullDescendingScan
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible) (A : ℕ) :
    suffixWindowScan visible carry A =
      fullDescendingScan (splitCost visible carry) A := by
  unfold suffixWindowScan fullDescendingScan
  exact suffixWindowScanAux_eq_fullDescendingScanAux
    visible carry hvisible A (splitCost visible carry A)

/-- The initialized instrumented scan exposes the same cost as the cost-only
suffix scan. -/
theorem suffixWindowResult_cost
    (visible carry : ℕ → ℕ) (A : ℕ) :
    (suffixWindowResult visible carry A).cost =
      suffixWindowScan visible carry A := by
  unfold suffixWindowResult suffixWindowScan
  exact suffixWindowResultAux_cost visible carry A
    (splitCost visible carry A) 1

/-- Direct finite-minimum statement for the generic suffix compiler. -/
theorem suffixWindowScan_eq_minImage
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible) (A : ℕ) :
    suffixWindowScan visible carry A =
      ((Finset.range (A + 1)).image (splitCost visible carry)).min'
        (by
          refine ⟨splitCost visible carry A, ?_⟩
          exact Finset.mem_image.2 ⟨A, by simp, rfl⟩) := by
  rw [suffixWindowScan_eq_fullDescendingScan visible carry hvisible A]
  exact fullDescendingScan_eq_minImage (splitCost visible carry) A

/-- The instrumented result's cost field is the exact finite minimum. -/
theorem suffixWindowResult_cost_eq_minImage
    (visible carry : ℕ → ℕ) (hvisible : Antitone visible) (A : ℕ) :
    (suffixWindowResult visible carry A).cost =
      ((Finset.range (A + 1)).image (splitCost visible carry)).min'
        (by
          refine ⟨splitCost visible carry A, ?_⟩
          exact Finset.mem_image.2 ⟨A, by simp, rfl⟩) := by
  rw [suffixWindowResult_cost]
  exact suffixWindowScan_eq_minImage visible carry hvisible A

/-- Visible part of a radix representative cost. -/
def radixVisibleCost (p h Q a : ℕ) : ℕ :=
  (p * Q - radixRepresentative p Q a) * (h + 1)

/-- Carry part of a radix representative cost. -/
def radixCarryCost (p Q a : ℕ) : ℕ :=
  padicValNat p ((Q - 1).choose a)

/-- The Block 05 radix cost is definitionally the visible/carry split. -/
theorem radixBarrierCost_eq_splitCost (p h Q a : ℕ) :
    radixBarrierCost p h Q a =
      splitCost (radixVisibleCost p h Q) (radixCarryCost p Q) a := by
  rfl

/-- Radix representatives are monotone in the block index. -/
theorem radixRepresentative_mono
    {p Q a b : ℕ} (hab : a ≤ b) :
    radixRepresentative p Q a ≤ radixRepresentative p Q b := by
  unfold radixRepresentative
  apply min_le_min
  · exact Nat.le_refl Q
  · exact Nat.mul_le_mul_left p (Nat.add_le_add_right hab 1)

/-- Earlier radix blocks have no smaller visible cost. -/
theorem radixVisibleCost_antitone (p h Q : ℕ) :
    Antitone (radixVisibleCost p h Q) := by
  intro a b hab
  unfold radixVisibleCost
  have hrep : radixRepresentative p Q a ≤ radixRepresentative p Q b :=
    radixRepresentative_mono hab
  have hsub : p * Q - radixRepresentative p Q b ≤
      p * Q - radixRepresentative p Q a :=
    Nat.sub_le_sub_left hrep (p * Q)
  exact Nat.mul_le_mul_right (h + 1) hsub

/-- Executable suffix-window cost for the exact radix barrier. -/
def suffixRadixBarrierCost (p h Q : ℕ) : ℕ :=
  suffixWindowScan (radixVisibleCost p h Q) (radixCarryCost p Q)
    ((Q - 1) / p)

/-- Instrumented exact radix suffix compiler. -/
def suffixRadixBarrierResult (p h Q : ℕ) : SuffixWindowResult :=
  suffixWindowResult (radixVisibleCost p h Q) (radixCarryCost p Q)
    ((Q - 1) / p)

/-- The instrumented radix compiler exposes the same exact cost. -/
theorem suffixRadixBarrierResult_cost (p h Q : ℕ) :
    (suffixRadixBarrierResult p h Q).cost = suffixRadixBarrierCost p h Q := by
  unfold suffixRadixBarrierResult suffixRadixBarrierCost suffixWindowResult
  exact suffixWindowResultAux_cost
    (radixVisibleCost p h Q) (radixCarryCost p Q)
    ((Q - 1) / p)
    (splitCost (radixVisibleCost p h Q) (radixCarryCost p Q) ((Q - 1) / p)) 1

/-- The instrumented radix scan never evaluates more than the full
representative count. -/
theorem suffixRadixBarrierResult_tested_bounds (p h Q : ℕ) :
    1 ≤ (suffixRadixBarrierResult p h Q).tested ∧
      (suffixRadixBarrierResult p h Q).tested ≤ (Q - 1) / p + 1 := by
  exact suffixWindowResult_tested_bounds
    (radixVisibleCost p h Q) (radixCarryCost p Q) ((Q - 1) / p)

/-- The suffix-window compiler returns the same exact minimum as the full
Block 05 representative compiler. -/
theorem suffixRadixBarrierCost_eq_minRadixBarrierCost
    (p h Q : ℕ) :
    suffixRadixBarrierCost p h Q = minRadixBarrierCost p h Q := by
  unfold suffixRadixBarrierCost
  rw [suffixWindowScan_eq_fullDescendingScan
    (radixVisibleCost p h Q) (radixCarryCost p Q)
    (radixVisibleCost_antitone p h Q)]
  have hfun : splitCost (radixVisibleCost p h Q) (radixCarryCost p Q) =
      radixBarrierCost p h Q := by
    funext a
    exact (radixBarrierCost_eq_splitCost p h Q a).symm
  rw [hfun, fullDescendingScan_eq_minImage]
  rfl

/-- The instrumented compiler's cost is the exact Block 05 minimum. -/
theorem suffixRadixBarrierResult_cost_eq_minRadixBarrierCost
    (p h Q : ℕ) :
    (suffixRadixBarrierResult p h Q).cost = minRadixBarrierCost p h Q := by
  rw [suffixRadixBarrierResult_cost, suffixRadixBarrierCost_eq_minRadixBarrierCost]

/-- Boolean suffix compiler. -/
def suffixCompilerCrosses (p r h Q : ℕ) : Bool :=
  decide (suffixRadixBarrierCost p h Q < r)

/-- The suffix compiler is extensionally identical to the full Block 05
representative compiler, without any primality or positivity assumptions. -/
theorem suffixCompilerCrosses_eq_radixCompilerCrosses (p r h Q : ℕ) :
    suffixCompilerCrosses p r h Q = radixCompilerCrosses p r h Q := by
  simp [suffixCompilerCrosses, radixCompilerCrosses,
    suffixRadixBarrierCost_eq_minRadixBarrierCost]

/-- Kernel-checked correctness of the suffix compiler against the mathematical
barrier predicate. -/
theorem suffixCompilerCrosses_eq_true_iff
    {p r h Q : ℕ} (hp : p.Prime) (hQ : 0 < Q) :
    suffixCompilerCrosses p r h Q = true ↔
      CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p Q := by
  simp only [suffixCompilerCrosses, decide_eq_true_eq,
    suffixRadixBarrierCost_eq_minRadixBarrierCost]
  exact (binomialPadic_crossesBarrier_iff_minCost hp hQ).symm

end KomorebiPadic
