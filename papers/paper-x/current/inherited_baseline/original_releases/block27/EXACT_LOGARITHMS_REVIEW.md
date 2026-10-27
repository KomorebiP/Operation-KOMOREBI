# Independent review of the Block 20 exact logarithm computation

Verdict: the implementation and finite assertions are verified in the stated
constructed range. The independent bounded replay passed and reproduced the
original scientific result byte for byte. No mathematical, implementation,
environment, timeout, or resource failure occurred during this review.

The reviewer did not author or modify `checks/exact_logarithms.py`. This review
covers that actual source, `exact_logarithms_contract.json`, the original results,
and the original and independent version-2 manifests. It is separate from the
Lean proof audit. The reviewer also authored the block's linear recovery Lean
module, so this is independent review of the computation author, not a claim of
independence from every component of the release.

## Mathematical and implementation checks

All scalar arithmetic is exact Python integer or `fractions.Fraction` arithmetic.
The script has no project or third-party imports. It uses column vectors and
superdiagonal Jordan blocks. Matrix powers, finite exponentials and finite
logarithms use the declared coefficient signs and factorial denominators. The
annihilating-power assertion runs before either finite series is used. The
zero-dimensional matrix case is outside the declared range.

The direct multiplication, power accumulation, augmented row reduction, and
conjugation routines were inspected. Each constructed inverse is checked on both
sides. `rref(exp(tN)-I) == rref(N)` is a sufficient check of equality of their
kernels over the rational field, and the additional rank assertion agrees with
the Jordan formula `dimension - number of blocks`. This is stronger than merely
comparing ranks. All calls to the shape-dependent routines in this fixed suite
have compatible dimensions; they are not offered as validation of malformed
arbitrary matrices.

The polynomial inverse checks use coefficient convolution rather than matrix
multiplication. The matrix exponential and logarithm are also compared with
closed Jordan entry formulas. These provide orthogonal checks of the tested
identities. Both inverse directions are exercised, including inputs `I+N` for
the exponential-of-logarithm direction and changes of basis across summand
boundaries. The longer logarithm cutoff is checked explicitly. No floating-point
value or tolerance enters a mathematical assertion.

For rectangular maps, the independently checked indexing interpretation is that
the last source basis vector maps to target `e_s`, with
`0 <= s < min(source dimension,target dimension)`. Its successive nilpotent
images give the earlier columns. The code first checks the actual relation
`N_target H = H N_source`, then exponential, logarithmic, and recovered-monodromy
intertwining. This does not enumerate all rational matrices or all rational
intertwiners.

For reconstruction, the diagonal entries are `3^(-z*i)`, so their successive
ratios are `3^z` and the convention is
`rho(t,z) = exp(tN) r(t,z)` with product
`(t,z)(u,w) = (t+3^z u,z+w)`. Rational negative powers are computed as Fraction
powers. The recovery sample `(-2/3,0)` has nonzero scalar and trivial original
action. The script checks that recovery yields both the original monodromy and
the original group action. It separately checks the representation law on all
36 declared parameter pairs, including the exponential factor order.

The boundaries also agree with elementary independent calculations. On a
length-four chain, the coefficient of `N^3` in the quadratic logarithm of
`exp(N)` is `1/6 - 1/2 = -1/3`. The missing cubic logarithm term contributes
`1/3`. For `A=E_(0,1)` and `B=E_(1,2)`, `AB=E_(0,2)` and `BA=0`, so
`exp(A)exp(B)-exp(A+B)=E_(0,2)/2`. The zero sample is the identity for both zero
and nonzero monodromy, and the script actually tests the resulting recovery and
kernel obstruction.

## Exact declared scope

| Assertion family | Scope | Parameter cases |
|---|---|---:|
| Scalar coefficient inverses | Cutoffs 1 through 20, both directions | 20 |
| Logarithm of exponential, recovery, cutoff and kernel checks | 18 partitions, 3 basis variants, 5 nonzero rational samples | 270 |
| Exponential of logarithm | 18 partitions and 3 basis variants | 54 |
| Rectangular intertwiners | Both dimensions 1 through 6, `min(a,b)` generators, 2 samples | 182 |
| Reconstructed action and its recovery | 4 source/target pairs, 3 affine elements | 12 |
| Affine group law | 4 target representations, 9 element pairs | 36 |
| Insufficient logarithm degree | Degrees 2 through 6 on chains of length degree plus 2 | 5 |

The matrix dimension is at most 12 and the nilpotence index at most 12. The
mixed partitions, rational samples, and rectangular shapes in the contract
match the loops. The count 182 equals `2 * sum_{a,b=1}^6 min(a,b)`. Some parameter
cases produce the same operator, especially one-dimensional conjugations; the
counts are tested parameter tuples, not distinct operators. Counts from different
rows are not counts of independent mathematical theorems. There is no random
sampling or silent truncation of the declared loops.

## Independent replay and provenance

The independently chosen execution used the documented program and contract:

```sh
python3 checks/exact_logarithms.py --output checks/logarithms_independent_run/results.json
```

The computation-audit version-2 runner enclosed that command with a 240-second
wall limit, 220-second per-process CPU limit, 1 GiB address-space limit, one CPU
core, and 1 MiB combined-log limit. The conventional thread cap was one. The
script itself does not launch threads or subprocesses. The actual argv and
limits are in `checks/logarithms_independent_run/manifest.json`.

- CPython version: 3.12.13.
- Independent runtime: 9.356552 seconds; exit status zero.
- Source SHA-256: `20dbbb7a5bca8559df52d06262f6723bdf3f7e2969e2d04449eb9e64ffc7a28d`.
- Scientific result SHA-256: `ebbeb29c3489b7fbe5a6471e894ee461431c69fe4ec3fb96da7815fae5eef7b2`.
- Contract SHA-256 at review: `8c3a03de413bf082cbbd0d284e85aa226f8164de28b70052c8d0151c25468fc0`.
- Both original and independent manifests validated with `--root`.
- Input hashes before and after the independent run match the frozen source.
- The independent result, original result, and root `exact_logarithms.json` are
  byte-identical.
- The scientific result's embedded source hash matches the actual script bytes.

The source's complete nonstandard dependency closure is empty; the only imported
modules are part of the recorded CPython standard library. There is no usable
Git commit, so the actual source and result bytes are pinned by SHA-256 rather
than inferred from a revision name. The standard library implementation is not
kernel verified by this audit. A deterministic replay can reproduce an error,
which is why this review also inspected the implementation, conventions,
independent formulas, and hand-computable boundary values.

## Interpretation

The finite computation supports the nilpotent logarithm construction and its
recovery formulas on this declared deterministic suite. It does not establish
universal algebraic identities, arbitrary-dimensional recovery, or any
arithmetic Galois-to-Weil-Deligne attachment. Those universal algebraic claims
have separate Lean proofs. No coefficient or Hodge-Tate period comparison,
analytic convergence, or novelty is tested here. The full arithmetic status
must remain 15 checked claims and 5 partial claims.
