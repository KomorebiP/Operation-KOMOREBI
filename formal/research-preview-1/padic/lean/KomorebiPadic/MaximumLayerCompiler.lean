import Mathlib.Order.Interval.Finset.Nat
import KomorebiPadic.StableQuotient
import KomorebiPadic.DescendingSearch

/-!
# End-to-end exact maximum-layer compiler

The first noncrossing quotient localizes every active target below `p * Q`.
If `Q > 1`, the preceding crossed barrier supplies the lower endpoint
`p * (Q - 1)`; for `Q = 1`, positivity of the precision supplies target `1`.
Thus the exact maximum lies in one finite stable quotient fiber.
-/

namespace KomorebiPadic

open scoped BigOperators

/-- Lower endpoint of the stable quotient fiber. -/
def stableFiberLower (p Q : ℕ) : ℕ :=
  max 1 (p * (Q - 1))

/-- Upper endpoint of the stable quotient fiber. -/
def stableFiberUpper (p Q : ℕ) : ℕ :=
  p * Q - 1

/-- The stable fiber is nonempty for `p > 1` and positive `Q`. -/
theorem stableFiberLower_le_upper
    {p Q : ℕ} (hp : 1 < p) (hQ : 0 < Q) :
    stableFiberLower p Q ≤ stableFiberUpper p Q := by
  have hQeq : Q = (Q - 1) + 1 := by omega
  have hmul : p * Q = p * (Q - 1) + p := by
    calc
      p * Q = p * ((Q - 1) + 1) := congrArg (fun x : ℕ => p * x) hQeq
      _ = p * (Q - 1) + p := by rw [Nat.mul_add, Nat.mul_one]
  unfold stableFiberLower stableFiberUpper
  refine Nat.max_le.2 ⟨?_, ?_⟩
  · rw [hmul]
    omega
  · rw [hmul]
    omega

/-- At quotient `1`, the stable fiber starts at layer `1`. -/
theorem stableFiberLower_one (p : ℕ) :
    stableFiberLower p 1 = 1 := by
  simp [stableFiberLower]

/-- Beyond quotient `1`, the stable fiber starts at the preceding barrier. -/
theorem stableFiberLower_eq_previous_barrier
    {p Q : ℕ} (hp : 0 < p) (hQ : 1 < Q) :
    stableFiberLower p Q = p * (Q - 1) := by
  apply Nat.max_eq_right
  have hpred : 0 < Q - 1 := by omega
  exact Nat.succ_le_iff.2 (Nat.mul_pos hp hpred)

/-- Selected stable quotient. -/
def stableQuotient (p r h : ℕ) : ℕ :=
  firstNoncrossingQuotient p r h

/-- Lower endpoint specialized to the selected stable quotient. -/
def finalFiberLower (p r h : ℕ) : ℕ :=
  stableFiberLower p (stableQuotient p r h)

/-- Upper endpoint specialized to the selected stable quotient. -/
def finalFiberUpper (p r h : ℕ) : ℕ :=
  stableFiberUpper p (stableQuotient p r h)

/-- Exact target layers detected inside the final stable fiber. -/
def finalFiberTargetSet (p r h : ℕ) : Finset ℕ :=
  (Finset.Icc (finalFiberLower p r h) (finalFiberUpper p r h)).filter fun t =>
    targetCompiler p r h (stableQuotient p r h) t = true

/-- Total candidate set.  The lower endpoint is inserted unconditionally;
under prime and positive-precision hypotheses it is proved to be active. -/
def finalFiberCandidateSet (p r h : ℕ) : Finset ℕ :=
  insert (finalFiberLower p r h) (finalFiberTargetSet p r h)

/-- The final-fiber candidate set is nonempty. -/
theorem finalFiberCandidateSet_nonempty (p r h : ℕ) :
    (finalFiberCandidateSet p r h).Nonempty := by
  refine ⟨finalFiberLower p r h, ?_⟩
  simp [finalFiberCandidateSet]

/-- Executable exact maximum layer in the selected stable fiber. -/
def exactMaximumLayer (p r h : ℕ) : ℕ :=
  (finalFiberCandidateSet p r h).max'
    (finalFiberCandidateSet_nonempty p r h)

