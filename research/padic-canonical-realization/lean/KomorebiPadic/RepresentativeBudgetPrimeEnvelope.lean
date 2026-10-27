import KomorebiPadic.RepresentativeBudgetClosedForm

/-!
# Prime-sensitive triangular envelope for the representative budget

Block 10 proved the exact all-natural formula

`R(p,B) = B + p*d*(d-1)/2 + d*(s+1)`

with `d = (B-1)/p` and `s = (B-1)%p`.  At positive base, `s+1 ≤ p`, so the
partial terminal block can be replaced by one full block.  This module proves
both the resulting simplified envelope

`R(p,B) ≤ B + p*d*(d+1)/2`

and the exact slack

`d * (p - (s+1))`.

The simplified bound is additional evidence.  It does not replace the exact
closed formula or any executable counter.
-/

namespace KomorebiPadic

/-- At positive base, the final radix-block remainder plus one is at most the
base. -/
theorem lastRadixBlockRemainder_succ_le_base
    {p B : ℕ} (hp : 0 < p) :
    lastRadixBlockRemainder p B + 1 ≤ p := by
  unfold lastRadixBlockRemainder
  exact Nat.succ_le_of_lt (Nat.mod_lt _ hp)

/-- Triangular full-block envelope for the representative budget. -/
def radixRepresentativeBudgetPrimeEnvelope (p B : ℕ) : ℕ :=
  let d := lastRadixBlockQuotient p B
  B + (p * d * (d + 1)) / 2

/-- Exact slack between the triangular envelope and the representative budget. -/
def radixRepresentativeBudgetPrimeEnvelopeGap (p B : ℕ) : ℕ :=
  let d := lastRadixBlockQuotient p B
  let s := lastRadixBlockRemainder p B
  d * (p - (s + 1))

/-- Binomial-coefficient form of the triangular envelope. -/
theorem radixRepresentativeBudgetPrimeEnvelope_eq_choose
    (p B : ℕ) :
    radixRepresentativeBudgetPrimeEnvelope p B =
      B + p * (lastRadixBlockQuotient p B + 1).choose 2 := by
  unfold radixRepresentativeBudgetPrimeEnvelope
  dsimp
  let d := lastRadixBlockQuotient p B
  change B + (p * d * (d + 1)) / 2 =
    B + p * (d + 1).choose 2
  rw [Nat.choose_two_right, Nat.add_sub_cancel]
  rw [Nat.mul_comm (d + 1) d]
  have hdvd : 2 ∣ d * (d + 1) := Nat.two_dvd_mul_add_one d
  rw [Nat.mul_assoc p d (d + 1)]
  rw [Nat.mul_div_assoc p hdvd]

/-- At positive base, the triangular envelope is the exact budget plus the
explicit terminal-block slack. -/
theorem radixRepresentativeBudget_add_gap_eq_primeEnvelope
    {p B : ℕ} (hp : 0 < p) :
    radixRepresentativeBudget p B +
        radixRepresentativeBudgetPrimeEnvelopeGap p B =
      radixRepresentativeBudgetPrimeEnvelope p B := by
  rw [radixRepresentativeBudget_eq_lastBlockForm]
  rw [radixRepresentativeBudgetPrimeEnvelope_eq_choose]
  unfold radixRepresentativeBudgetLastBlockForm
  unfold radixRepresentativeBudgetPrimeEnvelopeGap
  dsimp
  let d := lastRadixBlockQuotient p B
  let s := lastRadixBlockRemainder p B
  change (B + p * d.choose 2 + d * (s + 1)) +
      d * (p - (s + 1)) = B + p * (d + 1).choose 2
  have hs : s + 1 ≤ p := by
    dsimp [s]
    exact lastRadixBlockRemainder_succ_le_base hp
  have hsplit : d * (s + 1) + d * (p - (s + 1)) = d * p := by
    rw [← Nat.mul_add, Nat.add_sub_of_le hs]
  have hchoose : (d + 1).choose 2 = d.choose 2 + d := by
    simpa [Nat.add_comm] using Nat.choose_succ_succ d 1
  calc
    (B + p * d.choose 2 + d * (s + 1)) + d * (p - (s + 1)) =
        B + p * d.choose 2 + (d * (s + 1) + d * (p - (s + 1))) := by ring
    _ = B + p * d.choose 2 + d * p := by rw [hsplit]
    _ = B + p * (d.choose 2 + d) := by ring
    _ = B + p * (d + 1).choose 2 := by rw [hchoose]

/-- The exact representative budget lies below the triangular positive-base
envelope. -/
theorem radixRepresentativeBudget_le_primeEnvelope
    {p B : ℕ} (hp : 0 < p) :
    radixRepresentativeBudget p B ≤
      radixRepresentativeBudgetPrimeEnvelope p B := by
  have h := radixRepresentativeBudget_add_gap_eq_primeEnvelope
    (p := p) (B := B) hp
  omega

