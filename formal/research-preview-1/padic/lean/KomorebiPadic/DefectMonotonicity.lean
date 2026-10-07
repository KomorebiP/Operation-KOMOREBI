import KomorebiPadic.RepresentativeBudgetParameterEnvelope

/-!
# Defect monotonicity and attained envelope extrema

Increasing the defect valuation deletes active edges. It therefore weakly decreases
both the first noncrossing quotient and the exact maximum layer. The certified
parameter envelope is likewise antitone, attains its largest value at defect zero,
and stabilizes at `p + 2` when `h ≥ r - 1`.

These are statements about graph outputs and certified envelopes, not a claim
that the adaptive compiler's exact total work is antitone.
-/

namespace KomorebiPadic

/-- Increasing defect weakly increases every branch cost. -/
theorem branchCost_mono_defect {h₁ h₂ k carry : ℕ} (hh : h₁ ≤ h₂) :
    branchCost h₁ k carry ≤ branchCost h₂ k carry := by
  unfold branchCost
  exact Nat.add_le_add_right
    (Nat.mul_le_mul_left k (Nat.add_le_add_right hh 1)) carry

/-- Increasing defect can only delete active branches. -/
theorem activeAt_antitone_defect {r h₁ h₂ k carry : ℕ} (hh : h₁ ≤ h₂)
    (ha : ActiveAt r h₂ k carry) : ActiveAt r h₁ k carry := by
  exact Nat.lt_of_le_of_lt (branchCost_mono_defect hh) ha

/-- Defect monotonicity of the coarse correction-order cap, including `r = 0`. -/
theorem coarseK_antitone_defect {r h₁ h₂ : ℕ} (hh : h₁ ≤ h₂) :
    coarseK r h₂ ≤ coarseK r h₁ := by
  unfold coarseK
  exact Nat.div_le_div_left (Nat.add_le_add_right hh 1) (Nat.succ_pos h₁)

/-- At zero defect the coarse cap is exactly the raw precision cap. -/
@[simp] theorem coarseK_zero_defect (r : ℕ) : coarseK r 0 = r - 1 := by
  simp [coarseK]

/-- Exact saturation threshold for the visible correction-order cap. -/
theorem coarseK_eq_zero_iff_defect (r h : ℕ) :
    coarseK r h = 0 ↔ r - 1 ≤ h := by
  unfold coarseK
  rw [Nat.div_eq_zero_iff]
  omega

/-- The finite quotient-search bound is antitone in defect at every natural base. -/
theorem quotientSearchBound_antitone_defect {p r h₁ h₂ : ℕ} (hh : h₁ ≤ h₂) :
    quotientSearchBound p r h₂ ≤ quotientSearchBound p r h₁ := by
  unfold quotientSearchBound
  exact Nat.add_le_add_right (Nat.div_le_div_right (coarseK_antitone_defect hh)) 1

/-- The direct radix depth is antitone in defect, also at totalized bases 0 and 1. -/
theorem coarseRadixDepth_antitone_defect {p r h₁ h₂ : ℕ} (hh : h₁ ≤ h₂) :
    coarseRadixDepth p r h₂ ≤ coarseRadixDepth p r h₁ := by
  unfold coarseRadixDepth
  exact Nat.div_le_div_right (coarseK_antitone_defect hh)

/-- The certified parameter envelope is antitone in defect for all natural inputs. -/
theorem maximumLayerCompilerParameterEnvelopeBound_antitone_defect
    {p r h₁ h₂ : ℕ} (hh : h₁ ≤ h₂) :
    maximumLayerCompilerParameterEnvelopeBound p r h₂ ≤
      maximumLayerCompilerParameterEnvelopeBound p r h₁ := by
  exact compilerEnvelopeFromCoarseK_mono (coarseK_antitone_defect hh)

/-- The raw-precision bound is attained by the zero-defect envelope. -/
theorem maximumLayerCompilerParameterEnvelopeBound_zero_defect (p r : ℕ) :
    maximumLayerCompilerParameterEnvelopeBound p r 0 =
      maximumLayerCompilerRawPrecisionBound p r := by
  simp [maximumLayerCompilerParameterEnvelopeBound,
    maximumLayerCompilerRawPrecisionBound]

/-- The raw-precision envelope is the attained maximum of the entire defect family. -/
theorem maximumLayerCompilerParameterEnvelopeBound_worst_defect (p r : ℕ) :
    (∀ h : ℕ, maximumLayerCompilerParameterEnvelopeBound p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p r 0) ∧
    maximumLayerCompilerParameterEnvelopeBound p r 0 =
      maximumLayerCompilerRawPrecisionBound p r := by
  exact ⟨fun h => maximumLayerCompilerParameterEnvelopeBound_antitone_defect
    (Nat.zero_le h), maximumLayerCompilerParameterEnvelopeBound_zero_defect p r⟩

