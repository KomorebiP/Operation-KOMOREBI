import KomorebiPadic.TargetCompiler
import KomorebiPadic.SequentialSearch

/-!
# First noncrossing quotient

The coarse correction-order bound gives a finite terminal quotient whose
barrier cannot cross.  A genuine left-to-right Boolean search therefore finds
the first noncrossing quotient, and the generic first-false theorem supplies
minimality together with exact test accounting.
-/

namespace KomorebiPadic

/-- Finite quotient bound forced by the coarse correction-order obstruction. -/
def quotientSearchBound (p r h : ℕ) : ℕ :=
  coarseK r h / (p - 1) + 1

/-- The quotient search bound is always positive. -/
theorem quotientSearchBound_pos (p r h : ℕ) :
    0 < quotientSearchBound p r h := by
  unfold quotientSearchBound
  exact Nat.succ_pos _

/-- At a prime base, the coarse order bound lies strictly below the diagonal
order at `quotientSearchBound`. -/
theorem coarseK_lt_diagonal_at_searchBound
    {p r h : ℕ} (hp : p.Prime) :
    coarseK r h < (p - 1) * quotientSearchBound p r h := by
  let K := coarseK r h
  let d := p - 1
  have hd : 0 < d := by
    have hpgt : 1 < p := hp.one_lt
    dsimp [d]
    omega
  have hmod : K % d < d := Nat.mod_lt K hd
  have hdecomp : K % d + d * (K / d) = K := Nat.mod_add_div K d
  have hlt : K < d * (K / d) + d := by omega
  dsimp [quotientSearchBound, K, d] at hlt ⊢
  simpa [Nat.mul_add] using hlt

/-- The terminal search-bound quotient cannot cross its barrier. -/
theorem quotientSearchBound_not_crosses
    {p r h : ℕ} (hp : p.Prime) :
    ¬ CrossesBarrier
      (binomialPadicEdgeSystem p r h hp.one_lt) p
      (quotientSearchBound p r h) := by
  exact binomialPadic_no_crossing_of_coarseK_lt hp.one_lt
    (coarseK_lt_diagonal_at_searchBound hp)

/-- False reflection form of the exact suffix barrier compiler. -/
theorem suffixCompilerCrosses_eq_false_iff
    {p r h Q : ℕ} (hp : p.Prime) (hQ : 0 < Q) :
    suffixCompilerCrosses p r h Q = false ↔
      ¬ CrossesBarrier
        (binomialPadicEdgeSystem p r h hp.one_lt) p Q := by
  constructor
  · intro hfalse hcross
    have htrue := (suffixCompilerCrosses_eq_true_iff
      (p := p) (r := r) (h := h) (Q := Q) hp hQ).2 hcross
    rw [hfalse] at htrue
    contradiction
  · intro hnot
    cases hcompiler : suffixCompilerCrosses p r h Q with
    | false => rfl
    | true =>
        have hcross := (suffixCompilerCrosses_eq_true_iff
          (p := p) (r := r) (h := h) (Q := Q) hp hQ).1 hcompiler
        exact (hnot hcross).elim

/-- Instrumented sequential quotient search. -/
def stableQuotientSearchResult (p r h : ℕ) : FirstFalseResult :=
  firstFalseResultAux (suffixCompilerCrosses p r h) 1
    (quotientSearchBound p r h)

/-- First quotient at which the exact barrier compiler does not cross. -/
def firstNoncrossingQuotient (p r h : ℕ) : ℕ :=
  (stableQuotientSearchResult p r h).value

/-- The terminal quotient is false for the executable suffix compiler. -/
theorem suffixCompiler_false_at_searchBound
    {p r h : ℕ} (hp : p.Prime) :
    suffixCompilerCrosses p r h (quotientSearchBound p r h) = false := by
  exact (suffixCompilerCrosses_eq_false_iff hp
    (quotientSearchBound_pos p r h)).2
    (quotientSearchBound_not_crosses hp)

