# Focused self-review of SF-LEAN-B18

Claim: for every rational scale tuple `p`, rational `x`, optional natural index,
optional rational outer radius and result `v`, a successful
`certifiedEvaluationSpec` return preserves the exact metadata and coefficient
counts, encloses both canonical real components at `x`, and supplies a uniform
complex Taylor error bound on `|z| <= x` equal to its `tail_bound` field.

Primary mathematical verdict: **proved as written**, with successful
final compilation, exact axiom audit and same-kernel replay recorded in the
formal receipt. The separate claim about all actual Python executions is
**conditional on the primitive semantics** in `SOURCE_CORRESPONDENCE.md`; no
full Python refinement theorem is asserted.

## Dependency graph

`certifiedEvaluationSpec` success -> `evaluation_success_shape` -> strict
rational scales, `0 <= x < S`, successful fixed-budget `checkedMajorant`, and
the exact result constructor.

* Metadata and counts follow from the constructor and Block16 array length.
* Strict rational scales imply the real positivity/contraction hypotheses.
* Block17 checked-majorant success -> guarded success -> first-small ladder,
  adequate fuel and the exact rational majorant value.
* Block16 normalization/array equality and Block15 analytic endpoint bounds
  give the two real enclosures.
* Block15 rational complex remainder with the same adequate fuel gives the
  reported uniform complex error.

Leaves are internal proofs and the existing Mathlib/Lean foundations. Python
primitives are unchecked assumptions only in the separate correspondence
argument. Runtime tests are finite evidence, not leaves of the Lean proof.
No downstream result is used to prove its own prerequisite.

## Obligations

| Obligation | Finding |
| --- | --- |
| Input domain and quantifiers | Passed: success itself supplies strict scales and `0 <= x < S`; no separate hidden admissibility hypothesis. |
| Zero denominator | Passed: `S > x >= 0` implies `S > 0` on every successful return. |
| Normalization and index | Passed: derivatives divide by odd factorials; `last_index=N` retains `N+1` coefficients, with first omitted degree `2*N+3`. |
| Component order | Passed: `U` uses index 0 and `V` index 1. The source's products are materialized before either append. |
| Majorant guards | Passed at specification level: fixed 20/2,000,000 defaults, explicit error propagation, no inference of success from mathematical fuel existence. |
| Origin/default | Passed: default radius is 1 at the origin; the majorant is still called. Strict contractions require one ladder step from 1. |
| Real versus complex conclusions | Passed: intervals are for nonnegative real `x`; complex error applies on the closed disk and uses the same tail. |
| Constructor versus successful computation | Passed: the unchecked constructor is not asserted to enclose functions without the success premise. |
| Source-language sequencing | Conditional: pure mathematical arrays can be constructed after majorant success in the model; Python constructs them before the call. Unexpected exceptions and full trace equivalence remain outside scope. |
| Runtime coverage | Finite only: 240 valid grid cases plus named default/manuscript and boundary cases, 507 checks. No population-wide Python conclusion. |
| External numerical or theorem claims | Out of scope: no new cited theorem or floating benchmark is used. |

The first Python audit run failed because its test incorrectly expected step
exhaustion at `S=1`. That expectation was corrected to the actual `S=2`
discriminator; the failed manifest is preserved and is not acceptance evidence.
Development compile diagnostics are similarly retained outside the release.

Review provenance: author self-review, using the proof-audit and proofread-math
checklists. No independent reviewer or second kernel was used. The exact
reviewed source digest is in `declarations.json`; the final evidence receipt
must agree with that digest. The new Lean source and this report were checked
for notation, indexing, theorem references and scope. No prior manuscript or
Python source was edited.
