import KomorebiPadic.DefectMonotonicity

/-!
# Precision monotonicity and uniform parameter rectangles

Higher precision admits every previously active edge. Together with defect
antitonicity, this orders exact outputs and envelopes on parameter rectangles.
The envelope's adverse corner bounds reported work everywhere, even though
reported work itself is not monotone. At fixed defect and stable quotient,
the reported total plus the maximum layer is exactly conserved.
-/

namespace KomorebiPadic

/-- Raising precision cannot remove an active branch. -/
theorem activeAt_mono_precision {r₁ r₂ h k carry : ℕ} (hr : r₁ ≤ r₂)
    (ha : ActiveAt r₁ h k carry) : ActiveAt r₂ h k carry := by
  exact Nat.lt_of_lt_of_le ha hr

/-- Coarse correction-order monotonicity includes the totalized precision zero. -/
theorem coarseK_mono_precision {r₁ r₂ h : ℕ} (hr : r₁ ≤ r₂) :
    coarseK r₁ h ≤ coarseK r₂ h := by
  exact Nat.div_le_div_right (Nat.sub_le_sub_right hr 1)

/-- Precision monotonicity of the finite quotient-search bound at every base. -/
theorem quotientSearchBound_mono_precision {p r₁ r₂ h : ℕ} (hr : r₁ ≤ r₂) :
    quotientSearchBound p r₁ h ≤ quotientSearchBound p r₂ h := by
  exact Nat.add_le_add_right (Nat.div_le_div_right (coarseK_mono_precision hr)) 1

/-- Precision monotonicity of the direct radix depth at every natural base. -/
theorem coarseRadixDepth_mono_precision {p r₁ r₂ h : ℕ} (hr : r₁ ≤ r₂) :
    coarseRadixDepth p r₁ h ≤ coarseRadixDepth p r₂ h := by
  exact Nat.div_le_div_right (coarseK_mono_precision hr)

/-- The parameter envelope is monotone in precision for all natural inputs. -/
theorem maximumLayerCompilerParameterEnvelopeBound_mono_precision
    {p r₁ r₂ h : ℕ} (hr : r₁ ≤ r₂) :
    maximumLayerCompilerParameterEnvelopeBound p r₁ h ≤
      maximumLayerCompilerParameterEnvelopeBound p r₂ h := by
  exact compilerEnvelopeFromCoarseK_mono (coarseK_mono_precision hr)

/-- The raw-precision envelope is monotone as well. -/
theorem maximumLayerCompilerRawPrecisionBound_mono {p r₁ r₂ : ℕ} (hr : r₁ ≤ r₂) :
    maximumLayerCompilerRawPrecisionBound p r₁ ≤
      maximumLayerCompilerRawPrecisionBound p r₂ := by
  exact compilerEnvelopeFromCoarseK_mono (Nat.sub_le_sub_right hr 1)

/-- Precision transport for an arbitrary Pascal valuation model. -/
theorem valuationEdge_mono_precision (V : PascalValuationModel)
    {r₁ r₂ h q k : ℕ} (hr : r₁ ≤ r₂) (he : valuationEdge V r₁ h q k) :
    valuationEdge V r₂ h q k := by
  exact activeAt_mono_precision hr he

/-- At a fixed quotient, raising precision includes all previous targets. -/
theorem valuationTarget_mono_precision (V : PascalValuationModel)
    {r₁ r₂ h Q t : ℕ} (hr : r₁ ≤ r₂)
    (ht : IsTarget (valuationEdgeSystem V r₁ h) Q t) :
    IsTarget (valuationEdgeSystem V r₂ h) Q t := by
  rcases ht with ⟨q, k, hq, hqQ, he, ht⟩
  exact ⟨q, k, hq, hqQ, valuationEdge_mono_precision V hr he, ht⟩

/-- Concrete binomial target inclusion in precision at fixed quotient. -/
theorem binomialTarget_mono_precision {p r₁ r₂ h Q t : ℕ}
    (hp : 1 < p) (hr : r₁ ≤ r₂)
    (ht : IsTarget (binomialPadicEdgeSystem p r₁ h hp) Q t) :
    IsTarget (binomialPadicEdgeSystem p r₂ h hp) Q t := by
  exact valuationTarget_mono_precision (binomialPadicModel p hp) hr ht

