# Independent audit of the quantitative counting continuation

Verdict: **proved as written at the declared block scope**. All 22 new production modules independently rebuilt with strict compiler exit 0 and identical proof objects. The block adds 106 theorem/lemma declarations. The transitive axiom traversal covered all 261 environment declarations owned by these modules, including generated declarations, and found only `propext`, `Classical.choice`, and `Quot.sound`. All 199 predecessor source hashes and all 22 new source hashes remained unchanged.

The normalized geometric claim is: for a fixed full lattice Lambda in a finite-dimensional real inner-product space, and a bounded measurable region D with the constructed finite Lipschitz boundary atlas, there is a nonnegative constant C such that every translate a and every real t≥1 satisfy

`|#((a+Lambda) ∩ tD) − vol(D)/covol(Lambda) * t^d| ≤ C*(t^(d−1)+1)`.

For the actual ordinary number-field cone the atlas is constructed, not assumed. For every number field K of degree d≥1 and every ordinary ideal class C, the final arithmetic assembly proves

`#{nonzero integral I : N(I)≤X and [I]=C} = c_K*X + O_(K,C)(X^(1−1/d))`,

where `c_K = 2^r1 * (2*pi)^r2 * regulator(K) / (torsionOrder(K) * sqrt(|discr(K)|))`. It also proves an explicit existential error bound valid for every X≥1. These are statements about the actual ideals and field invariants.

The target is the actual ordinary number-field cone, its finite boundary atlas of dimension d−1, a fixed-lattice discrepancy estimate uniform in translations and scales t≥1, and the resulting ordinary ideal-class count. The separate real-axis endpoint argument is an analytic prerequisite. It does not supply arithmetic character cancellation or an Euler-product identity.

## Source and mathematical review

The polar construction restores each real sign and each complex argument. The parameter space has exactly d real coordinates. The boundary cover puts at least one non-angular coordinate on a face, then removes that coordinate. The resulting charts therefore have dimension d−1. The origin is covered by the zero radial face. Degree one is included through a zero-dimensional face parameter space. Smoothness is established on the full parameter space, and compactness of the unit cube supplies finite Lipschitz constants. The finite maximum makes the bound uniform over charts.

The cell argument uses closed unit cells to detect the topological boundary and disjoint half-open unit cells for exact volume. This distinction is necessary: closed cells overlap, while their disjoint half-open versions each have volume one. A connected cell with one point in D and one outside D meets the boundary. The symmetric difference between D and the cell union selected by integer tags is therefore covered by boundary cells. The resulting discrepancy bound concerns actual cardinality and actual Lebesgue volume.

The regular mesh has denominator ceil(t). Every point of the chart parameter cube is within distance 1/ceil(t) of a mesh point. After dilation by t, each chart piece lies in a ball whose radius depends on the chart Lipschitz constant but not on t or the translation. Counting coordinatewise integer boxes around these balls gives O(t^(d−1)) boundary cells with a translation-independent constant. The constants are intentionally coarse.

The ideal attachment uses actual nonzero integral ideals, an inverse-class ideal representative, the ordinary fundamental cone, and the lattice of that ideal. The torsion factor is an exact cardinality identity, and the covolume normalization gives the classical common leading coefficient. The attachment follows the existing Mathlib `NumberField.Ideal.Asymptotics` generator correspondence; the source development there credits Xavier Roblot. The final `IdealClassQuantitativeTheorem` assembly discharges the radial discrepancy hypothesis using the actual cone atlas and the proved full-lattice discrepancy theorem. Consequently the final ordinary ideal-class asymptotic has no supplied counting-bound premise.

The real-axis integral proof assumes measurable data and a finite weighted first moment, then proves integrability and an O(h) endpoint error. The Mellin module derives the weighted first moment from an actual all-x>1 estimate ||S(x)||≤C x^r with r<1. The pole product theorem derives the exponent-one and nonzero-endpoint conclusions from this first-order control, nonzero simple-pole residues, and the supplied product identity. No meromorphic continuation is assumed. The square-root boundary example has finite endpoint limit but not O(h), so it correctly refutes replacing the first-order requirement by finite limits alone.

No claim of arithmetic prime-series divergence, character cancellation, or the source separator assembly follows from these statements alone. Full Claim 9.1 remains partial, and the full paper ledger remains 17 checked / 3 partial.

## Independent execution protocol

The audit rebuild copies each explicitly frozen new source to `privatechecks/audit_replay/lean`. Its first Lean module root contains the audit's own newly rebuilt objects together with copies of exactly the 199 frozen predecessor objects, followed by the pinned Mathlib environment. It never searches the authors' mixed new-object build directory. Every source and proof-object hash is compared with the corresponding frozen author result.