/-- Exact successful-search specification for the stable quotient search. -/
theorem stableQuotientSearchResult_spec
    {p r h : ℕ} (hp : p.Prime) :
    FirstFalseSpec
      (suffixCompilerCrosses p r h) 1
      (quotientSearchBound p r h)
      (stableQuotientSearchResult p r h) := by
  apply firstFalseResultAux_spec
  · exact quotientSearchBound_pos p r h
  · have hfalse := suffixCompiler_false_at_searchBound
      (p := p) (r := r) (h := h) hp
    have hidx : 1 + quotientSearchBound p r h - 1 =
        quotientSearchBound p r h := by omega
    rw [hidx]
    exact hfalse

/-- The first noncrossing quotient is positive at a prime base. -/
theorem firstNoncrossingQuotient_pos
    {p r h : ℕ} (hp : p.Prime) :
    0 < firstNoncrossingQuotient p r h := by
  have hspec := stableQuotientSearchResult_spec
    (p := p) (r := r) (h := h) hp
  unfold FirstFalseSpec at hspec
  unfold firstNoncrossingQuotient
  omega

/-- The first noncrossing quotient lies within the coarse finite bound. -/
theorem firstNoncrossingQuotient_le_bound
    {p r h : ℕ} (hp : p.Prime) :
    firstNoncrossingQuotient p r h ≤ quotientSearchBound p r h := by
  have hspec := stableQuotientSearchResult_spec (p := p) (r := r) (h := h) hp
  unfold FirstFalseSpec at hspec
  unfold firstNoncrossingQuotient
  omega

/-- The selected quotient is genuinely noncrossing. -/
theorem firstNoncrossingQuotient_not_crosses
    {p r h : ℕ} (hp : p.Prime) :
    ¬ CrossesBarrier
      (binomialPadicEdgeSystem p r h hp.one_lt) p
      (firstNoncrossingQuotient p r h) := by
  have hspec := stableQuotientSearchResult_spec (p := p) (r := r) (h := h) hp
  unfold FirstFalseSpec at hspec
  have hfalse : suffixCompilerCrosses p r h
      (firstNoncrossingQuotient p r h) = false := by
    exact hspec.2.2.1
  exact (suffixCompilerCrosses_eq_false_iff hp
    (firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp)).1 hfalse

/-- Every positive quotient strictly before the selected one crosses. -/
theorem crossesBarrier_of_lt_firstNoncrossing
    {p r h q : ℕ} (hp : p.Prime)
    (hq : 0 < q) (hlt : q < firstNoncrossingQuotient p r h) :
    CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p q := by
  have hspec := stableQuotientSearchResult_spec (p := p) (r := r) (h := h) hp
  unfold FirstFalseSpec at hspec
  have htrue : suffixCompilerCrosses p r h q = true :=
    hspec.2.2.2.1 q (by omega) hlt
  exact (suffixCompilerCrosses_eq_true_iff hp hq).1 htrue

/-- The instrumented quotient search reports exactly the selected quotient
because it tests `1, 2, ..., Q*`. -/
theorem stableQuotientSearchResult_tested
    {p r h : ℕ} (hp : p.Prime) :
    (stableQuotientSearchResult p r h).tested =
      firstNoncrossingQuotient p r h := by
  have hspec := stableQuotientSearchResult_spec (p := p) (r := r) (h := h) hp
  unfold FirstFalseSpec at hspec
  unfold firstNoncrossingQuotient
  have hpos : 1 ≤ (stableQuotientSearchResult p r h).value := hspec.1
  omega

/-- Exact first-failure specification of the stable quotient. -/
theorem firstNoncrossingQuotient_spec
    {p r h : ℕ} (hp : p.Prime) :
    (¬ CrossesBarrier
        (binomialPadicEdgeSystem p r h hp.one_lt) p
        (firstNoncrossingQuotient p r h)) ∧
      ∀ q : ℕ, 0 < q → q < firstNoncrossingQuotient p r h →
        CrossesBarrier
          (binomialPadicEdgeSystem p r h hp.one_lt) p q := by
  exact ⟨firstNoncrossingQuotient_not_crosses hp,
    fun q hq hlt => crossesBarrier_of_lt_firstNoncrossing hp hq hlt⟩

end KomorebiPadic