/-- Every crossing persists when precision increases. -/
theorem crossesBarrier_mono_precision {p r₁ r₂ h Q : ℕ}
    (hp : 1 < p) (hr : r₁ ≤ r₂)
    (hc : CrossesBarrier (binomialPadicEdgeSystem p r₁ h hp) p Q) :
    CrossesBarrier (binomialPadicEdgeSystem p r₂ h hp) p Q := by
  exact binomialTarget_mono_precision hp hr hc

/-- The actual first noncrossing quotient is monotone in precision. -/
theorem stableQuotient_mono_precision {p r₁ r₂ h : ℕ}
    (hp : p.Prime) (hr : r₁ ≤ r₂) :
    stableQuotient p r₁ h ≤ stableQuotient p r₂ h := by
  by_contra hn
  have hlt : firstNoncrossingQuotient p r₂ h <
      firstNoncrossingQuotient p r₁ h := Nat.lt_of_not_ge hn
  have hc := crossesBarrier_of_lt_firstNoncrossing (r := r₁) (h := h) hp
    (firstNoncrossingQuotient_pos (r := r₂) (h := h) hp) hlt
  exact firstNoncrossingQuotient_not_crosses (r := r₂) (h := h) hp
    (crossesBarrier_mono_precision hp.one_lt hr hc)

/-- Exact maximum-layer monotonicity requires a nonempty lower-precision target. -/
theorem exactMaximumLayer_mono_precision {p r₁ r₂ h : ℕ}
    (hp : p.Prime) (hr₁ : 0 < r₁) (hr : r₁ ≤ r₂) :
    exactMaximumLayer p r₁ h ≤ exactMaximumLayer p r₂ h := by
  have ht := binomialTarget_mono_precision hp.one_lt hr
    (exactMaximumLayer_isTarget (r := r₁) (h := h) hp hr₁)
  exact isTarget_le_exactMaximumLayer hp
    (isTarget_mono_quotient _ ht (stableQuotient_mono_precision hp hr))

/-- The quotient-test counter is genuinely monotone in precision. -/
theorem quotientTestCount_mono_precision {p r₁ r₂ h : ℕ}
    (hp : p.Prime) (hr : r₁ ≤ r₂) :
    quotientTestCount p r₁ h ≤ quotientTestCount p r₂ h := by
  unfold quotientTestCount
  rw [stableQuotientSearchResult_tested hp, stableQuotientSearchResult_tested hp]
  exact stableQuotient_mono_precision hp hr

/-- The executable layer inherits the exact maximum's precision comparison. -/
theorem maximumLayerCompiler_layer_mono_precision {p r₁ r₂ h : ℕ}
    (hp : p.Prime) (hr₁ : 0 < r₁) (hr : r₁ ≤ r₂) :
    (maximumLayerCompiler p r₁ h).layer ≤ (maximumLayerCompiler p r₂ h).layer := by
  change finalFiberBoundaryLayer p r₁ h ≤ finalFiberBoundaryLayer p r₂ h
  rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr₁,
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp (hr₁.trans_le hr)]
  exact exactMaximumLayer_mono_precision hp hr₁ hr

/-- Combined parameter order: lower precision and higher defect lower the envelope. -/
theorem maximumLayerCompilerParameterEnvelopeBound_mono_parameters
    {p r₁ r₂ h₁ h₂ : ℕ} (hr : r₁ ≤ r₂) (hh : h₁ ≤ h₂) :
    maximumLayerCompilerParameterEnvelopeBound p r₁ h₂ ≤
      maximumLayerCompilerParameterEnvelopeBound p r₂ h₁ := by
  exact (maximumLayerCompilerParameterEnvelopeBound_mono_precision hr).trans
    (maximumLayerCompilerParameterEnvelopeBound_antitone_defect hh)

/-- Combined parameter order for the exact stable quotient. -/
theorem stableQuotient_mono_parameters {p r₁ r₂ h₁ h₂ : ℕ}
    (hp : p.Prime) (hr : r₁ ≤ r₂) (hh : h₁ ≤ h₂) :
    stableQuotient p r₁ h₂ ≤ stableQuotient p r₂ h₁ := by
  exact (stableQuotient_mono_precision hp hr).trans
    (stableQuotient_antitone_defect hp hh)

