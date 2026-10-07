import KomorebiPadic.ConcreteBinomialModel

/-!
# Quotient barrier criterion

For quotient states `1, ..., Q`, the next quotient is forced precisely when the
target `p * Q` is active. Because the target set is an initial interval, failure
of this single barrier target excludes every target at or above the barrier.
The barrier equation also forces the correction order to lie on the diagonal
`k = p * Q - q`.
-/

namespace KomorebiPadic

/-- The quotient barrier target at state bound `Q`. -/
def CrossesBarrier
    (G : PredecessorEdgeSystem) (p Q : ℕ) : Prop :=
  IsTarget G Q (p * Q)

/-- A missing barrier excludes every target at or above it. -/
theorem target_lt_barrier_of_not_crosses
    (G : PredecessorEdgeSystem) {p Q t : ℕ}
    (hp : 0 < p) (hQ : 0 < Q)
    (hstop : ¬ CrossesBarrier G p Q)
    (ht : IsTarget G Q t) :
    t < p * Q := by
  by_contra hnot
  have hle : p * Q ≤ t := Nat.le_of_not_gt hnot
  have hbarrier : IsTarget G Q (p * Q) :=
    isTarget_of_between G ht (Nat.mul_pos hp hQ) hle
  exact hstop hbarrier

/-- If all targets lie below the barrier, the barrier itself is absent. -/
theorem not_crosses_of_all_targets_lt
    (G : PredecessorEdgeSystem) {p Q : ℕ}
    (hbelow : ∀ t : ℕ, IsTarget G Q t → t < p * Q) :
    ¬ CrossesBarrier G p Q := by
  intro hbarrier
  exact (Nat.lt_irrefl (p * Q)) (hbelow (p * Q) hbarrier)

/-- Barrier absence is equivalent to a strict upper bound on every target. -/
theorem not_crosses_iff_all_targets_lt
    (G : PredecessorEdgeSystem) {p Q : ℕ}
    (hp : 0 < p) (hQ : 0 < Q) :
    (¬ CrossesBarrier G p Q) ↔
      ∀ t : ℕ, IsTarget G Q t → t < p * Q := by
  constructor
  · intro hstop t ht
    exact target_lt_barrier_of_not_crosses G hp hQ hstop ht
  · intro hbelow
    exact not_crosses_of_all_targets_lt G hbelow

/-- Enlarging the quotient interval preserves every existing target. -/
theorem isTarget_mono_quotient
    (G : PredecessorEdgeSystem) {Q₁ Q₂ t : ℕ}
    (ht : IsTarget G Q₁ t) (hQ : Q₁ ≤ Q₂) :
    IsTarget G Q₂ t := by
  rcases ht with ⟨q, k, hq1, hqQ, hedge, htarget⟩
  exact ⟨q, k, hq1, hqQ.trans hQ, hedge, htarget⟩

/-- A crossed preceding barrier remains a target at the next quotient stage. -/
theorem previous_barrier_reaches_next
    (G : PredecessorEdgeSystem) {p Q : ℕ}
    (hQ : 1 < Q) (hprev : CrossesBarrier G p (Q - 1)) :
    IsTarget G Q (p * (Q - 1)) := by
  unfold CrossesBarrier at hprev
  exact isTarget_mono_quotient G hprev (by omega)

/-- At the first failed barrier, all targets lie in the stable quotient corridor. -/
theorem stable_quotient_corridor
    (G : PredecessorEdgeSystem) {p Q : ℕ}
    (hp : 0 < p) (hQ : 1 < Q)
    (hprev : CrossesBarrier G p (Q - 1))
    (hstop : ¬ CrossesBarrier G p Q) :
    IsTarget G Q (p * (Q - 1)) ∧
      ∀ t : ℕ, IsTarget G Q t → t ≤ p * Q - 1 := by
  constructor
  · exact previous_barrier_reaches_next G hQ hprev
  · intro t ht
    have hlt := target_lt_barrier_of_not_crosses G hp (by omega) hstop ht
    omega