The 199 predecessor source hashes are checked against `evidence/frozen_sources.json` before each replay batch. The compiler uses Lean 4.34.0-rc2 with `-DwarningAsError=true`. The results are recorded per module. Appending the combined compilation table is protected by an exclusive file lock and committed through an atomic rename, so independent batches cannot lose rows.

The axiom audit traverses every environment declaration owned by the accepted new modules, including generated declarations, and recursively collects its axioms. Only `propext`, `Classical.choice`, and `Quot.sound` are permitted. Named theorem counts and environment declaration counts are different quantities.

## Controls and failures

All six audit controls produced their expected outcomes:

| Control | Result |
|---|---|
| Actual damping inequality, exact integer box cardinality, and square-root first-order failure | Strict exit 0 |
| Both final ideal-count bounds specialized to K=Q and exponent 0 | Strict exit 0 |
| Exact residue c_Q=1, using real-place count, roots of unity, and empty regulator determinant | Strict exit 0 |
| False bound that the one-dimensional radius-zero containing box has cardinality at most 2 | Rejected after reduction to `False` |
| False nonvanishing of the explicit square-root endpoint | Rejected after reduction to `False` |
| Explicit placeholder in a file requiring no imports | Rejected specifically with `declaration uses sorry` |

One audit harness attempt failed before proof elaboration: the initial separate module roots caused Lean to look for `RayCountingGeometry.olean` only in the first `PaperX` directory. The baseline object existed in the second root, but Lean did not fall through to it. The repair copied only the 199 frozen baseline objects into the audit's first module root. The failed diagnostic is preserved in `privatechecks/audit_replay/logs/CountingBoundaryPolar.prior.*.log`, and the failed result remains in `compilation.json`. The unchanged source then rebuilt with the expected identical proof-object hash. This import-layout failure was not counted as a negative mathematical control.

The arithmetic author's first numeric coefficient test stopped because generic simplification did not unfold the real-place count, regulator, and torsion order. Its repaired explicit argument was copied and independently replayed as `AuditRationalResidue`; it passed. No production statement was weakened or changed for either repair.


## Dependency and obligation matrix

| Required implication | Evidence and status |
|---|---|
| Full mixed-space boundary, including signs, angles, and origin | `CountingBoundaryPolar/Cover/Atlas`: passed |
| Parameter dimension is exactly d−1, including degree one | Cardinality and face equivalences: passed |
| Transport to arbitrary actual lattice coordinates | `CountingBoundaryTransport` and `LatticeCountingTransport`: passed |
| Uniform mesh and finite cell count | `IntegerCellBounds/ChartCounting/FiniteCharts`: passed |
| Cardinality-volume discrepancy from actual cells | `LatticeCountingInterface/Discrepancy/Grid`: passed |
| Arbitrary full lattice and actual lattice coset | `LatticeCountingFull`: passed |
| Exact ideal/torsion correspondence and coefficient | `IdealClassQuantitativeAttachment/Constant`: passed |
| Actual ordinary ideal-class power-saving count | `IdealClassQuantitativeTransfer/Geometry/Theorem`: passed, no supplied quantitative-bound premise |
| Mellin endpoint first-order bound from power-saving summatory input | `RealAxisEndpointIntegral/MellinMoment`: passed under the displayed measurable-function and bound hypotheses |
| Pole index one and nonvanishing | `RealAxisPoleRigidity/MellinPole`: passed under the displayed product identity and nonzero-residue hypotheses |
| Actual arithmetic character cancellation, Euler identities, and prescribed-prime nonsummability | Not addressed by this block |
| Full Paper X Claim 9.1 and remaining source-theorem assembly | Incomplete |

## Reproduction and exact evidence

Run `python3 privatechecks/audit_replay.py MODULE...` in dependency order using `modules_in_build_order` in `privatechecks/audit_summary.json`. These research-workspace commands require the full frozen predecessor object tree restored under `build/PaperX`; the release's separate clean source-closure replay is the standalone reproduction route. The command uses the pinned portable Lean kit recorded in the script. Then run `python3 privatechecks/audit_axioms.py`, `python3 privatechecks/audit_controls.py`, and `python3 privatechecks/audit_finalize.py`.

The compiler's exact commands, exit statuses, source hashes, proof-object hashes, and elapsed times are in `privatechecks/audit_replay/compilation.json`. Complete axiom output is in `privatechecks/audit_replay/logs/AuditAxioms.log`. Machine-readable verdict, counts, control outcomes, and frozen hashes are in `privatechecks/audit_summary.json`.

This audit is an independent source replay against frozen predecessor proof objects. It does not claim to freshly rebuild all 199 predecessors. The release's separate clean replay may verify the smaller source dependency closure, but that is distinct evidence.

The strongest safe conclusion is completion of the requested quantitative geometric and ordinary ideal-class counting block. The next missing implication is cancellation for the actual arithmetic character-weighted count, with the corresponding Euler-product identity and prime-series argument. The full paper ledger remains 17 checked / 3 partial.
