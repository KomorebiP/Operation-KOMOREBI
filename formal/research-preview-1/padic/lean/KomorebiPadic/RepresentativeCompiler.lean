import KomorebiPadic.RadixDescent

/-!
# Exact radix representatives for the quotient barrier

The Kummer descent theorem makes the carry cost constant on every interval

`p * a < q ≤ p * (a + 1)`.

Inside such a block, increasing `q` decreases the diagonal correction order
`p * Q - q`.  Consequently the maximal admissible point

`min Q (p * (a + 1))`

is the unique representative needed to test that block for barrier crossing.
This file turns that observation into an exact finite compiler criterion.
-/

namespace KomorebiPadic

/-- The maximal point of radix block `a` that remains inside `1, ..., Q`. -/
def radixRepresentative (p Q a : ℕ) : ℕ :=
  min Q (p * (a + 1))

/-- The concrete carry attached to a diagonal barrier branch. -/
def barrierCarry (p Q q : ℕ) : ℕ :=
  padicValNat p ((p * Q - 1).choose (p * Q - q))

/-- The total cost of a diagonal barrier branch. -/
def barrierBranchCost (p h Q q : ℕ) : ℕ :=
  branchCost h (p * Q - q) (barrierCarry p Q q)

/-- The compressed cost of radix block `a`. -/
def radixBarrierCost (p h Q a : ℕ) : ℕ :=
  branchCost h (p * Q - radixRepresentative p Q a)
    (padicValNat p ((Q - 1).choose a))

/-- A quotient is `a` exactly throughout the radix interval
`p*a < q ≤ p*(a+1)`. -/
theorem quotient_eq_of_radix_block
    {p a q : ℕ} (hp : 0 < p)
    (hlower : p * a < q) (hupper : q ≤ p * (a + 1)) :
    (q - 1) / p = a := by
  apply Nat.le_antisymm
  · have hlt : q - 1 < (a + 1) * p := by
      have : q - 1 < p * (a + 1) := by omega
      simpa [Nat.mul_comm] using this
    have hdivlt : (q - 1) / p < a + 1 :=
      (Nat.div_lt_iff_lt_mul hp).2 hlt
    omega
  · apply (Nat.le_div_iff_mul_le hp).2
    have hmul : p * a ≤ q - 1 := by omega
    simpa [Nat.mul_comm] using hmul

/-- The radix representative lies strictly above its block's lower wall. -/
theorem radixRepresentative_gt_lower
    {p Q a : ℕ} (hp : 0 < p) (hblock : p * a < Q) :
    p * a < radixRepresentative p Q a := by
  rw [radixRepresentative, Nat.lt_min]
  constructor
  · exact hblock
  · simpa [Nat.succ_eq_add_one] using
      ((Nat.mul_lt_mul_left hp).2 (Nat.lt_succ_self a))

/-- A radix representative remains inside the quotient interval. -/
theorem radixRepresentative_le_Q (p Q a : ℕ) :
    radixRepresentative p Q a ≤ Q := by
  exact Nat.min_le_left _ _

/-- A radix representative remains below its radix-block ceiling. -/
theorem radixRepresentative_le_ceiling (p Q a : ℕ) :
    radixRepresentative p Q a ≤ p * (a + 1) := by
  exact Nat.min_le_right _ _

/-- Every nonempty radix block has a positive representative. -/
theorem radixRepresentative_pos
    {p Q a : ℕ} (hp : 0 < p) (hblock : p * a < Q) :
    0 < radixRepresentative p Q a := by
  have h := radixRepresentative_gt_lower hp hblock
  omega

/-- The representative of a nonempty radix block has quotient exactly `a`. -/
theorem radixRepresentative_quotient
    {p Q a : ℕ} (hp : 0 < p) (hblock : p * a < Q) :
    (radixRepresentative p Q a - 1) / p = a := by
  exact quotient_eq_of_radix_block hp
    (radixRepresentative_gt_lower hp hblock)
    (radixRepresentative_le_ceiling p Q a)