/-- Definition-free form of the positive-base representative envelope. -/
theorem radixRepresentativeBudget_le_primeEnvelope_explicit
    {p B : ℕ} (hp : 0 < p) :
    radixRepresentativeBudget p B ≤
      let d := (B - 1) / p
      B + (p * d * (d + 1)) / 2 := by
  simpa [radixRepresentativeBudgetPrimeEnvelope,
    lastRadixBlockQuotient] using
    radixRepresentativeBudget_le_primeEnvelope (p := p) (B := B) hp

/-- The triangular envelope is exact precisely in the first block or at a full
terminal radix block. -/
theorem radixRepresentativeBudget_eq_primeEnvelope_iff
    {p B : ℕ} (hp : 0 < p) :
    radixRepresentativeBudget p B =
        radixRepresentativeBudgetPrimeEnvelope p B ↔
      lastRadixBlockQuotient p B = 0 ∨
        lastRadixBlockRemainder p B + 1 = p := by
  have hs := lastRadixBlockRemainder_succ_le_base (p := p) (B := B) hp
  have hdecomp := radixRepresentativeBudget_add_gap_eq_primeEnvelope
    (p := p) (B := B) hp
  constructor
  · intro heq
    have hgap0 : radixRepresentativeBudgetPrimeEnvelopeGap p B = 0 := by
      omega
    unfold radixRepresentativeBudgetPrimeEnvelopeGap at hgap0
    dsimp at hgap0
    rw [Nat.mul_eq_zero] at hgap0
    rcases hgap0 with hd | hsub
    · exact Or.inl hd
    · right
      exact Nat.le_antisymm hs (Nat.sub_eq_zero_iff_le.mp hsub)
  · intro hcase
    have hgap0 : radixRepresentativeBudgetPrimeEnvelopeGap p B = 0 := by
      unfold radixRepresentativeBudgetPrimeEnvelopeGap
      dsimp
      rcases hcase with hd | hsfull
      · simp [hd]
      · simp [hsfull]
    omega

/-- The triangular representative envelope lies below the quadratic
representative envelope from Block 09.  This statement is total over all
natural bases. -/
theorem radixRepresentativeBudgetPrimeEnvelope_le_sq
    {p B : ℕ} :
    radixRepresentativeBudgetPrimeEnvelope p B ≤ B * B := by
  unfold radixRepresentativeBudgetPrimeEnvelope
  dsimp
  let d := lastRadixBlockQuotient p B
  change B + (p * d * (d + 1)) / 2 ≤ B * B
  by_cases hB0 : B = 0
  · subst B
    simp [d, lastRadixBlockQuotient]
  have hB : 0 < B := Nat.pos_of_ne_zero hB0
  have hpd : p * d ≤ B - 1 := by
    dsimp [d, lastRadixBlockQuotient]
    exact Nat.mul_div_le (B - 1) p
  have hd : d ≤ B - 1 := by
    dsimp [d, lastRadixBlockQuotient]
    exact Nat.div_le_self (B - 1) p
  have hd1 : d + 1 ≤ B := by omega
  have hprod : p * d * (d + 1) ≤ (B - 1) * B :=
    Nat.mul_le_mul hpd hd1
  have hdiv : (p * d * (d + 1)) / 2 ≤ p * d * (d + 1) :=
    Nat.div_le_self _ 2
  have hterm : (p * d * (d + 1)) / 2 ≤ (B - 1) * B :=
    hdiv.trans hprod
  have hBform : B = (B - 1) + 1 := by omega
  calc
    B + (p * d * (d + 1)) / 2 ≤ B + (B - 1) * B :=
      Nat.add_le_add_left hterm B
    _ = ((B - 1) + 1) * B := by ring
    _ = B * B := by rw [← hBform]

/-- Simplified compiler envelope obtained by replacing the exact terminal
remainder contribution by one full radix block. -/
def maximumLayerCompilerPrimeEnvelopeBound (p r h : ℕ) : ℕ :=
  let B := quotientSearchBound p r h
  let d := lastRadixBlockQuotient p B
  2 * B + p + (p * d * (d + 1)) / 2

/-- Exact slack between the closed Block 10 compiler envelope and the simplified
prime-sensitive compiler envelope. -/
def maximumLayerCompilerPrimeEnvelopeGap (p r h : ℕ) : ℕ :=
  radixRepresentativeBudgetPrimeEnvelopeGap p (quotientSearchBound p r h)

/-- The simplified compiler envelope is the closed Block 10 envelope plus the
exact terminal-block slack. -/
theorem maximumLayerCompilerClosedBudgetBound_add_gap_eq_primeEnvelopeBound
    {p r h : ℕ} (hp : 0 < p) :
    maximumLayerCompilerClosedBudgetBound p r h +
        maximumLayerCompilerPrimeEnvelopeGap p r h =
      maximumLayerCompilerPrimeEnvelopeBound p r h := by
  rw [← maximumLayerCompilerBudgetBound_eq_closedBudgetBound]
  unfold maximumLayerCompilerBudgetBound
  unfold maximumLayerCompilerPrimeEnvelopeBound
  unfold maximumLayerCompilerPrimeEnvelopeGap
  dsimp
  have hgap := radixRepresentativeBudget_add_gap_eq_primeEnvelope
    (p := p) (B := quotientSearchBound p r h) hp
  unfold radixRepresentativeBudgetPrimeEnvelope at hgap
  dsimp at hgap
  omega

