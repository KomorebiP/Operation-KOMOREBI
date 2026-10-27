# Paper X: quantitative counting continuation

The requested counting block is proved for actual ordinary ideal classes of every number field. The bundle contains 221 cumulative Lean source modules: 199 unchanged predecessors and 22 new modules containing 106 theorem/lemma declarations and 151 explicitly named declarations of all kinds.

For a number field K of degree d, let A_C(X) count nonzero integral ideals in an ordinary ideal class C with absolute norm at most X. The new theorem proves

\[
A_C(X)=c_KX+O_{K,C}(X^{1-1/d}),\qquad
c_K=\frac{2^{r_1}(2\pi)^{r_2}R_K}{w_K\sqrt{|\Delta_K|}}.
\]

The final theorem supplies the actual boundary atlas and lattice estimate internally. It has no remaining counting, boundary-chart, or class-representative hypothesis. A second form bounds the absolute error for every real X at least one. The degree-one specialization has a constant error bound; the normalization check proves c_Q=1.

## What is proved

1. The actual mixed-space unit cone has a finite common-Lipschitz cover of its full frontier by charts on the (d−1)-dimensional unit cube. Real signs, complex angles, and the origin are included.
2. For each fixed full lattice Lambda and bounded measurable D with such an atlas, there is a C such that, uniformly over translations a and real t at least one,
   \[
   \left|\#((a+\Lambda)\cap tD)-
   \frac{\operatorname{vol}(D)}{\operatorname{covol}(\Lambda)}t^d\right|
   \le C(t^{d-1}+1).
   \]
   The proof derives this through actual unit-cell volumes and boundary-cell counts.
3. An exact ideal-to-lattice correspondence, including the roots-of-unity factor, attaches this estimate to A_C(X). The cone volume and ideal-lattice covolume give the displayed constant c_K.
4. A separate real-axis argument proves a first-order endpoint estimate from a finite logarithmic moment. A measurable summatory function bounded by C x^r with r<1 supplies that moment for its actual Mellin integral. With a supplied pole-product identity and nonzero pole residues, the endpoint argument forces the factors' endpoint values to be nonzero and the product exponent to be one. A square-root example proves that finite endpoint limits alone do not suffice.

These are formalizations and connections of classical mathematical arguments; no novelty claim is made.

## Exact scope of the paper ledger

The source ledger remains **17 checked / 3 partial**. Claims 9.1, 9.2 and 11.1 remain partial. This block does not yet give character cancellation in norm-residue or ray classes, the required arithmetic Euler-product identity, prescribed-Frobenius prime-series divergence, or the final source separator assembly. The real-axis Mellin/pole theorem still assumes its summatory-function bounds and product identity. Ordinary ideal-class counting alone does not discharge those assumptions.

See `CURRENT_STATUS.md` for claim-level dependencies and `COUNTING_ADDENDUM.tex` for the mathematical statement and connection to the manuscript. The older complete manuscript is retained unchanged under `evidence/baseline/`; the addendum is the current amendment.

## Reproducibility

Pinned runtime: Lean 4.34.0-rc2 and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, from the project's Komorebi portable kit. The runtime and Mathlib are external dependencies, not bundled here. Exact source and proof-object hashes are in `manifest.json`; all delivered files are covered by `INTEGRITY.json`.

From the extracted release directory, run:

```sh
python3 checks/replay_counting.py /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The script rebuilds all 22 new modules and their one required predecessor, `RayCountingGeometry`, in an empty PaperX object directory. It imports no delivered PaperX proof objects, compares all 23 rebuilt objects against their recorded hashes, and queries the transitive axioms of every explicitly named new declaration. Other predecessors are included as frozen source history; a new cumulative 221-module rebuild is not claimed.

`verification.json` records the final independent audit and release gates. `fresh_replay_verification.json` records the separate source-closure replay. The independent audit traverses every environment declaration owned by the new modules, including generated declarations. Positive controls exercise endpoint estimates, cell cardinality, the degree-one error, and the rational-field coefficient. False claims and a placeholder are required to fail for their intended reasons.

The route reports and retained logs describe earlier unsuccessful compiler attempts and repairs. Failed exploratory checks are not counted as passed evidence. `licenses/Mathlib-LICENSE` and `licenses/NOTICE.md` record the Mathlib proof adaptation used in the ideal-count attachment.

## Main entry points

| File | Main result |
|---|---|
| `lean/PaperX/CountingBoundaryAtlas.lean` | Actual finite boundary atlas |
| `lean/PaperX/LatticeCountingFull.lean` | Uniform translated full-lattice discrepancy |
| `lean/PaperX/IdealClassQuantitativeTheorem.lean` | Unconditional ordinary ideal-class quantitative count |
| `lean/PaperX/RealAxisEndpointIntegral.lean` | Endpoint error from weighted integrability |
| `lean/PaperX/RealAxisMellinPole.lean` | Conditional Mellin/pole assembly |