/-- The lower stable-fiber endpoint is always at most the returned layer. -/
theorem finalFiberLower_le_exactMaximumLayer (p r h : ℕ) :
    finalFiberLower p r h ≤ exactMaximumLayer p r h := by
  apply Finset.le_max'
  simp [finalFiberCandidateSet]

/-- The specialized stable fiber is nonempty at a prime base. -/
theorem finalFiberLower_le_upper
    {p r h : ℕ} (hp : p.Prime) :
    finalFiberLower p r h ≤ finalFiberUpper p r h := by
  exact stableFiberLower_le_upper hp.one_lt
    (firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp)

/-- The returned layer lies below the final barrier. -/
theorem exactMaximumLayer_le_finalFiberUpper
    {p r h : ℕ} (hp : p.Prime) :
    exactMaximumLayer p r h ≤ finalFiberUpper p r h := by
  have hmem : exactMaximumLayer p r h ∈ finalFiberCandidateSet p r h := by
    unfold exactMaximumLayer
    exact Finset.max'_mem _ _
  rw [finalFiberCandidateSet, Finset.mem_insert] at hmem
  rcases hmem with hlower | hfiltered
  · rw [hlower]
    exact finalFiberLower_le_upper hp
  · rw [finalFiberTargetSet, Finset.mem_filter] at hfiltered
    exact (Finset.mem_Icc.mp hfiltered.1).2

/-- The final fiber's lower endpoint is an actual target. -/
theorem finalFiberLower_isTarget
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    IsTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h)
      (finalFiberLower p r h) := by
  by_cases hQone : stableQuotient p r h = 1
  · unfold finalFiberLower
    rw [hQone, stableFiberLower_one]
    refine ⟨1, 0, by omega, by omega, ?_, by omega⟩
    change ActiveAt r h 0 (padicValNat p ((1 + 0 - 1).choose 0))
    simp [ActiveAt, branchCost, hr]
  · have hQpos : 0 < stableQuotient p r h :=
      firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp
    have hQgt : 1 < stableQuotient p r h := by omega
    have hprevpos : 0 < stableQuotient p r h - 1 := by omega
    have hprevlt : stableQuotient p r h - 1 < stableQuotient p r h := by omega
    have hprev : CrossesBarrier
        (binomialPadicEdgeSystem p r h hp.one_lt) p
        (stableQuotient p r h - 1) :=
      crossesBarrier_of_lt_firstNoncrossing hp hprevpos hprevlt
    have htarget := previous_barrier_reaches_next
      (binomialPadicEdgeSystem p r h hp.one_lt) hQgt hprev
    rw [finalFiberLower,
      stableFiberLower_eq_previous_barrier hp.pos hQgt]
    exact htarget

/-- The returned layer is an actual active target. -/
theorem exactMaximumLayer_isTarget
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    IsTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h)
      (exactMaximumLayer p r h) := by
  have hmem : exactMaximumLayer p r h ∈ finalFiberCandidateSet p r h := by
    unfold exactMaximumLayer
    exact Finset.max'_mem _ _
  rw [finalFiberCandidateSet, Finset.mem_insert] at hmem
  rcases hmem with hlower | hfiltered
  · rw [hlower]
    exact finalFiberLower_isTarget hp hr
  · rw [finalFiberTargetSet, Finset.mem_filter] at hfiltered
    exact (targetCompiler_eq_true_iff_isTarget hp.one_lt).1 hfiltered.2

/-- Every active target at the stable quotient is bounded by the returned
layer. -/
theorem isTarget_le_exactMaximumLayer
    {p r h t : ℕ} (hp : p.Prime)
    (ht : IsTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h) t) :
    t ≤ exactMaximumLayer p r h := by
  have hQpos : 0 < stableQuotient p r h :=
    firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp
  have hstop := firstNoncrossingQuotient_not_crosses
    (p := p) (r := r) (h := h) hp
  have htlt : t < p * stableQuotient p r h :=
    target_lt_barrier_of_not_crosses
      (binomialPadicEdgeSystem p r h hp.one_lt)
      hp.pos hQpos hstop ht
  have htupper : t ≤ finalFiberUpper p r h := by
    unfold finalFiberUpper stableFiberUpper
    omega
  have hlower := finalFiberLower_le_exactMaximumLayer p r h
  by_cases hbelow : t < finalFiberLower p r h
  · omega
  · have htlower : finalFiberLower p r h ≤ t := Nat.le_of_not_gt hbelow
    have hcompiler : targetCompiler p r h (stableQuotient p r h) t = true :=
      (targetCompiler_eq_true_iff_isTarget hp.one_lt).2 ht
    have htmem : t ∈ finalFiberCandidateSet p r h := by
      rw [finalFiberCandidateSet, Finset.mem_insert]
      right
      apply Finset.mem_filter.2
      exact ⟨Finset.mem_Icc.2 ⟨htlower, htupper⟩, hcompiler⟩
    exact Finset.le_max' _ t htmem