/-- A barrier target is exactly an active diagonal edge `k = p*Q-q`. -/
theorem crossesBarrier_iff_diagonal
    (G : PredecessorEdgeSystem) {p Q : ℕ} (hp : 0 < p) :
    CrossesBarrier G p Q ↔
      ∃ q : ℕ, 1 ≤ q ∧ q ≤ Q ∧ G.edge q (p * Q - q) := by
  constructor
  · rintro ⟨q, k, hq1, hqQ, hedge, htarget⟩
    refine ⟨q, hq1, hqQ, ?_⟩
    have hk : k = p * Q - q := by omega
    simpa [hk] using hedge
  · rintro ⟨q, hq1, hqQ, hedge⟩
    have hp1 : 1 ≤ p := hp
    have hqbarrier : q ≤ p * Q := by
      calc
        q ≤ Q := hqQ
        _ = 1 * Q := by simp
        _ ≤ p * Q := Nat.mul_le_mul_right Q hp1
    refine ⟨q, p * Q - q, hq1, hqQ, hedge, ?_⟩
    omega

/-- Concrete valuation form of the barrier criterion. -/
theorem binomialPadic_crossesBarrier_iff
    {p r h Q : ℕ} (hp : 1 < p) :
    CrossesBarrier (binomialPadicEdgeSystem p r h hp) p Q ↔
      ∃ q : ℕ, 1 ≤ q ∧ q ≤ Q ∧
        ActiveAt r h (p * Q - q)
          (padicValNat p ((p * Q - 1).choose (p * Q - q))) := by
  rw [crossesBarrier_iff_diagonal
    (binomialPadicEdgeSystem p r h hp) (Nat.zero_lt_of_lt hp)]
  constructor
  · rintro ⟨q, hq1, hqQ, hedge⟩
    have hp1 : 1 ≤ p := Nat.le_of_lt hp
    have hqbarrier : q ≤ p * Q := by
      calc
        q ≤ Q := hqQ
        _ = 1 * Q := by simp
        _ ≤ p * Q := Nat.mul_le_mul_right Q hp1
    have hsum : q + (p * Q - q) = p * Q := by omega
    refine ⟨q, hq1, hqQ, ?_⟩
    change ActiveAt r h (p * Q - q)
      (padicValNat p ((q + (p * Q - q) - 1).choose (p * Q - q))) at hedge
    simpa [hsum] using hedge
  · rintro ⟨q, hq1, hqQ, hedge⟩
    have hp1 : 1 ≤ p := Nat.le_of_lt hp
    have hqbarrier : q ≤ p * Q := by
      calc
        q ≤ Q := hqQ
        _ = 1 * Q := by simp
        _ ≤ p * Q := Nat.mul_le_mul_right Q hp1
    have hsum : q + (p * Q - q) = p * Q := by omega
    refine ⟨q, hq1, hqQ, ?_⟩
    change ActiveAt r h (p * Q - q)
      (padicValNat p ((q + (p * Q - q) - 1).choose (p * Q - q)))
    simpa [hsum] using hedge

/-- The inherited correction-order bound makes the final quotient barrier stop. -/
theorem no_crossing_of_diagonal_orders_large
    (G : PredecessorEdgeSystem) {p Q K : ℕ} (hp : 0 < p)
    (hlarge : K < (p - 1) * Q)
    (hedgeOrder : ∀ {q k : ℕ}, 1 ≤ q → q ≤ Q → G.edge q k → k ≤ K) :
    ¬ CrossesBarrier G p Q := by
  rw [crossesBarrier_iff_diagonal G hp]
  rintro ⟨q, hq1, hqQ, hedge⟩
  have hk := hedgeOrder hq1 hqQ hedge
  have hpdecomp : p = (p - 1) + 1 := by omega
  have hmul : p * Q = (p - 1) * Q + Q := by
    calc
      p * Q = ((p - 1) + 1) * Q := congrArg (fun x => x * Q) hpdecomp
      _ = (p - 1) * Q + 1 * Q := Nat.add_mul (p - 1) 1 Q
      _ = (p - 1) * Q + Q := by simp
  have hdiag : (p - 1) * Q ≤ p * Q - q := by
    omega
  omega


/-- The concrete binomial graph stops whenever the coarse correction bound lies
strictly below the diagonal order forced by the barrier. -/
theorem binomialPadic_no_crossing_of_coarseK_lt
    {p r h Q : ℕ} (hp : 1 < p)
    (hlarge : coarseK r h < (p - 1) * Q) :
    ¬ CrossesBarrier (binomialPadicEdgeSystem p r h hp) p Q := by
  apply no_crossing_of_diagonal_orders_large
    (binomialPadicEdgeSystem p r h hp) (Nat.zero_lt_of_lt hp) hlarge
  intro q k hq1 hqQ hedge
  change ActiveAt r h k
    (padicValNat p ((q + k - 1).choose k)) at hedge
  exact activeAt_implies_le_coarseK hedge

end KomorebiPadic
