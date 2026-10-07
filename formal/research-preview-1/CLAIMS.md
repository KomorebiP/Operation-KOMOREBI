# Claims and source register

The seven public claim groups refer to the unchanged Block 34 mathematical checkpoint. This is a source map, not an originality register. Historical Lean evidence and fresh release checks are separately labeled in [REPRODUCE.md](REPRODUCE.md). Each source locator is mechanically checked.
## C01 — Canonical normalized solution

Existence and uniqueness of F with F(0)=1 and BF=A F(z^p).

**Hypotheses:** Prime p; r>0; integer A,B; p does not divide B(0); equal constants in ZMod(p^r).

**Boundary:** Not analytic convergence or a statement about all generating functions.

`existsUnique_canonicalMaskSeries` — [CanonicalMaskAutomaton.lean, line 56](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L56).

`exists_normalizedMaskSeries_iff` — [CanonicalMaskAutomaton.lean, line 69](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L69).

## C02 — Integral defect and exact one-layer obstruction

B^p=B(z^p)+p E_B; the literal one-layer criterion is E_B=0 modulo p^(r-1).

**Hypotheses:** Prime p for the integral defect. For the one-layer converse additionally use the actual Mahler equation, unit denominator and unit F at positive precision.

**Boundary:** Not an obstruction to the existence of the underlying normalized series.

`frobeniusDefect_identity` — [FrobeniusDefect.lean, line 59](padic/lean/KomorebiPadic/FrobeniusDefect.lean#L59).

`frobeniusDefect_unique` — [FrobeniusDefect.lean, line 70](padic/lean/KomorebiPadic/FrobeniusDefect.lean#L70).

`literalOneLayerCartier_iff_defectVanishing` — [CartierObstruction.lean, line 120](padic/lean/KomorebiPadic/CartierObstruction.lean#L120).

`literalOneLayerCartier_iff_defectDepth` — [CartierObstruction.lean, line 132](padic/lean/KomorebiPadic/CartierObstruction.lean#L132).

## C03 — Actual Cartier transition

The finite correction formula is a full formal-series identity. Exact branch-content valuation justifies removal of inactive terms, with nonzero-defect hypotheses stated separately.

**Hypotheses:** Prime p; r>0; digit d<p; denominator constant a unit; F satisfies its equation. Finite valuation pruning distinguishes zero defect.

**Boundary:** An active pre-section term need not survive every digit or cancellation.

`maskLayerSeries_cartier_transition` — [CartierMaskTransition.lean, line 126](padic/lean/KomorebiPadic/CartierMaskTransition.lean#L126).

`maskLayerSeries_cartier_transition_pruned` — [CartierMaskTransition.lean, line 175](padic/lean/KomorebiPadic/CartierMaskTransition.lean#L175).

`cartierBranchWeight_order` — [PolynomialBranchValuation.lean, line 81](padic/lean/KomorebiPadic/PolynomialBranchValuation.lean#L81).

`cartierBranchWeight_survives_iff_activeAt` — [PolynomialBranchValuation.lean, line 100](padic/lean/KomorebiPadic/PolynomialBranchValuation.lean#L100).

## C04 — Finite all-coefficient machine

Finite linear state transitions compute every coefficient of the constructed canonical series. Canonical series and finite outputs reduce compatibly across positive precisions.

**Hypotheses:** C01 mask assumptions; least-significant-first digits and all-word convention.

**Boundary:** Noncomputable Lean mathematics is not a formally refined efficient Python program.

`finiteMask_output_canonical_word` — [CanonicalMaskAutomaton.lean, line 82](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L82).

`finiteMask_output_canonical_coefficient` — [CanonicalMaskAutomaton.lean, line 93](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L93).

`canonicalMaskSeries_reduce` — [CanonicalMaskAutomaton.lean, line 132](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L132).

`finiteMask_output_precision_compatible` — [CanonicalMaskAutomaton.lean, line 142](padic/lean/KomorebiPadic/CanonicalMaskAutomaton.lean#L142).

## C05 — Preservation through compressed representations

The reduced reachable-observable state system retains the canonical output.

**Hypotheses:** C01 mask assumptions. The predecessor modules carry the separate invariance and capacity contracts.

**Boundary:** No universal strict reduction and no claim that the linear span is the deterministic orbit.

`observableMask_output_canonical_coefficient` — [ObservableMaskAutomaton.lean, line 112](padic/lean/KomorebiPadic/ObservableMaskAutomaton.lean#L112).

`observableMask_reachable` — [ObservableMaskAutomaton.lean, line 202](padic/lean/KomorebiPadic/ObservableMaskAutomaton.lean#L202).

`observableMask_observable` — [ObservableMaskAutomaton.lean, line 141](padic/lean/KomorebiPadic/ObservableMaskAutomaton.lean#L141).

## C06 — Canonical global finite-linear minimum

Unique structure-preserving isomorphism of reachable-observable realizations and a cardinality lower bound against every finite linear realization.

**Hypotheses:** Same commutative coefficient ring and alphabet; equality of the function on all words. The cardinality competitor is finite.

**Boundary:** Not minimum DFA size, minimum generator rank, canonical literal matrices, or a claim of historical novelty.

`minimalMask_comparison` — [MinimalMaskRealization.lean, line 58](padic/lean/KomorebiPadic/MinimalMaskRealization.lean#L58).

`minimalMask_cardinality` — [MinimalMaskRealization.lean, line 71](padic/lean/KomorebiPadic/MinimalMaskRealization.lean#L71).

`minimalMask_unique_equiv` — [MinimalMaskRealization.lean, line 82](padic/lean/KomorebiPadic/MinimalMaskRealization.lean#L82).

## C07 — Finite behavior-comparison horizon

Agreement on all words of length < b+c is equivalent to all-word agreement.

**Hypotheses:** Finite state modules of cardinalities p^b and p^c; p prime; the same ring and alphabet.

**Boundary:** A finite word-length horizon is a finite enumeration only for a finite alphabet; no efficiency claim.

`behavior_eq_iff_finite_words` — [FiniteBehaviorComparison.lean, line 36](padic/lean/KomorebiPadic/FiniteBehaviorComparison.lean#L36).

`exists_short_behavior_difference` — [FiniteBehaviorComparison.lean, line 56](padic/lean/KomorebiPadic/FiniteBehaviorComparison.lean#L56).

The worked example in the technical note is checked by `demo.py`. Generic minimization and structure results are situated in [ATTRIBUTION.md](ATTRIBUTION.md). Proposed work is listed only in [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md), not counted as an additional proved claim.