/-- Abstract specification of a maximum target layer. -/
def IsMaximumTarget
    (G : PredecessorEdgeSystem) (Q M : ℕ) : Prop :=
  IsTarget G Q M ∧ ∀ t : ℕ, IsTarget G Q t → t ≤ M

/-- End-to-end correctness of the exact maximum-layer compiler. -/
theorem exactMaximumLayer_spec
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    IsMaximumTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h)
      (exactMaximumLayer p r h) := by
  exact ⟨exactMaximumLayer_isTarget hp hr,
    fun t ht => isTarget_le_exactMaximumLayer hp ht⟩


/-- Recover the quotient fiber containing a positive layer. -/
def quotientOfLayer (p t : ℕ) : ℕ :=
  t / p + 1

/-- The exact maximum layer lies in precisely the selected quotient fiber. -/
theorem quotientOf_exactMaximumLayer
    {p r h : ℕ} (hp : p.Prime) :
    quotientOfLayer p (exactMaximumLayer p r h) = stableQuotient p r h := by
  have hQpos : 0 < stableQuotient p r h :=
    firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp
  have hQone : 1 ≤ stableQuotient p r h := Nat.succ_le_iff.2 hQpos
  have hlower := finalFiberLower_le_exactMaximumLayer p r h
  have hupper := exactMaximumLayer_le_finalFiberUpper
    (p := p) (r := r) (h := h) hp
  have hlower' : p * (stableQuotient p r h - 1) ≤
      exactMaximumLayer p r h := by
    exact (Nat.le_max_right 1 (p * (stableQuotient p r h - 1))).trans hlower
  have hupper' : exactMaximumLayer p r h < p * stableQuotient p r h := by
    unfold finalFiberUpper stableFiberUpper at hupper
    have hmulpos : 0 < p * stableQuotient p r h :=
      Nat.mul_pos hp.pos hQpos
    omega
  have hdiv : exactMaximumLayer p r h / p = stableQuotient p r h - 1 := by
    apply Nat.div_eq_of_lt_le
    · simpa [Nat.mul_comm] using hlower'
    · have hQpred : stableQuotient p r h - 1 + 1 = stableQuotient p r h :=
        Nat.sub_add_cancel hQone
      simpa [Nat.mul_comm, hQpred] using hupper'
  unfold quotientOfLayer
  rw [hdiv]
  exact Nat.sub_add_cancel hQone

/-- The active target set at the stable quotient is exactly the initial interval
from `1` through the compiled maximum layer. -/
theorem isTarget_iff_le_exactMaximumLayer
    {p r h t : ℕ} (hp : p.Prime) (hr : 0 < r) :
    IsTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h) t ↔
      1 ≤ t ∧ t ≤ exactMaximumLayer p r h := by
  constructor
  · intro ht
    rcases ht with ⟨q, k, hq1, hqQ, hedge, hsum⟩
    refine ⟨?_, ?_⟩
    · omega
    · exact isTarget_le_exactMaximumLayer hp
        ⟨q, k, hq1, hqQ, hedge, hsum⟩
  · rintro ⟨ht1, htM⟩
    exact target_interval_property
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (exactMaximumLayer_isTarget hp hr) t ht1 htM

/-- The compiled layer is both the maximum active target and a fixed-point
certificate for its quotient fiber. -/
theorem exactMaximumLayer_fixedPoint_spec
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    quotientOfLayer p (exactMaximumLayer p r h) = stableQuotient p r h ∧
    IsMaximumTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      (stableQuotient p r h)
      (exactMaximumLayer p r h) := by
  exact ⟨quotientOf_exactMaximumLayer hp, exactMaximumLayer_spec hp hr⟩

