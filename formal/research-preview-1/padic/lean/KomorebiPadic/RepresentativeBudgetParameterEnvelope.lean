import KomorebiPadic.RepresentativeBudgetPrimeEnvelope

/-!
# Parameter-only compiler envelope

The Block 11 compiler bound is written using two auxiliary quantities:

* `B = quotientSearchBound p r h`, and
* `d = (B - 1) / p`.

This module eliminates both auxiliaries.  Under Lean's totalized natural-number
arithmetic, the elimination is exact for every natural base, including `p = 0`
and `p = 1`:

`d = coarseK r h / (p * (p - 1))`.

The resulting displayed bound depends directly on `p`, `r`, and `h`.  A second
monotonicity theorem replaces `coarseK r h` by `r - 1`, yielding an `h`-free
precision envelope.  Neither envelope replaces the executable counters.
-/

namespace KomorebiPadic

/-- The radix depth obtained directly from the visible correction-order bound. -/
def coarseRadixDepth (p r h : ℕ) : ℕ :=
  coarseK r h / (p * (p - 1))

/-- The search bound minus one is exactly the quotient of `coarseK` by `p - 1`.
This is total over all natural bases. -/
theorem quotientSearchBound_sub_one (p r h : ℕ) :
    quotientSearchBound p r h - 1 = coarseK r h / (p - 1) := by
  simp [quotientSearchBound]

/-- Exact elimination of the auxiliary final-block quotient.  The statement is
valid even at the totalized bases `p = 0` and `p = 1`. -/
theorem lastRadixBlockQuotient_at_searchBound
    (p r h : ℕ) :
    lastRadixBlockQuotient p (quotientSearchBound p r h) =
      coarseRadixDepth p r h := by
  unfold lastRadixBlockQuotient coarseRadixDepth
  rw [quotientSearchBound_sub_one]
  rw [Nat.div_div_eq_div_mul]
  rw [Nat.mul_comm (p - 1) p]

/-- Definition-free form of the exact auxiliary-index elimination. -/
theorem lastRadixBlockQuotient_at_searchBound_explicit
    (p r h : ℕ) :
    lastRadixBlockQuotient p (quotientSearchBound p r h) =
      coarseK r h / (p * (p - 1)) := by
  simpa [coarseRadixDepth] using
    lastRadixBlockQuotient_at_searchBound p r h

/-- The proposed Block 12 depth inequality holds with equality. -/
theorem lastRadixBlockQuotient_at_searchBound_le
    (p r h : ℕ) :
    lastRadixBlockQuotient p (quotientSearchBound p r h) ≤
      coarseK r h / (p * (p - 1)) := by
  exact (lastRadixBlockQuotient_at_searchBound_explicit p r h).le

@[simp] theorem coarseRadixDepth_zero_base (r h : ℕ) :
    coarseRadixDepth 0 r h = 0 := by
  simp [coarseRadixDepth]

@[simp] theorem coarseRadixDepth_one_base (r h : ℕ) :
    coarseRadixDepth 1 r h = 0 := by
  simp [coarseRadixDepth]

/-- Core triangular envelope as a monotone function of a visible-order cap `K`. -/
def compilerEnvelopeFromCoarseK (p K : ℕ) : ℕ :=
  let d := K / (p * (p - 1))
  2 * (K / (p - 1) + 1) + p + (p * d * (d + 1)) / 2

/-- Direct `(p,r,h)` envelope obtained by substituting `coarseK` for both
auxiliary quantities in the Block 11 bound. -/
def maximumLayerCompilerParameterEnvelopeBound (p r h : ℕ) : ℕ :=
  compilerEnvelopeFromCoarseK p (coarseK r h)

/-- An `h`-free precision envelope obtained by replacing `coarseK r h` with its
universal upper bound `r - 1`. -/
def maximumLayerCompilerRawPrecisionBound (p r : ℕ) : ℕ :=
  compilerEnvelopeFromCoarseK p (r - 1)

/-- The Block 11 prime envelope is exactly the direct parameter envelope. -/
theorem maximumLayerCompilerPrimeEnvelopeBound_eq_parameterEnvelopeBound
    (p r h : ℕ) :
    maximumLayerCompilerPrimeEnvelopeBound p r h =
      maximumLayerCompilerParameterEnvelopeBound p r h := by
  unfold maximumLayerCompilerPrimeEnvelopeBound
  unfold maximumLayerCompilerParameterEnvelopeBound
  unfold compilerEnvelopeFromCoarseK
  dsimp
  rw [lastRadixBlockQuotient_at_searchBound_explicit]
  rfl

/-- The core parameter envelope is monotone in the visible-order cap. -/
theorem compilerEnvelopeFromCoarseK_mono
    {p K₁ K₂ : ℕ} (hK : K₁ ≤ K₂) :
    compilerEnvelopeFromCoarseK p K₁ ≤
      compilerEnvelopeFromCoarseK p K₂ := by
  unfold compilerEnvelopeFromCoarseK
  dsimp
  let q₁ := K₁ / (p - 1)
  let q₂ := K₂ / (p - 1)
  let d₁ := K₁ / (p * (p - 1))
  let d₂ := K₂ / (p * (p - 1))
  have hq : q₁ ≤ q₂ := by
    dsimp [q₁, q₂]
    exact Nat.div_le_div_right hK
  have hd : d₁ ≤ d₂ := by
    dsimp [d₁, d₂]
    exact Nat.div_le_div_right hK
  have hd1 : d₁ + 1 ≤ d₂ + 1 := Nat.add_le_add_right hd 1
  have hpd : p * d₁ ≤ p * d₂ := Nat.mul_le_mul_left p hd
  have hprod : p * d₁ * (d₁ + 1) ≤ p * d₂ * (d₂ + 1) :=
    Nat.mul_le_mul hpd hd1
  have hhalf : (p * d₁ * (d₁ + 1)) / 2 ≤
      (p * d₂ * (d₂ + 1)) / 2 := Nat.div_le_div_right hprod
  dsimp [q₁, q₂, d₁, d₂] at hq hd hhalf ⊢
  omega

