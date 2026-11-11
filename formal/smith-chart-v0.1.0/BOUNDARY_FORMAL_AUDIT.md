# Formal boundary continuation: self-review

This is a review by the author of the continuation, not an independent
review. The exact Lean declarations are in [SmithBoundaries.lean](SmithBoundaries.lean);
[run14](verification/run14/receipt.json) records the compiler, inputs,
direct cached imports, axiom inventory, and replay outcome.

## Claim card: discrete cyclic reachability

For `N > 0`, let `omega N = exp(2*pi*I/N)`. Given complex `start` and
`target`, if `start != 0`, the formalized claim is

```
(exists k : Nat, k < N and target = omega N ^ k * start)
  iff (target / start) ^ N = 1.
```

`cyclic_reachable_iff` proves both directions. `zero_start_reachable_iff`
separately proves that the zero start reaches exactly zero. These statements
are for the finite canonical phase orbit; they do not assert that a point is
reachable by an arbitrary matching network. To interpret them as points on a
passive Smith chart, the user must additionally impose the appropriate disk
and finite-impedance hypotheses from `SmithGeometry.lean`.

| Obligation | Self-review | Evidence and boundary |
| --- | --- | --- |
| Necessity | Passed | Cancel the nonzero start and use the proved exact order of the canonical root. |
| Sufficiency | Passed | The pinned Mathlib declarations `Complex.isPrimitiveRoot_exp` and `IsPrimitiveRoot.eq_pow_of_pow_eq_one` enumerate all Nth roots of unity; multiplication by `start` recovers `target`. |
| Zero and minimal order | Passed | The zero start is a separate theorem. At `N=1` the criterion requires `target=start` for nonzero start. |
| Concrete quarter turn | Passed | Lean proves infeasibility for order 2 and existence for order 4 from start `1/2` to target `I/2`. The guide's identification of the order-4 index as `1` is an elementary written calculation. |
| Physical realization | Out of scope | No frequency-domain circuit, physical transmission line, floating-point code, or arbitrary network is modeled by the orbit theorem. |

## Other formal witnesses

`noncoprime_projector_counterexample` compares the coefficient of degree 4:
the nested residue-zero projectors for orders 2 and 4 keep it, whereas the
order-8 projector removes it. The guide's values at `t=1/2` are checked by
the separate exact-rational computation, rather than by a polynomial
evaluation theorem here.

`two_sample_equal_but_not_identical` checks that the two displayed complex
polynomials agree at `-1/2` and `1/2` and differ at zero.
`second_sample_positive_real` proves its real part exceeds `11/16` for every
complex `t` with `norm t < 1`; the constant function has real part one.
Polynomial analyticity is used in the written explanation. The theorem for
an arbitrary finite list of sample points is not formalized by these results,
and positive real part as a function of the reflection coordinate is not a
physical circuit-realizability theorem.

The proofs use the pinned Mathlib and its precompiled caches, which are not
all rebuilt or exhaustively hashed by replay. Source-to-formal mapping,
interpretation, and this review are self-review. The Lean proof does not
recover later ChatGPT-only material that was unavailable to the session.