/-- Number of candidate layers in the final stable fiber. -/
def finalFiberWidth (p r h : ℕ) : ℕ :=
  finalFiberUpper p r h + 1 - finalFiberLower p r h

/-- The final stable fiber has positive width at a prime base. -/
theorem finalFiberWidth_pos
    {p r h : ℕ} (hp : p.Prime) :
    0 < finalFiberWidth p r h := by
  unfold finalFiberWidth
  have hbounds := finalFiberLower_le_upper (p := p) (r := r) (h := h) hp
  omega

/-- The final-fiber width always fits below the successor of its upper endpoint. -/
theorem finalFiberWidth_le_upper_succ (p r h : ℕ) :
    finalFiberWidth p r h ≤ finalFiberUpper p r h + 1 := by
  unfold finalFiberWidth
  exact Nat.sub_le _ _

/-- The lowest index inspected by the descending scan is exactly the lower
endpoint of the final stable fiber. -/
theorem finalFiberTerminal_eq_lower
    {p r h : ℕ} (hp : p.Prime) :
    finalFiberUpper p r h + 1 - finalFiberWidth p r h =
      finalFiberLower p r h := by
  unfold finalFiberWidth
  have hbounds := finalFiberLower_le_upper (p := p) (r := r) (h := h) hp
  omega

/-- The exact target compiler accepts the final fiber's lower endpoint. -/
theorem targetCompiler_finalFiberLower_true
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    targetCompiler p r h (stableQuotient p r h)
      (finalFiberLower p r h) = true := by
  exact (targetCompiler_eq_true_iff_isTarget hp.one_lt).2
    (finalFiberLower_isTarget hp hr)

/-- Instrumented descending boundary search through the final stable fiber. -/
def finalFiberBoundaryResult (p r h : ℕ) : FirstTrueDescendingResult :=
  firstTrueDescendingAux
    (targetCompiler p r h (stableQuotient p r h))
    (finalFiberUpper p r h)
    (finalFiberWidth p r h)

/-- Layer returned by the descending final-fiber boundary search. -/
def finalFiberBoundaryLayer (p r h : ℕ) : ℕ :=
  (finalFiberBoundaryResult p r h).value

/-- Exact number of target-membership tests used by the descending boundary search. -/
def finalFiberBoundaryTestCount (p r h : ℕ) : ℕ :=
  (finalFiberBoundaryResult p r h).tested

/-- Exact successful-search specification for the descending final-fiber scan. -/
theorem finalFiberBoundaryResult_spec
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    FirstTrueDescendingSpec
      (targetCompiler p r h (stableQuotient p r h))
      (finalFiberLower p r h)
      (finalFiberUpper p r h)
      (finalFiberBoundaryResult p r h) := by
  unfold finalFiberBoundaryResult
  have hterminal :
      targetCompiler p r h (stableQuotient p r h)
        (finalFiberUpper p r h + 1 - finalFiberWidth p r h) = true := by
    rw [finalFiberTerminal_eq_lower hp]
    exact targetCompiler_finalFiberLower_true hp hr
  have hspec := firstTrueDescendingAux_spec
    (targetCompiler p r h (stableQuotient p r h))
    (finalFiberWidth_pos hp)
    (finalFiberWidth_le_upper_succ p r h)
    hterminal
  rw [finalFiberTerminal_eq_lower hp] at hspec
  exact hspec

/-- The descending boundary search is extensionally equal to the reference
finite-set maximum. -/
theorem finalFiberBoundaryLayer_eq_exactMaximumLayer
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    finalFiberBoundaryLayer p r h = exactMaximumLayer p r h := by
  have hspec := finalFiberBoundaryResult_spec
    (p := p) (r := r) (h := h) hp hr
  unfold FirstTrueDescendingSpec at hspec
  rcases hspec with ⟨hlower, hupper, htrue, habove, htested⟩
  have hboundaryTarget :
      IsTarget
        (binomialPadicEdgeSystem p r h hp.one_lt)
        (stableQuotient p r h)
        (finalFiberBoundaryLayer p r h) := by
    apply (targetCompiler_eq_true_iff_isTarget hp.one_lt).1
    simpa [finalFiberBoundaryLayer] using htrue
  have hboundary_le :
      finalFiberBoundaryLayer p r h ≤ exactMaximumLayer p r h :=
    isTarget_le_exactMaximumLayer hp hboundaryTarget
  have hexact_le :
      exactMaximumLayer p r h ≤ finalFiberBoundaryLayer p r h := by
    by_contra hnot
    have hgt :
        finalFiberBoundaryLayer p r h < exactMaximumLayer p r h := by
      omega
    have hfalse :
        targetCompiler p r h (stableQuotient p r h)
          (exactMaximumLayer p r h) = false := by
      apply habove (exactMaximumLayer p r h)
      · simpa [finalFiberBoundaryLayer] using hgt
      · exact exactMaximumLayer_le_finalFiberUpper hp
    have htrueExact :
        targetCompiler p r h (stableQuotient p r h)
          (exactMaximumLayer p r h) = true :=
      (targetCompiler_eq_true_iff_isTarget hp.one_lt).2
        (exactMaximumLayer_isTarget hp hr)
    rw [htrueExact] at hfalse
    contradiction
  exact Nat.le_antisymm hboundary_le hexact_le