/-- Binomial symmetry converts the diagonal index `p*Q-q` to the low index
`q-1` used by the radix-descent theorem. -/
theorem barrier_choose_symm
    {p Q q : ℕ} (hp : 0 < p) (hq1 : 1 ≤ q) (hqQ : q ≤ Q) :
    (p * Q - 1).choose (p * Q - q) =
      (p * Q - 1).choose (q - 1) := by
  have hp1 : 1 ≤ p := hp
  have hqbarrier : q ≤ p * Q := by
    calc
      q ≤ Q := hqQ
      _ = 1 * Q := by simp
      _ ≤ p * Q := Nat.mul_le_mul_right Q hp1
  have hk : p * Q - q ≤ p * Q - 1 := by omega
  have hsub : p * Q - 1 - (p * Q - q) = q - 1 := by omega
  calc
    (p * Q - 1).choose (p * Q - q) =
        (p * Q - 1).choose (p * Q - 1 - (p * Q - q)) :=
      (Nat.choose_symm hk).symm
    _ = (p * Q - 1).choose (q - 1) := by rw [hsub]

/-- Concrete diagonal carries descend to the smaller binomial indexed by the
radix quotient. -/
theorem barrierCarry_radix_descent
    {p Q q : ℕ} (hp : p.Prime) (hq1 : 1 ≤ q) (hqQ : q ≤ Q) :
    barrierCarry p Q q =
      padicValNat p ((Q - 1).choose ((q - 1) / p)) := by
  unfold barrierCarry
  rw [barrier_choose_symm hp.pos hq1 hqQ]
  exact binomial_padic_radix_descent hp hq1 hqQ

/-- The representative carry is exactly the smaller-binomial carry for its
radix-block index. -/
theorem barrierCarry_representative
    {p Q a : ℕ} (hp : p.Prime) (hblock : p * a < Q) :
    barrierCarry p Q (radixRepresentative p Q a) =
      padicValNat p ((Q - 1).choose a) := by
  rw [barrierCarry_radix_descent hp
    (Nat.succ_le_iff.2 (radixRepresentative_pos hp.pos hblock))
    (radixRepresentative_le_Q p Q a)]
  rw [radixRepresentative_quotient hp.pos hblock]

/-- Branch cost is monotone in the correction order when the carry is fixed. -/
theorem branchCost_mono_order
    {h k₁ k₂ carry : ℕ} (hk : k₂ ≤ k₁) :
    branchCost h k₂ carry ≤ branchCost h k₁ carry := by
  unfold branchCost
  exact Nat.add_le_add_right (Nat.mul_le_mul_right (h + 1) hk) carry

/-- Every point in a nonempty radix block lies below its representative. -/
theorem le_radixRepresentative
    {p Q a q : ℕ} (hqQ : q ≤ Q) (hupper : q ≤ p * (a + 1)) :
    q ≤ radixRepresentative p Q a := by
  exact Nat.le_min.2 ⟨hqQ, hupper⟩

/-- The representative minimizes total barrier cost throughout its radix block. -/
theorem barrierBranchCost_representative_min
    {p h Q a q : ℕ} (hp : p.Prime)
    (hblock : p * a < Q)
    (hq1 : 1 ≤ q) (hqQ : q ≤ Q)
    (hlower : p * a < q) (hupper : q ≤ p * (a + 1)) :
    barrierBranchCost p h Q (radixRepresentative p Q a) ≤
      barrierBranchCost p h Q q := by
  have hqrep : q ≤ radixRepresentative p Q a :=
    le_radixRepresentative hqQ hupper
  have hcarry_q : barrierCarry p Q q =
      padicValNat p ((Q - 1).choose a) := by
    rw [barrierCarry_radix_descent hp hq1 hqQ]
    rw [quotient_eq_of_radix_block hp.pos hlower hupper]
  have hcarry_rep := barrierCarry_representative hp hblock
  unfold barrierBranchCost
  rw [hcarry_rep, hcarry_q]
  apply branchCost_mono_order
  exact Nat.sub_le_sub_left hqrep (p * Q)