/-- Combined parameter order for the exact maximum target. -/
theorem exactMaximumLayer_mono_parameters {p r₁ r₂ h₁ h₂ : ℕ}
    (hp : p.Prime) (hr₁ : 0 < r₁) (hr : r₁ ≤ r₂) (hh : h₁ ≤ h₂) :
    exactMaximumLayer p r₁ h₂ ≤ exactMaximumLayer p r₂ h₁ := by
  exact (exactMaximumLayer_antitone_defect hp hr₁ hh).trans
    (exactMaximumLayer_mono_precision hp hr₁ hr)

/-- One adverse-corner envelope certifies an entire unbounded-defect region.
There is deliberately no upper bound on h. -/
theorem maximumLayerCompilerTotalTests_le_parameterRegionEnvelope
    {p r rmax h hmin : ℕ} (hp : p.Prime) (hr : 0 < r)
    (hrr : r ≤ rmax) (hhh : hmin ≤ h) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p rmax hmin := by
  exact (maximumLayerCompilerTotalTests_le_parameterEnvelopeBound hp hr).trans
    (maximumLayerCompilerParameterEnvelopeBound_mono_parameters hrr hhh)

/-- Membership in a closed precision/defect rectangle. -/
def InParameterRectangle (rlo rhi hlo hhi r h : ℕ) : Prop :=
  rlo ≤ r ∧ r ≤ rhi ∧ hlo ≤ h ∧ h ≤ hhi

/-- Opposite corners enclose every envelope value, including totalized boundaries. -/
theorem parameterRectangle_envelope_bounds {p rlo rhi hlo hhi r h : ℕ}
    (hx : InParameterRectangle rlo rhi hlo hhi r h) :
    maximumLayerCompilerParameterEnvelopeBound p rlo hhi ≤
      maximumLayerCompilerParameterEnvelopeBound p r h ∧
    maximumLayerCompilerParameterEnvelopeBound p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p rhi hlo := by
  exact ⟨maximumLayerCompilerParameterEnvelopeBound_mono_parameters hx.1 hx.2.2.2,
    maximumLayerCompilerParameterEnvelopeBound_mono_parameters hx.2.1 hx.2.2.1⟩

/-- The favorable and adverse corners bound the exact quotient everywhere. -/
theorem parameterRectangle_quotient_bounds {p rlo rhi hlo hhi r h : ℕ}
    (hp : p.Prime) (hx : InParameterRectangle rlo rhi hlo hhi r h) :
    stableQuotient p rlo hhi ≤ stableQuotient p r h ∧
      stableQuotient p r h ≤ stableQuotient p rhi hlo := by
  exact ⟨stableQuotient_mono_parameters hp hx.1 hx.2.2.2,
    stableQuotient_mono_parameters hp hx.2.1 hx.2.2.1⟩

/-- The exact maximum lies between the two extreme corner maxima. -/
theorem parameterRectangle_layer_bounds {p rlo rhi hlo hhi r h : ℕ}
    (hp : p.Prime) (hrlo : 0 < rlo)
    (hx : InParameterRectangle rlo rhi hlo hhi r h) :
    exactMaximumLayer p rlo hhi ≤ exactMaximumLayer p r h ∧
      exactMaximumLayer p r h ≤ exactMaximumLayer p rhi hlo := by
  exact ⟨exactMaximumLayer_mono_parameters hp hrlo hx.1 hx.2.2.2,
    exactMaximumLayer_mono_parameters hp (hrlo.trans_le hx.1) hx.2.1 hx.2.2.1⟩

/-- Corner bounds for the genuinely monotone quotient-test counter. -/
theorem parameterRectangle_quotientTests_bounds {p rlo rhi hlo hhi r h : ℕ}
    (hp : p.Prime) (hx : InParameterRectangle rlo rhi hlo hhi r h) :
    quotientTestCount p rlo hhi ≤ quotientTestCount p r h ∧
      quotientTestCount p r h ≤ quotientTestCount p rhi hlo := by
  unfold quotientTestCount
  rw [stableQuotientSearchResult_tested hp, stableQuotientSearchResult_tested hp,
    stableQuotientSearchResult_tested hp]
  exact parameterRectangle_quotient_bounds hp hx

/-- The envelope extrema are attained, since both corners belong to a nonempty rectangle. -/
theorem parameterRectangle_envelope_extrema {p rlo rhi hlo hhi : ℕ}
    (hr : rlo ≤ rhi) (hh : hlo ≤ hhi) :
    InParameterRectangle rlo rhi hlo hhi rlo hhi ∧
    InParameterRectangle rlo rhi hlo hhi rhi hlo ∧
    ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
      maximumLayerCompilerParameterEnvelopeBound p rlo hhi ≤
        maximumLayerCompilerParameterEnvelopeBound p r h ∧
      maximumLayerCompilerParameterEnvelopeBound p r h ≤
        maximumLayerCompilerParameterEnvelopeBound p rhi hlo := by
  exact ⟨⟨le_rfl, hr, hh, le_rfl⟩, ⟨hr, le_rfl, le_rfl, hh⟩,
    fun _ _ hx => parameterRectangle_envelope_bounds hx⟩