/-- Exact distance formula for the descending boundary-search test count. -/
theorem finalFiberBoundaryTestCount_eq_distance
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    finalFiberBoundaryTestCount p r h =
      finalFiberUpper p r h - finalFiberBoundaryLayer p r h + 1 := by
  have hspec := finalFiberBoundaryResult_spec
    (p := p) (r := r) (h := h) hp hr
  exact hspec.2.2.2.2

/-- Exact test-count formula expressed through the reference maximum. -/
theorem finalFiberBoundaryTestCount_eq_exactDistance
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    finalFiberBoundaryTestCount p r h =
      finalFiberUpper p r h - exactMaximumLayer p r h + 1 := by
  rw [finalFiberBoundaryTestCount_eq_distance hp hr,
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr]

/-- The descending boundary search performs at least one membership test. -/
theorem finalFiberBoundaryTestCount_pos
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    0 < finalFiberBoundaryTestCount p r h := by
  rw [finalFiberBoundaryTestCount_eq_distance hp hr]
  have hspec := finalFiberBoundaryResult_spec
    (p := p) (r := r) (h := h) hp hr
  unfold FirstTrueDescendingSpec at hspec
  have hupper : finalFiberBoundaryLayer p r h ≤ finalFiberUpper p r h := by
    simpa [finalFiberBoundaryLayer] using hspec.2.1
  omega

/-- The descending boundary search never evaluates more candidates than the
full final-fiber width. -/
theorem finalFiberBoundaryTestCount_le_width
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    finalFiberBoundaryTestCount p r h ≤ finalFiberWidth p r h := by
  rw [finalFiberBoundaryTestCount_eq_distance hp hr]
  have hspec := finalFiberBoundaryResult_spec
    (p := p) (r := r) (h := h) hp hr
  unfold FirstTrueDescendingSpec at hspec
  have hlower : finalFiberLower p r h ≤ finalFiberBoundaryLayer p r h := by
    simpa [finalFiberBoundaryLayer] using hspec.1
  unfold finalFiberWidth
  omega

/-- The final stable fiber contains at most `p` candidate layers. -/
theorem finalFiberWidth_le_base
    {p r h : ℕ} (hp : p.Prime) :
    finalFiberWidth p r h ≤ p := by
  have hQpos : 0 < stableQuotient p r h :=
    firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp
  have hQeq :
      stableQuotient p r h = (stableQuotient p r h - 1) + 1 := by
    omega
  have hmul :
      p * stableQuotient p r h =
        p * (stableQuotient p r h - 1) + p := by
    calc
      p * stableQuotient p r h =
          p * ((stableQuotient p r h - 1) + 1) :=
        congrArg (fun x : ℕ => p * x) hQeq
      _ = p * (stableQuotient p r h - 1) + p := by
        rw [Nat.mul_add, Nat.mul_one]
  have hprodpos : 0 < p * stableQuotient p r h :=
    Nat.mul_pos hp.pos hQpos
  have hupperEq :
      finalFiberUpper p r h + 1 = p * stableQuotient p r h := by
    unfold finalFiberUpper stableFiberUpper
    omega
  have hlower :
      p * (stableQuotient p r h - 1) ≤ finalFiberLower p r h := by
    unfold finalFiberLower stableFiberLower
    exact Nat.le_max_right _ _
  unfold finalFiberWidth
  rw [hupperEq, hmul]
  omega

