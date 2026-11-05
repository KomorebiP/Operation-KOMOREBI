# Source correspondence: scope and remaining obligations

Assessed repository base: `f49e00d6088bbc8dca4f8a3a70b232db1eea085b`.
Execution inputs are named in `computation-contract.json`; their exact source
hashes are in the Python run manifests and `SOURCE_INPUTS.json`. The source is
`research/coupled_lab.py`, functions `_index`, `scales`,
`coupled_odd_derivatives`, `disk_majorant` and `certified_evaluation`, plus
`research/family_lab.py:ordinary_taylor_coefficients`.

The typed result theorem is a Lean theorem about `certifiedEvaluationSpec`.
The following source argument is a conditional manual correspondence argument,
reviewed by its author. It is not a mechanized semantics proof of Python.
The finite runtime checks provide separate evidence for an explicit grid.

## Exact conditional claim

For a normal successful return from the pinned `certified_evaluation`, assume
the primitive semantics listed below, immutable exact rational inputs, and no
concurrent changes to imported bindings or objects. Let `p`, `x`, and optional
`S` be the converted rational values and let `N` be the accepted exact integer
last index. Then the seven returned fields agree with `makeEvaluationResult`
for the same successful majorant value, and the checked specification succeeds
with that result. The Lean success theorems then give both real enclosures and
the uniform complex disk error bound.

This implication does not prove successful termination for every admissible
input. In particular, the actual majorant call has fixed limits of 20 steps and
2,000,000 bits. A rational input may be mathematically valid and still exceed
these limits. Unexpected failures such as allocation failure are outside the
typed error model.

## Primitive assumptions, not new proved leaves

| Assumption | Required meaning |
| --- | --- |
| Python execution | Expressions, loops, comprehensions, iteration, scope, tuple unpacking and control flow have their ordinary sequential meanings; no monkeypatching or asynchronous interference. |
| Integer arithmetic | Integers are exact; `range`, `enumerate`, integer exponents, comparisons and arithmetic have their mathematical meanings. |
| Rational arithmetic | Successful `Fraction` conversions produce the stated reduced rationals; operations, powers and comparisons are exact; numerator and positive denominator expose the reduced representation. Floats, if converted, mean their converted rational value. |
| Standard library | `comb` and `factorial` are the usual exact integer functions; `bit_length` is binary width of the absolute integer, with width zero at zero. |
| Containers and aggregation | Lists preserve order and prior values, `append` adds one entry, `reversed` visits the reverse order, and `sum(..., Fraction(0))` is exact rational addition. |
| Return and exception behavior | The literal dictionary has exactly the seven distinct keys and the stated tuple values; uncaught majorant exceptions interrupt the call. |

The model's `last = none` is an abstract invalid-index tag, not the semantics
of every Python object. By contrast, `outer = none` represents the actual
omission/`None` choice of outer radius. Conversion failures and their order,
arbitrary custom objects, subclasses, and exact exception messages or identities
are not formalized.

## Source argument by stage

1. `_index(last)` precedes conversion of scales. The accepted index is an exact
   nonnegative `int`, excluding `bool`. Scale conversion and strict-contraction
   validation precede conversion and validation of `x`. Outer conversion or
   default selection precedes the test `S > x`. These are the same validation
   decisions on already converted values as the typed specification.
2. At the start of derivative iteration `n`, both arrays have length `n` and
   contain the derivatives of odd orders through `2*n-1`. The initial arrays
   `[1]` satisfy the base case. The complete `products` list is built from both
   old arrays before either append occurs. Its `i`th coefficient is
   `comb(2*n,2*i+1)*A_i*B_(n-1-i)` with the corresponding two odd powers.
   Both next sums therefore use the old prefix and implement `derivativeNext`.
   Appending the two values preserves the invariant and gives `N+1` entries.
   Block16 proves that the mathematical paired-array recurrence has exactly
   these derivatives and that division by `(2*n+1)!` gives the ordinary
   coefficients.
3. `ordinary_taylor_coefficients` enumerates the array in increasing order and
   divides by the matching odd factorial. The exact sum at `x` is consequently
   `arrayPolynomial 0 N x` or `arrayPolynomial 1 N x`, respectively.
4. The source calls `disk_majorant(*p,s)` with no resource keywords. Its pinned
   defaults are exactly those in `certifiedEvaluationSpec`. The while-loop
   invariant is `x = Q^len(ladder)*S`, with earlier entries
   `S,Q*S,...,Q^(k-1)*S`, each at least one. The length guard runs before
   append. On normal exit the first small radius is the seed argument.
   The reverse loop computes `guardedFold` on that ladder. Every update is
   checked with the reduced-rational binary width predicate `sizeFits`.
   The seed itself is unchecked. Block17 proves the ladder/fold contract and
   its analytic soundness.
5. After majorant success the source sets `tail = B*(x/S)^(2*N+3)` and constructs
   the seven literal fields. These are the fields of `makeEvaluationResult`.
   A majorant exception prevents dictionary construction. The specification
   computes the pure mathematical arrays in the result constructor after
   majorant success, whereas Python computes the arrays before the call. On
   successful execution, purity makes these orders agree on values. A full
   exception-trace equivalence would additionally need normal completion of
   those earlier array operations; it is not claimed here.

No stage assumes that the finite tests establish a universal recurrence or
analytic theorem. The Python oracle uses the ordinary-coefficient recurrence
and recursive majorant, independently of `comb`, `factorial` and the source's
mutable ladder. It has not been extracted from, or evaluated by, Lean.

## Boundary cases

`N=0` retains one coefficient and uses exponent 3. `x=0` has default `S=1`,
so the majorant is still called. For strict contractions this ladder takes
exactly one step, not arbitrarily many steps; the seed and bit checks still
exist. The near-unit case `q=r=a=b=999/1000`, `x=1`, default `S=2`, exhausts
the 20-step limit. Successful output has a common tail and component-specific
lower endpoints. A majorant failure is never treated as an interval.

## Smallest remaining formal gap

Give the pinned Python functions an explicit operational semantics or a checked
translation, prove the array and ladder loop invariants in that semantics, and
establish the dictionary/exception relation to `certifiedEvaluationSpec`.
State which primitive implementation facts remain trusted. Until that is done,
the safe status is: typed mathematical specification proved; manual source
correspondence conditional on the listed semantics; actual Python behavior
checked only in the recorded finite range.
