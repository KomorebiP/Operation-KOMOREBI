# Final proofreading: limits, floors, and budget certificates

Reviewed all seven assigned chapters in edit mode with the mathematical proofreading checklist. Coverage is complete: 951 source lines before editing, including all statements, proofs, worked examples, figures, captions, tables, and cross-references. Shared notation and immediate context were checked.

## Outcome

Six local changes were made in three files. Four files remain byte-for-byte unchanged. There are no unresolved mathematical issues found in this proofreading scope. No new result or proof route was added, no proof was shortened mathematically, and all labels and numbered environments retain their order. Existing explanations already provide the required transitions, so no supplementary exposition was added.

## Exact changes

### L01 — source/chapters/05a_certificates.tex:20

Category: explicit_mathematical_type.

Before:
```latex
More generally, let \(\widetilde D:E\to R\) be the operator actually used in the measurement.
```

After:
```latex
More generally, let \(\widetilde D:E\to R\) be the bounded linear operator actually used in the measurement.
```

Makes explicit the operator type already required by the stated operator norm and by the proof. Root approved this clarification; no conclusion or estimate changes.

### L02 — source/chapters/05a_certificates.tex:42

Category: explicit_mathematical_geometry.

Before:
```latex
For a concrete family, take
\[
 D(a,b)=a,
```

After:
```latex
For a concrete family, take \(E=\R^2\) with the Euclidean norm and \(R=\R\), and define
\[
 D(a,b)=a,
```

States the ambient domain, target, and Euclidean norm already forced by the subsequent square-root calculation and gain value. Root approved this clarification.

### L03 — source/chapters/05e_escape.tex:34

Category: routine_prose.

Before:
```latex
A constant square-summable sequence must have constant zero,
```

After:
```latex
A constant square-summable sequence must be zero,
```

Removes an awkward repeated use of constant while retaining the same assertion.

### L04 — source/chapters/05g_budget_certificates.tex:60

Category: prose_scope_clarification.

Before:
```latex
The nonclosed range is the increasing union of these closed images.
```

After:
```latex
The full range is the increasing union of these closed images.
```

The union statement holds for every bounded linear map in the theorem, whether its range is closed or not. The surrounding paragraph continues to explain how closedness can be lost.

### L05 — source/chapters/05g_budget_certificates.tex:101

Category: routine_prose.

Before:
```latex
If either factor is zero, every feasible pairing is zero at its maximum and the same formula holds.
```

After:
```latex
If either factor is zero, every feasible pairing is zero and the same formula holds.
```

Removes the redundant phrase at its maximum. In either case all feasible pairings are zero, as the existing argument states.

### L06 — source/chapters/05g_budget_certificates.tex:133

Category: explicit_mathematical_type.

Before:
```latex
Suppose $\widetilde T:H\to Y$ and $\widetilde r\in Y$ satisfy
```

After:
```latex
Suppose the bounded linear map $\widetilde T:H\to Y$ and the datum $\widetilde r\in Y$ satisfy
```

Makes explicit the type required by the operator norm and Hilbert adjoint already used in WR05. Root checked BudgetRobustness.lean, where both operators are continuous linear maps, and approved this clarification.

## Mathematical-token and scope record

L01 and L06 explicitly state bounded linear operator types already required by the formulas. L02 explicitly states the Euclidean source geometry and real scalar target already used in the displayed calculation. These three clarifications were approved by the lead reviewer before editing. L04 corrects the scope of a prose description from “nonclosed range” to “full range”; the increasing-union identity already applies to the whole theorem, and neither its argument nor its hypotheses changes. No operator, relation, sign, coefficient, index, exponent, bound, quantifier, or theorem conclusion was changed.

## Validation

- Every changed passage was reread with its adjacent statement and proof.
- All local cross-references resolve in the assembled source.
- All LaTeX environments are balanced.
- Label order and numbered theorem-environment order are unchanged in every assigned file.
- Full PDF builds were intentionally left to the lead reviewer while parallel edits were in progress.
- No external attribution was changed, so no literature lookup was needed.
- No Lean file was edited or rebuilt by this reviewer.

## Coverage and hashes

- `source/chapters/05a_certificates.tex`: all 117 lines reviewed; final SHA-256 `94510b1a8bfc2eec7e5c6cb8baa73ac412d766c8296d38ba3b476e3e909766f0`.
- `source/chapters/05b_transport_cost.tex`: all 90 lines reviewed; final SHA-256 `9d853abffadfdeddc9804e4640ca9956c38bee681c0657279e7edb8423fcdd57`.
- `source/chapters/05c_iteration.tex`: all 206 lines reviewed; final SHA-256 `9233d3ecefcc2d8f54c5907a95e38e8edf1b885a80e9e740f55b7c2b68090418`.
- `source/chapters/05d_floors.tex`: all 75 lines reviewed; final SHA-256 `45afcd4004318d2336d3c3cf39970c45716e7cdd900920e0f709483ff88e2f7c`.
- `source/chapters/05e_escape.tex`: all 124 lines reviewed; final SHA-256 `2c71d289c6b88061387f62f91f11bd9e15a2f2deb2104d593d1a7987208cfc50`.
- `source/chapters/05f_bounded_realization.tex`: all 154 lines reviewed; final SHA-256 `caeba9d9a2573531f7212474ec7c42ce970d57c9b20bbb92788c3ba6f2bc9da8`.
- `source/chapters/05g_budget_certificates.tex`: all 185 lines reviewed; final SHA-256 `6f653ebd221d1a49547887a1e0ec737ddee7171961a1dc1d3c4a1afcc6e24cd9`.

## Outstanding release gates

Independent review of the changed mathematical prose and final PDF layout review remain with the lead reviewer until assigned. The source is frozen.

## Operational note

An intermediate baseline record was briefly named `limits_source_baseline.json`; it was immediately renamed to the assigned `limits_proofread.json`. No extra review file remains. No computation, build, or test failure occurred in this review scope.