/-- The exact Block 10 closed envelope lies below the simplified positive-base
envelope. -/
theorem maximumLayerCompilerClosedBudgetBound_le_primeEnvelopeBound
    {p r h : ℕ} (hp : 0 < p) :
    maximumLayerCompilerClosedBudgetBound p r h ≤
      maximumLayerCompilerPrimeEnvelopeBound p r h := by
  have h := maximumLayerCompilerClosedBudgetBound_add_gap_eq_primeEnvelopeBound
    (p := p) (r := r) (h := h) hp
  omega

/-- The finite-sum Block 09 envelope also lies below the simplified envelope. -/
theorem maximumLayerCompilerBudgetBound_le_primeEnvelopeBound
    {p r h : ℕ} (hp : 0 < p) :
    maximumLayerCompilerBudgetBound p r h ≤
      maximumLayerCompilerPrimeEnvelopeBound p r h := by
  rw [maximumLayerCompilerBudgetBound_eq_closedBudgetBound]
  exact maximumLayerCompilerClosedBudgetBound_le_primeEnvelopeBound hp

/-- Exact compiler work is bounded by the simplified prime-sensitive envelope. -/
theorem maximumLayerCompilerTotalTests_le_primeEnvelopeBound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerPrimeEnvelopeBound p r h :=
  (maximumLayerCompilerTotalTests_le_closedBudgetBound hp hr).trans
    (maximumLayerCompilerClosedBudgetBound_le_primeEnvelopeBound hp.pos)

/-- Definition-free form of the simplified total compiler envelope. -/
theorem maximumLayerCompilerTotalTests_le_primeEnvelopeBound_explicit
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      let B := quotientSearchBound p r h
      let d := (B - 1) / p
      2 * B + p + (p * d * (d + 1)) / 2 := by
  simpa [maximumLayerCompilerPrimeEnvelopeBound,
    lastRadixBlockQuotient] using
    maximumLayerCompilerTotalTests_le_primeEnvelopeBound hp hr

/-- The simplified compiler envelope refines the earlier quadratic envelope. -/
theorem maximumLayerCompilerPrimeEnvelopeBound_le_testBound
    {p r h : ℕ} :
    maximumLayerCompilerPrimeEnvelopeBound p r h ≤
      maximumLayerCompilerTestBound p r h := by
  have hrep := radixRepresentativeBudgetPrimeEnvelope_le_sq
    (p := p) (B := quotientSearchBound p r h)
  unfold maximumLayerCompilerPrimeEnvelopeBound maximumLayerCompilerTestBound
  unfold radixRepresentativeBudgetPrimeEnvelope at hrep
  dsimp at hrep ⊢
  omega

/-- Proof-carrying simplified-envelope certificate.  It retains the exact
Block 10 closed-form certificate, the exact slack, the simplified bound, and
its refinement relationship to the older quadratic bound. -/
structure MaximumLayerCompilerPrimeEnvelopeCertificate (p r h : ℕ) where
  closedForm : MaximumLayerCompilerClosedFormCertificate p r h
  bound : ℕ
  gap : ℕ
  bound_exact : bound = maximumLayerCompilerPrimeEnvelopeBound p r h
  gap_exact : gap = maximumLayerCompilerPrimeEnvelopeGap p r h
  terminalRemainder_cap :
    lastRadixBlockRemainder p (quotientSearchBound p r h) + 1 ≤ p
  representativeBudget_le :
    radixRepresentativeBudget p (quotientSearchBound p r h) ≤
      radixRepresentativeBudgetPrimeEnvelope p (quotientSearchBound p r h)
  closed_plus_gap_exact :
    maximumLayerCompilerClosedBudgetBound p r h + gap = bound
  totalTests_le : maximumLayerCompilerTotalTests p r h ≤ bound
  bound_le_quadratic : bound ≤ maximumLayerCompilerTestBound p r h

/-- Construct the proof-carrying simplified-envelope certificate. -/
def maximumLayerCompilerPrimeEnvelopeCertificate
    (p r h : ℕ) (hp : p.Prime) (hr : 0 < r) :
    MaximumLayerCompilerPrimeEnvelopeCertificate p r h where
  closedForm := maximumLayerCompilerClosedFormCertificate p r h hp hr
  bound := maximumLayerCompilerPrimeEnvelopeBound p r h
  gap := maximumLayerCompilerPrimeEnvelopeGap p r h
  bound_exact := rfl
  gap_exact := rfl
  terminalRemainder_cap :=
    lastRadixBlockRemainder_succ_le_base hp.pos
  representativeBudget_le :=
    radixRepresentativeBudget_le_primeEnvelope hp.pos
  closed_plus_gap_exact :=
    maximumLayerCompilerClosedBudgetBound_add_gap_eq_primeEnvelopeBound hp.pos
  totalTests_le := maximumLayerCompilerTotalTests_le_primeEnvelopeBound hp hr
  bound_le_quadratic := maximumLayerCompilerPrimeEnvelopeBound_le_testBound

end KomorebiPadic