/-- Once all positive correction orders are excluded, the envelope is constant. -/
theorem maximumLayerCompilerParameterEnvelopeBound_saturated
    {p r h : ℕ} (hh : r - 1 ≤ h) :
    maximumLayerCompilerParameterEnvelopeBound p r h = p + 2 := by
  have hK := (coarseK_eq_zero_iff_defect r h).2 hh
  simp [maximumLayerCompilerParameterEnvelopeBound, hK,
    compilerEnvelopeFromCoarseK, Nat.add_comm]

/-- A universal lower bound on the envelope, not on actual runtime. -/
theorem maximumLayerCompilerParameterEnvelopeBound_lower (p r h : ℕ) :
    p + 2 ≤ maximumLayerCompilerParameterEnvelopeBound p r h := by
  have h := compilerEnvelopeFromCoarseK_mono
    (p := p) (Nat.zero_le (coarseK r h))
  simpa [compilerEnvelopeFromCoarseK, maximumLayerCompilerParameterEnvelopeBound,
    Nat.add_comm] using h

/-- The minimum envelope is attained at defect `r - 1`. -/
theorem maximumLayerCompilerParameterEnvelopeBound_best_defect (p r : ℕ) :
    maximumLayerCompilerParameterEnvelopeBound p r (r - 1) = p + 2 ∧
    ∀ h : ℕ, maximumLayerCompilerParameterEnvelopeBound p r (r - 1) ≤
      maximumLayerCompilerParameterEnvelopeBound p r h := by
  have heq := maximumLayerCompilerParameterEnvelopeBound_saturated
    (p := p) (r := r) (h := r - 1) (Nat.le_refl _)
  exact ⟨heq, fun h => heq ▸ maximumLayerCompilerParameterEnvelopeBound_lower p r h⟩

/-- A lower reference defect certifies the work of every higher-defect instance. -/
theorem maximumLayerCompilerTotalTests_le_referenceDefectEnvelope
    {p r h₁ h₂ : ℕ} (hp : p.Prime) (hr : 0 < r) (hh : h₁ ≤ h₂) :
    maximumLayerCompilerTotalTests p r h₂ ≤
      maximumLayerCompilerParameterEnvelopeBound p r h₁ := by
  exact (maximumLayerCompilerTotalTests_le_parameterEnvelopeBound hp hr).trans
    (maximumLayerCompilerParameterEnvelopeBound_antitone_defect hh)

/-- Defect transport applies to every Pascal valuation model. -/
theorem valuationEdge_antitone_defect (V : PascalValuationModel)
    {r h₁ h₂ q k : ℕ} (hh : h₁ ≤ h₂) (he : valuationEdge V r h₂ q k) :
    valuationEdge V r h₁ q k := by
  exact activeAt_antitone_defect hh he

/-- At a fixed quotient interval, higher-defect targets are a subset of lower-defect targets. -/
theorem valuationTarget_antitone_defect (V : PascalValuationModel)
    {r h₁ h₂ Q t : ℕ} (hh : h₁ ≤ h₂)
    (ht : IsTarget (valuationEdgeSystem V r h₂) Q t) :
    IsTarget (valuationEdgeSystem V r h₁) Q t := by
  rcases ht with ⟨q, k, hq, hqQ, he, ht⟩
  exact ⟨q, k, hq, hqQ, valuationEdge_antitone_defect V hh he, ht⟩

/-- Concrete binomial targets inherit defect antitonicity at each fixed quotient. -/
theorem binomialTarget_antitone_defect {p r h₁ h₂ Q t : ℕ}
    (hp : 1 < p) (hh : h₁ ≤ h₂)
    (ht : IsTarget (binomialPadicEdgeSystem p r h₂ hp) Q t) :
    IsTarget (binomialPadicEdgeSystem p r h₁ hp) Q t := by
  exact valuationTarget_antitone_defect (binomialPadicModel p hp) hh ht

/-- Increasing defect can only remove a crossing at a fixed barrier. -/
theorem crossesBarrier_antitone_defect {p r h₁ h₂ Q : ℕ}
    (hp : 1 < p) (hh : h₁ ≤ h₂)
    (hc : CrossesBarrier (binomialPadicEdgeSystem p r h₂ hp) p Q) :
    CrossesBarrier (binomialPadicEdgeSystem p r h₁ hp) p Q := by
  exact binomialTarget_antitone_defect hp hh hc