/-- Equality of the two corner maxima certifies a whole layer plateau. -/
theorem parameterRectangle_layer_constant_of_corners_eq
    {p rlo rhi hlo hhi r h : ℕ} (hp : p.Prime) (hrlo : 0 < rlo)
    (hx : InParameterRectangle rlo rhi hlo hhi r h)
    (heq : exactMaximumLayer p rlo hhi = exactMaximumLayer p rhi hlo) :
    exactMaximumLayer p r h = exactMaximumLayer p rlo hhi := by
  have hb := parameterRectangle_layer_bounds hp hrlo hx
  omega

/-- A certified layer plateau also fixes the quotient by the proved fiber identity. -/
theorem parameterRectangle_quotient_constant_of_layer_corners_eq
    {p rlo rhi hlo hhi r h : ℕ} (hp : p.Prime) (hrlo : 0 < rlo)
    (hx : InParameterRectangle rlo rhi hlo hhi r h)
    (heq : exactMaximumLayer p rlo hhi = exactMaximumLayer p rhi hlo) :
    stableQuotient p r h = stableQuotient p rlo hhi := by
  rw [← quotientOf_exactMaximumLayer hp, ← quotientOf_exactMaximumLayer hp,
    parameterRectangle_layer_constant_of_corners_eq hp hrlo hx heq]

/-- The terminal target predicate is identical throughout a certified layer plateau. -/
theorem parameterRectangle_targets_iff_of_layer_corners_eq
    {p rlo rhi hlo hhi r h t : ℕ} (hp : p.Prime) (hrlo : 0 < rlo)
    (hx : InParameterRectangle rlo rhi hlo hhi r h)
    (heq : exactMaximumLayer p rlo hhi = exactMaximumLayer p rhi hlo) :
    IsTarget (binomialPadicEdgeSystem p r h hp.one_lt) (stableQuotient p r h) t ↔
      IsTarget (binomialPadicEdgeSystem p rlo hhi hp.one_lt)
        (stableQuotient p rlo hhi) t := by
  rw [isTarget_iff_le_exactMaximumLayer hp (hrlo.trans_le hx.1),
    isTarget_iff_le_exactMaximumLayer hp hrlo,
    parameterRectangle_layer_constant_of_corners_eq hp hrlo hx heq]

/-- Uniform exact saturation on an unbounded-defect region, not just a finite rectangle. -/
theorem maximumLayerCompiler_saturated_parameterRegion {p r rmax h hmin : ℕ}
    (hp : p.Prime) (hr : 0 < r) (hrr : r ≤ rmax) (hhh : hmin ≤ h)
    (hsat : rmax - 1 ≤ hmin) :
    maximumLayerCompiler p r h =
      { quotient := 1, layer := 1, quotientTests := 1,
        finalFiberTests := p - 1, barrierRepresentativeTests := 1 } := by
  exact maximumLayerCompiler_saturated hp hr
    ((Nat.sub_le_sub_right hrr 1).trans (hsat.trans hhh))

/-- At fixed defect and stable quotient, total reported work plus the maximum
layer is conserved. No precision ordering is required for this identity. -/
theorem maximumLayerCompilerTotalTests_add_layer_eq_of_quotient_eq
    {p r₁ r₂ h : ℕ} (hp : p.Prime) (hr₁ : 0 < r₁) (hr₂ : 0 < r₂)
    (hQ : stableQuotient p r₁ h = stableQuotient p r₂ h) :
    maximumLayerCompilerTotalTests p r₁ h + exactMaximumLayer p r₁ h =
      maximumLayerCompilerTotalTests p r₂ h + exactMaximumLayer p r₂ h := by
  have hqt : quotientTestCount p r₁ h = quotientTestCount p r₂ h := by
    unfold quotientTestCount
    rw [stableQuotientSearchResult_tested hp, stableQuotientSearchResult_tested hp]
    exact hQ
  have hrep : barrierRepresentativeTestCount p r₁ h =
      barrierRepresentativeTestCount p r₂ h := by
    simp only [barrierRepresentativeTestCount, hQ]
  have hupper : finalFiberUpper p r₁ h = finalFiberUpper p r₂ h := by
    simp only [finalFiberUpper, hQ]
  have hM₁ := exactMaximumLayer_le_finalFiberUpper (r := r₁) (h := h) hp
  have hM₂ := exactMaximumLayer_le_finalFiberUpper (r := r₂) (h := h) hp
  simp only [maximumLayerCompilerTotalTests, reportedCompilerTests, maximumLayerCompiler]
  rw [finalFiberBoundaryTestCount_eq_exactDistance hp hr₁,
    finalFiberBoundaryTestCount_eq_exactDistance hp hr₂]
  omega