/-- The visible-order cap never exceeds the raw precision cap. -/
theorem coarseK_le_precision_sub_one (r h : ℕ) :
    coarseK r h ≤ r - 1 := by
  unfold coarseK
  exact Nat.div_le_self (r - 1) (h + 1)

/-- The exact parameter envelope lies below the `h`-free precision envelope. -/
theorem maximumLayerCompilerParameterEnvelopeBound_le_rawPrecisionBound
    (p r h : ℕ) :
    maximumLayerCompilerParameterEnvelopeBound p r h ≤
      maximumLayerCompilerRawPrecisionBound p r := by
  unfold maximumLayerCompilerParameterEnvelopeBound
  unfold maximumLayerCompilerRawPrecisionBound
  exact compilerEnvelopeFromCoarseK_mono (coarseK_le_precision_sub_one r h)

/-- Exact compiler work is bounded directly by the `(p,r,h)` envelope. -/
theorem maximumLayerCompilerTotalTests_le_parameterEnvelopeBound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p r h := by
  rw [← maximumLayerCompilerPrimeEnvelopeBound_eq_parameterEnvelopeBound]
  exact maximumLayerCompilerTotalTests_le_primeEnvelopeBound hp hr

/-- Fully expanded `(p,r,h)` form of the direct compiler envelope. -/
theorem maximumLayerCompilerTotalTests_le_parameterEnvelopeBound_explicit
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      let K := (r - 1) / (h + 1)
      let d := K / (p * (p - 1))
      2 * (K / (p - 1) + 1) + p + (p * d * (d + 1)) / 2 := by
  simpa [maximumLayerCompilerParameterEnvelopeBound,
    compilerEnvelopeFromCoarseK, coarseK] using
    maximumLayerCompilerTotalTests_le_parameterEnvelopeBound hp hr

/-- Exact compiler work is also bounded by the `h`-free raw-precision envelope. -/
theorem maximumLayerCompilerTotalTests_le_rawPrecisionBound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerRawPrecisionBound p r :=
  (maximumLayerCompilerTotalTests_le_parameterEnvelopeBound hp hr).trans
    (maximumLayerCompilerParameterEnvelopeBound_le_rawPrecisionBound p r h)

/-- Fully expanded `h`-free form of the raw-precision compiler envelope. -/
theorem maximumLayerCompilerTotalTests_le_rawPrecisionBound_explicit
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      let K := r - 1
      let d := K / (p * (p - 1))
      2 * (K / (p - 1) + 1) + p + (p * d * (d + 1)) / 2 := by
  simpa [maximumLayerCompilerRawPrecisionBound,
    compilerEnvelopeFromCoarseK] using
    maximumLayerCompilerTotalTests_le_rawPrecisionBound hp hr

/-- Proof-carrying parameter-envelope certificate.  It retains the complete
Block 11 certificate and records the exact elimination of `B` and `d`. -/
structure MaximumLayerCompilerParameterEnvelopeCertificate (p r h : ℕ) where
  primeEnvelope : MaximumLayerCompilerPrimeEnvelopeCertificate p r h
  coarseOrder : ℕ
  radixDepth : ℕ
  bound : ℕ
  rawPrecisionBound : ℕ
  coarseOrder_exact : coarseOrder = coarseK r h
  radixDepth_exact : radixDepth = coarseK r h / (p * (p - 1))
  searchBound_exact : quotientSearchBound p r h = coarseOrder / (p - 1) + 1
  finalBlockQuotient_exact :
    lastRadixBlockQuotient p (quotientSearchBound p r h) = radixDepth
  bound_exact : bound = maximumLayerCompilerParameterEnvelopeBound p r h
  primeEnvelope_exact : maximumLayerCompilerPrimeEnvelopeBound p r h = bound
  rawPrecisionBound_exact : rawPrecisionBound = maximumLayerCompilerRawPrecisionBound p r
  totalTests_le : maximumLayerCompilerTotalTests p r h ≤ bound
  bound_le_rawPrecision : bound ≤ rawPrecisionBound

/-- Construct the proof-carrying parameter-envelope certificate. -/
def maximumLayerCompilerParameterEnvelopeCertificate
    (p r h : ℕ) (hp : p.Prime) (hr : 0 < r) :
    MaximumLayerCompilerParameterEnvelopeCertificate p r h where
  primeEnvelope := maximumLayerCompilerPrimeEnvelopeCertificate p r h hp hr
  coarseOrder := coarseK r h
  radixDepth := coarseRadixDepth p r h
  bound := maximumLayerCompilerParameterEnvelopeBound p r h
  rawPrecisionBound := maximumLayerCompilerRawPrecisionBound p r
  coarseOrder_exact := rfl
  radixDepth_exact := rfl
  searchBound_exact := rfl
  finalBlockQuotient_exact := lastRadixBlockQuotient_at_searchBound p r h
  bound_exact := rfl
  primeEnvelope_exact :=
    maximumLayerCompilerPrimeEnvelopeBound_eq_parameterEnvelopeBound p r h
  rawPrecisionBound_exact := rfl
  totalTests_le := maximumLayerCompilerTotalTests_le_parameterEnvelopeBound hp hr
  bound_le_rawPrecision :=
    maximumLayerCompilerParameterEnvelopeBound_le_rawPrecisionBound p r h

end KomorebiPadic