/-- The actual first noncrossing quotient weakly decreases with increasing defect. -/
theorem stableQuotient_antitone_defect {p r h₁ h₂ : ℕ}
    (hp : p.Prime) (hh : h₁ ≤ h₂) :
    stableQuotient p r h₂ ≤ stableQuotient p r h₁ := by
  by_contra hn
  have hlt : firstNoncrossingQuotient p r h₁ <
      firstNoncrossingQuotient p r h₂ := Nat.lt_of_not_ge hn
  have hc := crossesBarrier_of_lt_firstNoncrossing (r := r) (h := h₂) hp
    (firstNoncrossingQuotient_pos (r := r) (h := h₁) hp) hlt
  exact firstNoncrossingQuotient_not_crosses (r := r) (h := h₁) hp
    (crossesBarrier_antitone_defect hp.one_lt hh hc)

/-- Defect antitonicity of the exact maximum layer, not just of its envelope. -/
theorem exactMaximumLayer_antitone_defect {p r h₁ h₂ : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hh : h₁ ≤ h₂) :
    exactMaximumLayer p r h₂ ≤ exactMaximumLayer p r h₁ := by
  have ht := binomialTarget_antitone_defect hp.one_lt hh
    (exactMaximumLayer_isTarget (h := h₂) hp hr)
  exact isTarget_le_exactMaximumLayer hp
    (isTarget_mono_quotient _ ht (stableQuotient_antitone_defect hp hh))

/-- Quotient-search evaluations are exactly the quotient and are therefore antitone. -/
theorem quotientTestCount_antitone_defect {p r h₁ h₂ : ℕ}
    (hp : p.Prime) (hh : h₁ ≤ h₂) :
    quotientTestCount p r h₂ ≤ quotientTestCount p r h₁ := by
  unfold quotientTestCount
  rw [stableQuotientSearchResult_tested hp, stableQuotientSearchResult_tested hp]
  exact stableQuotient_antitone_defect hp hh

/-- The executable layer shares the exact maximum's defect comparison. -/
theorem maximumLayerCompiler_layer_antitone_defect {p r h₁ h₂ : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hh : h₁ ≤ h₂) :
    (maximumLayerCompiler p r h₂).layer ≤ (maximumLayerCompiler p r h₁).layer := by
  change finalFiberBoundaryLayer p r h₂ ≤ finalFiberBoundaryLayer p r h₁
  rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr,
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr]
  exact exactMaximumLayer_antitone_defect hp hr hh


/-- At saturated defect the quotient search stops at the first quotient. -/
theorem stableQuotient_eq_one_of_saturated_defect {p r h : ℕ}
    (hp : p.Prime) (hh : r - 1 ≤ h) : stableQuotient p r h = 1 := by
  have hK := (coarseK_eq_zero_iff_defect r h).2 hh
  have hbound : quotientSearchBound p r h = 1 := by
    simp [quotientSearchBound, hK]
  have hlo := firstNoncrossingQuotient_pos (p := p) (r := r) (h := h) hp
  have hhi := firstNoncrossingQuotient_le_bound (p := p) (r := r) (h := h) hp
  rw [hbound] at hhi
  change firstNoncrossingQuotient p r h = 1
  omega

/-- At positive precision and saturated defect the only terminal target is 1. -/
theorem exactMaximumLayer_eq_one_of_saturated_defect {p r h : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hh : r - 1 ≤ h) :
    exactMaximumLayer p r h = 1 := by
  have hK := (coarseK_eq_zero_iff_defect r h).2 hh
  have hQ := stableQuotient_eq_one_of_saturated_defect hp hh
  rcases exactMaximumLayer_isTarget (p := p) (r := r) (h := h) hp hr with
    ⟨q, k, hq, hqQ, he, ht⟩
  change ActiveAt r h k (padicValNat p ((q + k - 1).choose k)) at he
  have hk := activeAt_implies_le_coarseK he
  rw [hK] at hk
  rw [hQ] at hqQ
  omega