/-- Within a fixed-quotient precision plateau, reported work is antitone. -/
theorem maximumLayerCompilerTotalTests_antitone_precision_of_quotient_eq
    {p r₁ r₂ h : ℕ} (hp : p.Prime) (hr₁ : 0 < r₁) (hr : r₁ ≤ r₂)
    (hQ : stableQuotient p r₁ h = stableQuotient p r₂ h) :
    maximumLayerCompilerTotalTests p r₂ h ≤ maximumLayerCompilerTotalTests p r₁ h := by
  have hsum := maximumLayerCompilerTotalTests_add_layer_eq_of_quotient_eq
    hp hr₁ (hr₁.trans_le hr) hQ
  have hM := exactMaximumLayer_mono_precision (h := h) hp hr₁ hr
  omega

/-- A kernel-reduced precision witness: increased precision can reduce reported work. -/
theorem maximumLayerCompilerTotalTests_precision_counterexample :
    maximumLayerCompilerTotalTests 3 1 0 = 4 ∧
      maximumLayerCompilerTotalTests 3 2 0 = 3 := by
  decide +kernel

/-- Monotone exact outputs and envelopes do not imply monotone reported work. -/
theorem maximumLayerCompilerTotalTests_not_monotone_precision :
    ¬ Monotone (fun r : ℕ => maximumLayerCompilerTotalTests 3 r 0) := by
  intro hm
  have hb := hm (by decide : 1 ≤ 2)
  dsimp only at hb
  have hw := maximumLayerCompilerTotalTests_precision_counterexample
  omega

/-- Executable two-corner test for a rectangle's exact layer plateau. -/
def rectangleLayerPlateauCheck (p rlo rhi hlo hhi : ℕ) : Bool :=
  (maximumLayerCompiler p rlo hhi).layer == (maximumLayerCompiler p rhi hlo).layer

/-- The corner test reflects equality of the exact mathematical maxima. -/
theorem rectangleLayerPlateauCheck_eq_true_iff {p rlo rhi hlo hhi : ℕ}
    (hp : p.Prime) (hrlo : 0 < rlo) (hr : rlo ≤ rhi) :
    rectangleLayerPlateauCheck p rlo rhi hlo hhi = true ↔
      exactMaximumLayer p rlo hhi = exactMaximumLayer p rhi hlo := by
  simp only [rectangleLayerPlateauCheck, maximumLayerCompiler,
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp hrlo,
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp (hrlo.trans_le hr), beq_iff_eq]

/-- Two successful corner evaluations certify every exact layer and quotient
in the rectangle, without scanning its interior. -/
theorem rectangleLayerPlateauCheck_sound {p rlo rhi hlo hhi r h : ℕ}
    (hp : p.Prime) (hrlo : 0 < rlo)
    (hx : InParameterRectangle rlo rhi hlo hhi r h)
    (hc : rectangleLayerPlateauCheck p rlo rhi hlo hhi = true) :
    (maximumLayerCompiler p r h).layer = (maximumLayerCompiler p rlo hhi).layer ∧
    (maximumLayerCompiler p r h).quotient = (maximumLayerCompiler p rlo hhi).quotient := by
  have heq := (rectangleLayerPlateauCheck_eq_true_iff hp hrlo (hx.1.trans hx.2.1)).1 hc
  change finalFiberBoundaryLayer p r h = finalFiberBoundaryLayer p rlo hhi ∧
    stableQuotient p r h = stableQuotient p rlo hhi
  rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp (hrlo.trans_le hx.1),
    finalFiberBoundaryLayer_eq_exactMaximumLayer hp hrlo]
  exact ⟨parameterRectangle_layer_constant_of_corners_eq hp hrlo hx heq,
    parameterRectangle_quotient_constant_of_layer_corners_eq hp hrlo hx heq⟩

