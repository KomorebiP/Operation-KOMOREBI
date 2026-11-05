# SF-LEAN-B19: Python source binding and imperative refinement

The previous manual loop/dictionary argument is now a source-bound imperative
model with a universal Lean refinement proof. The model has exactly the same
dictionary or modeled error as `certifiedEvaluationSpec`, for every input in
its domain. It is total and deterministic as a mathematical execution model.
Every successful return uniquely represents a typed result with both real
enclosures and the complex disk error bound.

**The actual-Python conclusion is conditional on an explicit trust boundary:**
the Python AST parser, the closed-fragment binder/control template, and standard
Python/Fraction/integer/container primitives. These components have not been
proved correct in Lean. This is a checked source binding and proved imperative
refinement, not an unconditional verification of CPython or a verified compiler.

## What is proved

The two new modules are
[the source-bound operational translation](../../lean/CoupledPythonSource.lean)
and [its universal refinement proof](../../lean/CoupledPythonRefinement.lean).
The latter contains 35 named theorems. The recorded total becomes
517 names, including 39 inherited finite-core names; this is not a
count of independent discoveries or a whole-book completion percentage.

* The actual derivative loop's separate arrays and eagerly materialized
  products agree with the derivative recurrence. Both rows use the correct
  old prefix. Every array subscript and integer-subtraction index is safe.
* Enumerated division by the odd factorial and the following exact sum agree
  with the already proved ordinary arrays and polynomials.
* The while-loop accumulator, first-small stopping, pre-append length guard,
  reverse iteration and every post-update bit check refine the guarded
  majorant. The seed remains unchecked, as in the source.
* The exact seven keys, integer/rational types, tuple endpoints, component
  order, defaults and tail expression are connected to the typed result.
  The dictionary encoding is injective, so it recovers a unique typed result.
* `source_evaluation_iff` proves equality of outcomes in both directions,
  rather than only assuming a successful trace. Separate totality and
  determinism theorems rule out a vacuous relation that excludes difficult paths.
* The raw preparation layer distinguishes an exact nonnegative integer from
  booleans/other index types. It takes Fraction conversion as an explicit
  parameter, validates in source order and propagates conversion failures.
  `raw_source_return_encloses` and `raw_source_return_disk_error` attach the
  actual-function bounds to every normal raw-model return at its converted
  rational point.

## Binding to the actual files

[bind_python_source.py](../../tools/bind_python_source.py) pins both original
Python files and checks every selected function's complete non-docstring AST
shape. Arithmetic, powers, coefficient normalization, defaults and literal
dictionary fields are translated into the Lean artifact. Unexpected control
flow, altered literals or a different generated artifact fail the check.

The selected call closure is `_index`, `scales`, `coupled_odd_derivatives`,
`ordinary_taylor_coefficients`, `disk_majorant` and `certified_evaluation`.
The original calculator and manuscripts are unchanged. The exact byte hashes
remain `dff2a80db6f459e52dda45bc3399e0be45edf287df2efbeb1a56b57d38dfe20a`
and `7b546c1cd3159bb59634a3306c116719cd8d8d368c0046af90270c709b08cc8e`.

The binder/control template is a small trusted translation implementation.
Source binding does not turn it into a verified compiler. Its source and all
supporting patterns/templates are hashed into the formal receipt and receive
an explicit self-review in [SELF_REVIEW.md](SELF_REVIEW.md).

## Verification

All **24 final replay stages pass**: dependency-version checks, source
binding and mutation checks, two fresh compilations, exact theorem axiom
audits, two same-kernel module replays, five required rejections and one
positive fixture. All 35 new theorem audits contain only `propext`,
`Classical.choice` and `Quot.sound`. The source module adds operational
definitions and inductive relations, not additional named theorem counts.

The 24 source-mutation controls deliberately bypass whole-file pin rejection.
They test the structural/arithmetic binder itself: changed exponents, indices,
normalization, scale rows, seed/update signs, forward folding, guard boundaries,
default limits, dictionary keys/values, bool acceptance and lazy shared products
are all rejected or produce a different artifact. Two positive controls pass.
This finite test is not proof of translator correctness for arbitrary programs.

Eighteen coupled dependency modules are reused after checking their source and
object hashes and the recursive successful Block18/Block17 receipt chain with
the same compiler/checker bytes. Their 443 theorem names and the 39 finite-core
names retain inherited evidence. Mathlib is cached, not freshly rebuilt or
independently verified. Review is author self-review, and the replay uses the
same Lean kernel. Python 3.12.14, Lean 4.34.0-rc2 and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` are recorded in the receipts.

See [the final receipt](evidence/receipt.json),
[source binding](evidence/binding.json),
[mutation results](evidence/binding-controls.json) and
[the declaration map](declarations.json). The earlier 507 calculator checks
belong to Block18 and remain inherited evidence for unchanged Python sources;
they were not relabeled as fresh tests in this block. Development compiles and
intermediate bindings are diagnostics, not acceptance evidence.

## Remaining trust and exact limits

The primitive contract assumes exact Fraction/integer operations, exact
`comb`, `factorial` and binary width, standard sequential list/dictionary
semantics, faithful exact-type tagging, pure successful conversions and
idempotent normalization of Fraction values. It excludes monkeypatching,
concurrent mutation and hostile object side effects. The raw theorem is about
the converted rational value; it does not separately verify a custom object's
intended mathematical meaning.

Validation/conversion/resource errors are modeled explicitly. Exact Python
validation-exception object identity, unexpected allocation failure,
interruptions and the internals of CPython/stdlib are outside the theorem.
Mathematical model totality is not a wall-clock or memory guarantee. Removing
the parser/binder/primitive trust boundary is a separate interpreter/compiler
or library-verification project, not a consequence of passing this replay.

The source-model phase of [TARGET.md](TARGET.md) is complete with that stated
boundary. [ROUTES.md](ROUTES.md) preserves alternatives and their resumption
conditions. Broader Appendix J, F/H, I and A-E obligations retain their prior
scopes; ordinary type convergence stays conditional and G.2 retains its guard.
The work remains local and unpublished on repository base
`f49e00d6088bbc8dca4f8a3a70b232db1eea085b`, extending local SF-LEAN-B18.

## Reproduce

From `monographs/special-functions/`:

```text
python tools/bind_python_source.py --output NEW_BINDING.json
python tools/check_python_source_binding.py --output NEW_CONTROLS.json
python tools/verify_coupled_python_refinement.py --toolchain KIT --mathlib MATHLIB --work NEW_EXTERNAL_DIRECTORY --git GIT --dependency-build BLOCK18_BUILD --dependency-receipt BLOCK18_RECEIPT
```

Use fresh output paths. The dependency options reuse only the exact receipt-bound
objects; omit both for fresh compilation of all twenty coupled modules. No
dependency download is performed. The actual argv, source/object/output hashes,
platform and timings are retained in the receipt.
