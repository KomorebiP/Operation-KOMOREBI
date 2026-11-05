# SF-LEAN-B20 self-review

Primary verdict: **proved as written** for the typed expression interpretation
and its nineteen universal lowering/composition statements. The actual-Python
conclusion remains **conditional on the named parser/extractor, statement
template and standard primitive semantics**. Review is author self-review.

The source selector is frozen from Block19. A new emitter writes typed
expression data without using Block19's arithmetic string printer. The generic
Lean evaluator interprets that data. The refinement module compares the two
representations for all values of the source variables, rather than sampling
rational inputs. Equality is often definitional: the kernel checks that the
interpreter computes exactly the separately lowered operation. These are
registered supporting theorems, not nineteen independent discoveries.

## Obligations

| Obligation | Finding |
| --- | --- |
| Actual arithmetic selection | Checked source pin and complete masked-function shape; typed data come from the same selected expression sites. Parser, selector and emitter remain trusted. |
| Separate interpretation | Passed: NatExpr, RatExpr and ValueExpr have explicit Lean evaluators; the data emitter does not call the old arithmetic printer. |
| Arithmetic domain | Passed for exact rational arithmetic and nonnegative indices. No floating evaluation or tolerance appears. |
| Subtraction/index semantics | Conditional on the reachable-domain contract already proved in Block19: no negative Python subscript or negative natural exponent is silently accepted. This is not a generic semantics of Python subtraction. |
| Array and row order | Passed: product entries and each independently named scale row agree with the source operations for arbitrary arrays/scales; composition gives the proved canonical derivative arrays. |
| Factorials and partial sums | Passed: interpretation agrees with source factorial normalization and enumeration; Block19 supplies nonzero factorials and polynomial correspondence. |
| Seed/update/defaults | Passed: expression interpretation agrees with source operations. Resource defaults are exactly 20/2,000,000 and last index 24. |
| Tail and N=0 | Passed: exponent is 2N+3, including 3 at N=0. |
| Dictionary | Passed: exact seven keys, values and tuple endpoints agree with the unique typed encoding. |
| Analytic conclusion | Passed under successful typed evaluation via inherited Block18-19 theorems; no result constructor is asserted to certify an arbitrary majorant. |
| Source mutation controls | Finite only: ten emitter mutations and two positive controls, plus the retained binder controls. They do not prove a general compiler correct. |
| Trust reduction | The kernel checks the selected arithmetic lowering against the interpreter. Faithful AST extraction and the statement/control template remain assumptions; the entire source translator is not verified. |

Dependency graph: pinned source -> trusted AST selection/data extraction ->
typed expression data -> generic Lean interpretation -> universal lowering
equalities -> Block19 operational refinement -> Block18 typed evaluation ->
actual canonical-function bounds. The separate source-to-term printer is the
comparison target, not an assumed theorem of arithmetic equality. No circular
use of the desired enclosure is needed to prove a lowering equality.

No new external theorem or numerical approximation is used. Native library
dependencies and earlier modules retain their explicitly inherited evidence;
new compiles, axiom audits, kernel replays and controls are distinguished in
the final receipt. CPython, arbitrary side-effectful objects and unexpected
machine failures remain outside this mathematical execution contract.