/-- On a nonempty rectangle, the corner test is also necessary for a uniform layer. -/
theorem rectangleLayerPlateauCheck_eq_true_iff_uniform_layer
    {p rlo rhi hlo hhi : ℕ} (hp : p.Prime) (hrlo : 0 < rlo)
    (hr : rlo ≤ rhi) (hh : hlo ≤ hhi) :
    rectangleLayerPlateauCheck p rlo rhi hlo hhi = true ↔
      ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
        (maximumLayerCompiler p r h).layer = (maximumLayerCompiler p rlo hhi).layer := by
  constructor
  · exact fun hc _ _ hx => (rectangleLayerPlateauCheck_sound hp hrlo hx hc).1
  · intro hall
    have hc := hall rhi hlo ⟨hr, le_rfl, le_rfl, hh⟩
    simp only [rectangleLayerPlateauCheck, beq_iff_eq]
    exact hc.symm

/-- Proof-carrying rectangular family. It retains complete Block 13 certificates
at the two opposite corners; its total bound never assumes work monotonicity. -/
structure MaximumLayerCompilerRectangleCertificate (p rlo rhi hlo hhi : ℕ) where
  favorableCorner : MaximumLayerCompilerDefectCertificate p rlo hlo hhi
  adverseCorner : MaximumLayerCompilerDefectCertificate p rhi hlo hlo
  precision_pos : 0 < rlo
  precision_order : rlo ≤ rhi
  defect_order : hlo ≤ hhi
  envelope_bounds : ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
    maximumLayerCompilerParameterEnvelopeBound p rlo hhi ≤
      maximumLayerCompilerParameterEnvelopeBound p r h ∧
    maximumLayerCompilerParameterEnvelopeBound p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p rhi hlo
  quotient_bounds : ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
    stableQuotient p rlo hhi ≤ stableQuotient p r h ∧
      stableQuotient p r h ≤ stableQuotient p rhi hlo
  layer_bounds : ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
    exactMaximumLayer p rlo hhi ≤ exactMaximumLayer p r h ∧
      exactMaximumLayer p r h ≤ exactMaximumLayer p rhi hlo
  reported_total_bound : ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p rhi hlo
  plateau_check_sound : rectangleLayerPlateauCheck p rlo rhi hlo hhi = true →
    ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
      (maximumLayerCompiler p r h).layer = (maximumLayerCompiler p rlo hhi).layer ∧
      (maximumLayerCompiler p r h).quotient = (maximumLayerCompiler p rlo hhi).quotient
  layer_plateau : exactMaximumLayer p rlo hhi = exactMaximumLayer p rhi hlo →
    ∀ r h, InParameterRectangle rlo rhi hlo hhi r h →
      exactMaximumLayer p r h = exactMaximumLayer p rlo hhi

/-- Construct the rectangle certificate without changing any executable definition. -/
def maximumLayerCompilerRectangleCertificate (p rlo rhi hlo hhi : ℕ)
    (hp : p.Prime) (hrlo : 0 < rlo) (hr : rlo ≤ rhi) (hh : hlo ≤ hhi) :
    MaximumLayerCompilerRectangleCertificate p rlo rhi hlo hhi where
  favorableCorner := maximumLayerCompilerDefectCertificate p rlo hlo hhi hp hrlo hh
  adverseCorner := maximumLayerCompilerDefectCertificate p rhi hlo hlo hp
    (hrlo.trans_le hr) le_rfl
  precision_pos := hrlo
  precision_order := hr
  defect_order := hh
  envelope_bounds := fun _ _ hx => parameterRectangle_envelope_bounds hx
  quotient_bounds := fun _ _ hx => parameterRectangle_quotient_bounds hp hx
  layer_bounds := fun _ _ hx => parameterRectangle_layer_bounds hp hrlo hx
  reported_total_bound := fun _ _ hx => maximumLayerCompilerTotalTests_le_parameterRegionEnvelope
    hp (hrlo.trans_le hx.1) hx.2.1 hx.2.2.1
  plateau_check_sound := fun hc _ _ hx => rectangleLayerPlateauCheck_sound hp hrlo hx hc
  layer_plateau := fun heq _ _ hx => parameterRectangle_layer_constant_of_corners_eq hp hrlo hx heq

end KomorebiPadic