/-- Exact saturated compiler output, including all three unchanged counters. -/
theorem maximumLayerCompiler_saturated {p r h : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hh : r - 1 ≤ h) :
    maximumLayerCompiler p r h =
      { quotient := 1, layer := 1, quotientTests := 1,
        finalFiberTests := p - 1, barrierRepresentativeTests := 1 } := by
  have hQ := stableQuotient_eq_one_of_saturated_defect hp hh
  have hM := exactMaximumLayer_eq_one_of_saturated_defect hp hr hh
  have hL : finalFiberBoundaryLayer p r h = 1 := by
    rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr, hM]
  have hqt : quotientTestCount p r h = 1 := by
    unfold quotientTestCount
    rw [stableQuotientSearchResult_tested hp]
    exact hQ
  have hf : finalFiberBoundaryTestCount p r h = p - 1 := by
    rw [finalFiberBoundaryTestCount_eq_exactDistance hp hr, hM]
    simp only [finalFiberUpper, stableFiberUpper, hQ, Nat.mul_one]
    have hp2 := hp.two_le
    omega
  have hrep : barrierRepresentativeTestCount p r h = 1 := by
    simp [barrierRepresentativeTestCount, hQ, suffixRadixBarrierResult,
      suffixWindowResult, suffixWindowResultAux]
  simp only [maximumLayerCompiler, hQ, hL, hqt, hf, hrep]

/-- The saturated actual total is `p + 1`, one below the minimum envelope. -/
theorem maximumLayerCompilerTotalTests_saturated {p r h : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hh : r - 1 ≤ h) :
    maximumLayerCompilerTotalTests p r h = p + 1 := by
  unfold maximumLayerCompilerTotalTests
  rw [maximumLayerCompiler_saturated hp hr hh]
  simp only [reportedCompilerTests]
  have hp2 := hp.two_le
  omega

/-- A small kernel-reduced witness that adaptive total work need not decrease. -/
theorem maximumLayerCompilerTotalTests_defect_counterexample :
    maximumLayerCompilerTotalTests 3 2 0 = 3 ∧
      maximumLayerCompilerTotalTests 3 2 1 = 4 := by
  decide +kernel

/-- Envelope and layer antitonicity do not imply antitonicity of actual work. -/
theorem maximumLayerCompilerTotalTests_not_antitone :
    ¬ Antitone (maximumLayerCompilerTotalTests 3 2) := by
  intro ha
  have hbad := ha (by decide : 0 ≤ 1)
  have hw := maximumLayerCompilerTotalTests_defect_counterexample
  omega

/-- Proof-carrying comparison with a lower reference defect. This retains the
complete Block 12 certificate for the higher-defect compiler instance. -/
structure MaximumLayerCompilerDefectCertificate (p r h₁ h₂ : ℕ) where
  parameterEnvelope : MaximumLayerCompilerParameterEnvelopeCertificate p r h₂
  defect_le : h₁ ≤ h₂
  coarseOrder_le : coarseK r h₂ ≤ coarseK r h₁
  envelope_le : maximumLayerCompilerParameterEnvelopeBound p r h₂ ≤
    maximumLayerCompilerParameterEnvelopeBound p r h₁
  worst_case_attained : maximumLayerCompilerParameterEnvelopeBound p r 0 =
    maximumLayerCompilerRawPrecisionBound p r
  minimum_attained : maximumLayerCompilerParameterEnvelopeBound p r (r - 1) = p + 2
  quotient_le : stableQuotient p r h₂ ≤ stableQuotient p r h₁
  layer_le : exactMaximumLayer p r h₂ ≤ exactMaximumLayer p r h₁
  quotientTests_le : quotientTestCount p r h₂ ≤ quotientTestCount p r h₁
  totalTests_le_reference : maximumLayerCompilerTotalTests p r h₂ ≤
    maximumLayerCompilerParameterEnvelopeBound p r h₁

/-- Construct a defect comparison certificate without altering any executable counter. -/
def maximumLayerCompilerDefectCertificate (p r h₁ h₂ : ℕ)
    (hp : p.Prime) (hr : 0 < r) (hh : h₁ ≤ h₂) :
    MaximumLayerCompilerDefectCertificate p r h₁ h₂ where
  parameterEnvelope := maximumLayerCompilerParameterEnvelopeCertificate p r h₂ hp hr
  defect_le := hh
  coarseOrder_le := coarseK_antitone_defect hh
  envelope_le := maximumLayerCompilerParameterEnvelopeBound_antitone_defect hh
  worst_case_attained := maximumLayerCompilerParameterEnvelopeBound_zero_defect p r
  minimum_attained := (maximumLayerCompilerParameterEnvelopeBound_best_defect p r).1
  quotient_le := stableQuotient_antitone_defect hp hh
  layer_le := exactMaximumLayer_antitone_defect hp hr hh
  quotientTests_le := quotientTestCount_antitone_defect hp hh
  totalTests_le_reference := maximumLayerCompilerTotalTests_le_referenceDefectEnvelope hp hr hh

end KomorebiPadic
