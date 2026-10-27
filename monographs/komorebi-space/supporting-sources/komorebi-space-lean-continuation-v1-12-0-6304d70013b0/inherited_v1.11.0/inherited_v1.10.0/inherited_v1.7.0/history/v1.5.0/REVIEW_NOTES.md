# Komorebi Space bounded-budget expansion and review — 1.5.0

**Recorded:** 2026-10-12T16:02:20.514528+00:00

## Result

The monograph expands from 105 to **125 pages**, with six parts, 33 numbered sections, and five appendices. The visual guide has **39 pages and 36 plates**, and the Lean/evidence guide has **34 pages**. The final reader set totals **198 pages**. Four added chapters provide twelve separately indexed written theorem groups. The formal baseline is unchanged.

## Mathematical development

WR01 proves bounded approximate feasibility for fixed bounded linear Hilbert maps using a complete weak-subsequence argument. WR02 gives the exact finite energy identity for minimum-norm points of nested closed affine constraint sets and proves strong realization if and only if their norms stay bounded. An arbitrary bounded approximate sequence need not converge strongly.

WR03–WR05 retain an actual correction budget. Every finite budget has an attained residual minimum, even when the full range is not closed. The dual support witness is proved directly, including degenerate cases. Model uncertainty changes the budget profile by at most delta + eta*M on one fixed protected kernel.

WR06–WR09 derive the quadratic normal equation in that kernel. The Gram matrix of nonorthogonal coordinates is retained. The energy identity certifies uniqueness. Four cases distinguish the orthogonal residual floor from actual attainment of the projected datum. A regularized path can have vanishing residual and weighted penalty while correction norms diverge. The sharp data-noise coefficient is 1/(2*sqrt(alpha)).

WR10–WR12 compute the entire regularized diagonal family, rational enclosures for its infinite energies, and the limiting budget product pi/4. Hard prefix repair has limiting product one. The plotted finite points use each method's own natural budget; the full proof supplies the matched-budget conclusion. A separate attainable datum yields a deterministic delta^(1/3) bound under the stated ceiling parameter rule. None of these results is presented as a universal performance law or a new Lean instance.

## Scope and exact software

The retained catalogue has **80 KS entries and 211 references**. **WR01–WR12 have full printed proofs but no new Lean declarations.** The metadata checker enforces that distinction and hashes the written sources. It is not a mathematical proof checker.

The exact rational solver `examples/budgeted_repair.py` preserves the declared observable, retains the kernel Gram matrix, handles a fully protected zero-dimensional kernel, distinguishes measured fit from actual candidate residual, and returns a budget witness without rounding its square-root normalization. Its finite input validation rejects floats, malformed matrices, and nonpositive regularization.

Six suites passed **178,754 assertions**. The new suite passed **34,388**. It covers 2,187 two-dimensional systems with an independent adjugate oracle, 486 protected systems, 405 independent ambient KKT checks, 125 nested affine problems, 162 scalar uncertainty cases, 48 rational diagonal-tail windows, and 30 parameter-choice cases. Nine stronger-claim controls and ten invalid-input cases were rejected as intended. These are finite regression scopes, not proof by extrapolation.

## Formal preservation

All **156 formal-tree files** match the predecessor. The original frozen archives also pass their integrity checks. The accepted v1.2.0 result remains 138 production modules plus one root, 139 compiler targets, 4,745 audited declarations, and 1,507 explicit theorem/lemma declarations including auxiliaries. **No new Lean compilation or axiom audit was executed.** No formal source was edited to evade this boundary.

## Build and review

The accepted build receipt is `audit/regularization/build06.json`. It records exit code zero. The new figure sources, examples, and all six suites ran in that build. Mechanical preflight passes for the final three PDFs. All 198 final pages were rendered, draft contact sheets were inspected, and changed final pages were checked against their mathematical sources. The exact reviewed/unchanged pixel accounting is in `audit/visual_review.json`, bound to final PDF hashes. All fonts are embedded; no standalone font files are distributed.

The six new figures show finite energy bounds, the reachable ellipse and support witness, budget-dependent uncertainty, the regularization noise filter, smooth escaping coordinate profiles, and exact interval enclosures of budget products. Colors carry no unstated theorem. Plotting uses floating point only for display of explicit formulas and rational enclosure endpoints.

## Failures retained

Build01 failed on a literal caret in a generated TeX table, corrected to mathematical notation. Build02 was interrupted without a terminal receipt and is never counted as a successful build. Build03 passed mechanically but was superseded after review. Build04 also passed, then was superseded after two forced chapter breaks were removed. Build05 passed, but a further review found figures collected on isolated float pages. The six new main-text figures were changed to inline placement. The final build06 passed with a terminal zero exit code. Logs, receipts, and their portable paths are retained in `audit/regularization/attempts.json`.

Review corrected stale edition wording in the evidence guide, replaced an unsupported frequency interpretation of a diagonal coordinate by the actual coordinate statement, moved two isolated figures into their discussion, removed a short trailing reference page, and allowed two chapters to flow onto the preceding pages rather than leave short continuations. An attempted read of nonexistent `checks/manifest.py` failed; the existing manifest tool was found and used. Those lookup and interrupted-execution failures are not pass evidence.

## Remaining work

The twelve WR groups need actual new Lean formalization before formal coverage can be claimed. The natural order is bounded feasibility and nested affine projections, then the budget support theorem and protected quadratic repair, followed by limit and diagonal results. The existing closed KS54–KS58 list is unaffected. Universal-view, higher-stack, arbitrary semantic-realization, independent-kernel, full-source mathlib, native Windows, and universal Python-refinement claims remain excluded.
