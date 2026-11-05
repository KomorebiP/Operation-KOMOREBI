# SF-LEAN-B20: source-expression interpretation and checked arithmetic lowering

The selected Python arithmetic now has a typed Lean expression interpreter
separate from the Block19 source-to-term printer. Nineteen universal statements
prove that interpreting the source-derived expression data gives the same
products, weights, normalized coefficients, partial sums, majorant seed/update,
defaults, tail and dictionary as the already refined source operations.
The composed expression-based result retains the actual-function enclosures.

The new modules are [the interpreter](../../lean/CoupledExpressionSemantics.lean),
[the source-derived data](../../lean/CoupledSourceExpressions.lean) and
[the lowering/composition proof](../../lean/CoupledExpressionRefinement.lean).
These add 19 registered supporting theorems, bringing the total to 536 names,
including 39 inherited finite-core names. The count is not a count of independent
discoveries or a whole-book completion percentage.

## Exact advance and limits

Block19's arithmetic printer is checked against a separate semantic evaluation
for every value of each expression's source variables. The emitter does not
call that printer. Kernel reduction checks the many definitional equalities;
array/result composition uses the previously proved operational and analytic
theorems. Both scale rows retain their independently named environments.

This is a check of the selected expression profiles, not a verified compiler
for every Python expression or statement. The Python parser, source selector
and expression-data emitter remain trusted, as does the fixed statement/control
template. Standard integer/Fraction, container, type-tag and library primitive
semantics remain assumptions. Natural subtraction is used with Block19's proved
reachable nonnegative-index contract; arbitrary negative Python indices are
not silently given natural-number semantics. Unexpected machine failures and
side-effectful objects remain outside the mathematical execution model.

The original calculator and mathematical manuscripts are unchanged.
Read [TARGET.md](TARGET.md) and [SELF_REVIEW.md](SELF_REVIEW.md) for the exact
scope, dependency graph, conditions and self-review provenance.

## Accepted evidence

All 29 final replay stages pass, including source binding, ten
expression-mutation controls, the retained 24 binder-mutation controls, three
fresh compilations, nineteen exact theorem axiom audits, three same-kernel
module replays, five required rejections and one positive fixture. Only
`propext`, `Classical.choice` and `Quot.sound` occur in the new theorem audits.
The interpreter and expression-data modules add definitions rather than named
theorems. Mutation tests are finite rejection checks, not a proof of the parser
or emitter for all possible programs.

Twenty coupled modules are inherited after source, object, compiler and recursive
receipt-chain checks. Their 478 theorem names and the 39-name finite core retain
their earlier evidence. Mathlib is cached and not freshly rebuilt; replay uses
the same kernel and review is author self-review. Lean 4.34.0-rc2, Python 3.12.14
and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 are recorded.

[Final receipt](evidence/receipt.json) · [Expression binding](evidence/expressions.json)
· [Expression controls](evidence/expression-controls.json) · [Declaration map](declarations.json)

The earlier Block18 calculator checks remain inherited evidence for unchanged
source hashes. Intermediate emissions and development compiles are diagnostics.
No numerical sampling is substituted for the universal lowering statements.

## Publication and continuation

This companion prepares Blocks18-20 for GitHub and the reader website, including
their exact proof sources, records, source-inspector selection, current guides
and status catalogue. The [publication inventory](PUBLICATION_MANIFEST.json)
binds later reader selections without altering original import receipts.
Historical local/unpublished wording in Block18/19 is an as-of record, not the
current publication status; use the maintained current/ guide for the restart.

Next, extend the typed interpreter to the remaining statement/control fragment
or prove the AST extraction/lowering boundary itself. The remaining parser and
primitive assumptions are explicit; no unconditional CPython verification is
claimed. Other J degree/denominator/symmetry, ancillary F/H, I and broad A-E
remain; ordinary type convergence and G.2's guard retain their prior conditions.

## Reproduce

```text
python tools/emit_python_expressions.py --output NEW_EXPRESSION_BINDING.json
python tools/check_expression_binding.py --output NEW_EXPRESSION_CONTROLS.json
python tools/verify_coupled_expression_refinement.py --toolchain KIT --mathlib MATHLIB --work NEW_EXTERNAL_DIRECTORY --git GIT --dependency-build BLOCK19_BUILD --dependency-receipt BLOCK19_RECEIPT
```

All output paths must be fresh. Omit both dependency options for a complete
fresh coupled-module build. The runners perform no dependency installation.
Exact executed argv, input/output hashes, timings and environment are in the receipt.