/-- If any point in a radix block is active, then its representative is active. -/
theorem activeAt_radixRepresentative_of_block
    {p r h Q a q : ℕ} (hp : p.Prime)
    (hblock : p * a < Q)
    (hq1 : 1 ≤ q) (hqQ : q ≤ Q)
    (hlower : p * a < q) (hupper : q ≤ p * (a + 1))
    (hactive : ActiveAt r h (p * Q - q) (barrierCarry p Q q)) :
    ActiveAt r h (p * Q - radixRepresentative p Q a)
      (padicValNat p ((Q - 1).choose a)) := by
  have hcost := barrierBranchCost_representative_min
    (p := p) (h := h) hp hblock hq1 hqQ hlower hupper
  have hrep : ActiveAt r h (p * Q - radixRepresentative p Q a)
      (barrierCarry p Q (radixRepresentative p Q a)) := by
    unfold ActiveAt at hactive ⊢
    unfold barrierBranchCost at hcost
    exact lt_of_le_of_lt hcost hactive
  rw [barrierCarry_representative hp hblock] at hrep
  exact hrep

/-- Nonempty radix blocks are indexed exactly by
`a ≤ (Q-1)/p`. -/
theorem radix_block_nonempty_iff
    {p Q a : ℕ} (hp : 0 < p) (hQ : 0 < Q) :
    p * a < Q ↔ a ≤ (Q - 1) / p := by
  constructor
  · intro h
    apply (Nat.le_div_iff_mul_le hp).2
    have hmul : p * a ≤ Q - 1 := by omega
    simpa [Nat.mul_comm] using hmul
  · intro h
    have hmul : a * p ≤ Q - 1 :=
      (Nat.le_div_iff_mul_le hp).1 h
    have : p * a ≤ Q - 1 := by simpa [Nat.mul_comm] using hmul
    omega

/-- Exact representative compiler for the concrete quotient barrier: one point
per nonempty radix block is sufficient and necessary. -/
theorem binomialPadic_crossesBarrier_iff_radix
    {p r h Q : ℕ} (hp : p.Prime) :
    CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p Q ↔
      ∃ a : ℕ, p * a < Q ∧ radixBarrierCost p h Q a < r := by
  rw [binomialPadic_crossesBarrier_iff hp.one_lt]
  constructor
  · rintro ⟨q, hq1, hqQ, hactive⟩
    let a := (q - 1) / p
    have hmul : a * p ≤ q - 1 :=
      (Nat.le_div_iff_mul_le hp.pos).1 (le_refl a)
    have hlower : p * a < q := by
      have : p * a ≤ q - 1 := by simpa [Nat.mul_comm] using hmul
      omega
    have hdivlt : (q - 1) / p < a + 1 := by
      dsimp [a]
      omega
    have hltmul : q - 1 < (a + 1) * p :=
      (Nat.div_lt_iff_lt_mul hp.pos).1 hdivlt
    have hupper : q ≤ p * (a + 1) := by
      have : q - 1 < p * (a + 1) := by simpa [Nat.mul_comm] using hltmul
      omega
    have hblock : p * a < Q := lt_of_lt_of_le hlower hqQ
    refine ⟨a, hblock, ?_⟩
    have hactive' := activeAt_radixRepresentative_of_block
      hp hblock hq1 hqQ hlower hupper hactive
    simpa [radixBarrierCost, ActiveAt] using hactive'
  · rintro ⟨a, hblock, hcost⟩
    let q := radixRepresentative p Q a
    have hqpos : 0 < q := radixRepresentative_pos hp.pos hblock
    have hq1 : 1 ≤ q := Nat.succ_le_iff.2 hqpos
    have hqQ : q ≤ Q := radixRepresentative_le_Q p Q a
    refine ⟨q, hq1, hqQ, ?_⟩
    change ActiveAt r h (p * Q - q) (barrierCarry p Q q)
    dsimp [q]
    rw [barrierCarry_representative hp hblock]
    simpa [radixBarrierCost, ActiveAt] using hcost

/-- Equivalent bounded-index form of the representative compiler. -/
theorem binomialPadic_crossesBarrier_iff_radix_range
    {p r h Q : ℕ} (hp : p.Prime) (hQ : 0 < Q) :
    CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p Q ↔
      ∃ a : ℕ, a ≤ (Q - 1) / p ∧ radixBarrierCost p h Q a < r := by
  rw [binomialPadic_crossesBarrier_iff_radix hp]
  constructor
  · rintro ⟨a, ha, hcost⟩
    exact ⟨a, (radix_block_nonempty_iff hp.pos hQ).1 ha, hcost⟩
  · rintro ⟨a, ha, hcost⟩
    exact ⟨a, (radix_block_nonempty_iff hp.pos hQ).2 ha, hcost⟩

end KomorebiPadic