/-- Closed accounting bound for the optimized final-fiber boundary search. -/
theorem finalFiberBoundaryTestCount_bounds
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    1 ≤ finalFiberBoundaryTestCount p r h ∧
      finalFiberBoundaryTestCount p r h ≤ p := by
  constructor
  · exact Nat.succ_le_iff.2 (finalFiberBoundaryTestCount_pos hp hr)
  · exact (finalFiberBoundaryTestCount_le_width hp hr).trans
      (finalFiberWidth_le_base hp)

/-- Number of quotient barrier tests in the sequential first-failure search. -/
def quotientTestCount (p r h : ℕ) : ℕ :=
  (stableQuotientSearchResult p r h).tested

/-- Number of target-membership tests in the complete final-fiber scan. -/
def finalFiberTestCount (p r h : ℕ) : ℕ :=
  (Finset.Icc (finalFiberLower p r h) (finalFiberUpper p r h)).card

/-- Total number of complete radix representative costs evaluated across all
quotient barrier tests. -/
def barrierRepresentativeTestCount (p r h : ℕ) : ℕ :=
  (Finset.Icc 1 (stableQuotient p r h)).sum fun Q =>
    (suffixRadixBarrierResult p h Q).tested

/-- Fully instrumented end-to-end compiler result. -/
structure MaximumLayerCompilerResult where
  quotient : ℕ
  layer : ℕ
  quotientTests : ℕ
  finalFiberTests : ℕ
  barrierRepresentativeTests : ℕ
  deriving Repr, DecidableEq

/-- Executable end-to-end compiler with exact result and accounting fields. -/
def maximumLayerCompiler (p r h : ℕ) : MaximumLayerCompilerResult where
  quotient := stableQuotient p r h
  layer := finalFiberBoundaryLayer p r h
  quotientTests := quotientTestCount p r h
  finalFiberTests := finalFiberBoundaryTestCount p r h
  barrierRepresentativeTests := barrierRepresentativeTestCount p r h

/-- Exact closed form for the number of final-fiber membership tests. -/
theorem finalFiberTestCount_eq (p r h : ℕ) :
    finalFiberTestCount p r h =
      finalFiberUpper p r h + 1 - finalFiberLower p r h := by
  exact Nat.card_Icc _ _

/-- At a prime base, the final-fiber scan executes at least one test. -/
theorem finalFiberTestCount_pos
    {p r h : ℕ} (hp : p.Prime) :
    0 < finalFiberTestCount p r h := by
  rw [finalFiberTestCount_eq]
  have hbounds := finalFiberLower_le_upper (p := p) (r := r) (h := h) hp
  omega

/-- The compiler's principal fields satisfy the exact stable-quotient and
maximum-target specifications. -/
theorem maximumLayerCompiler_spec
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    let out := maximumLayerCompiler p r h
    out.quotient = stableQuotient p r h ∧
    out.layer = exactMaximumLayer p r h ∧
    out.quotientTests = out.quotient ∧
    0 < out.finalFiberTests ∧
    IsMaximumTarget
      (binomialPadicEdgeSystem p r h hp.one_lt)
      out.quotient out.layer := by
  have htested := stableQuotientSearchResult_tested
    (p := p) (r := r) (h := h) hp
  have hlayer := finalFiberBoundaryLayer_eq_exactMaximumLayer
    (p := p) (r := r) (h := h) hp hr
  have hfiberTests := finalFiberBoundaryTestCount_pos
    (p := p) (r := r) (h := h) hp hr
  dsimp [maximumLayerCompiler, quotientTestCount]
  refine ⟨rfl, hlayer, ?_, hfiberTests, ?_⟩
  · simpa [stableQuotient] using htested
  · rw [hlayer]
    exact exactMaximumLayer_spec hp hr

/-- The executable compiler's optimized final-fiber accounting is bounded
between one and the prime base. -/
theorem maximumLayerCompiler_finalFiberTests_bounds
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    let out := maximumLayerCompiler p r h
    1 ≤ out.finalFiberTests ∧ out.finalFiberTests ≤ p := by
  simpa [maximumLayerCompiler] using
    (finalFiberBoundaryTestCount_bounds (p := p) (r := r) (h := h) hp hr)

end KomorebiPadic
