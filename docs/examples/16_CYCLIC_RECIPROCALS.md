# 16. Split reciprocal coefficients into cyclic packets

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: formal reciprocal](../GLOSSARY.md#formal-reciprocal) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

This example introduces the coefficient operations behind Paper IV. Work over
the rational numbers and seek the formal reciprocal of $A(z)=1+z+z^2$.

## Solve one coefficient at a time

Write $B(z)=\sum_{n\ge0}b_nz^n$ and require $A(z)B(z)=1$. Comparing
coefficients gives $b_0=1$, $b_1+b_0=0$, and, for $n\ge2$,

```math
b_n+b_{n-1}+b_{n-2}=0.
```

The first six calculations are

| Degree | Calculation | Coefficient |
|---|---|---|
| 0 | Constant product must be one | $b_0=1$ |
| 1 | $b_1=-b_0$ | $-1$ |
| 2 | $b_2=-b_1-b_0$ | $0$ |
| 3 | $b_3=-b_2-b_1$ | $1$ |
| 4 | $b_4=-b_3-b_2$ | $-1$ |
| 5 | $b_5=-b_4-b_3$ | $0$ |

Thus the truncation through degree five is $B_{<6}(z)=1-z+z^3-z^4$.

## Check exactly what the truncation proves

Multiplying the two polynomials gives

```math
(1+z+z^2)(1-z+z^3-z^4)=1-z^6.
```

Every positive-degree coefficient below degree six vanishes. The product
equals one modulo $z^6$, but the degree-six discrepancy is $-1$.
The full formal identity follows instead from

```math
\frac{1}{1+z+z^2}=\frac{1-z}{1-z^3}
=(1-z)\sum_{k\ge0}z^{3k}.
```

The last expression can also be evaluated as a convergent complex series
when $|z|<1$. The finite polynomial calculation alone did not establish
an identity at arbitrary complex inputs.

## Select coefficients by residue class

Keep exponents congruent to $0$, $1$ and $2$ modulo three:

```math
P_0B_{<6}=1+z^3,\qquad P_1B_{<6}=-z-z^4,\qquad P_2B_{<6}=0.
```

Their sum recovers the truncation. Each selector is idempotent, and distinct
selectors annihilate each other because they keep disjoint exponent classes.

Over the complex numbers, let $\omega$ be a primitive cube root of unity.
The same selection has the root-filter formula

```math
P_rf(z)=\frac13\sum_{k=0}^{2}\omega^{-rk}f(\omega^kz).
```

On a monomial $z^n$, the multiplier is one when $n-r$ is divisible by three
and zero otherwise, using $1+\omega+\omega^2=0$.

## Try it

Compute $b_6,b_7,b_8$ and check the next truncation.

**Answer:** They are $1,-1,0$. Hence $B_{<9}=B_{<6}+z^6-z^7$ and
$A(z)B_{<9}(z)=1-z^9$. The coefficient pattern repeats in blocks of three.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Coefficient](../GLOSSARY.md#coefficient) · [Power series](../GLOSSARY.md#power-series) · [Truncation](../GLOSSARY.md#truncation) · [Formal reciprocal](../GLOSSARY.md#formal-reciprocal) · [Coefficient convolution](../GLOSSARY.md#convolution) · [Root of unity](../GLOSSARY.md#root-of-unity)

This coefficient model introduces cyclic projection and reciprocal recursion in Paper IV. Its finite product check does not address the paper’s analytic growth or spectral-zero results.

### Paper IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

[Read](../works/paper-iv.md#read) · [Written proofs](../works/paper-iv.md#written-proofs) · [Lean coverage](../works/paper-iv.md#lean) · [Code and setup](../works/paper-iv.md#code) · [Evidence](../works/paper-iv.md#evidence)

**Source passages:**

- [Paper IV: cyclic projection](../../papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex#L325)
- [Paper IV: reciprocal powers](../../papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex#L918)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#cyclic-coefficient-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: cyclic_reciprocals()](../../tools/check_hand_examples.py#L277). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Compose typed operations](15_TYPED_PATHS.md)
- [Next: Calculate quantum measurement and dephasing](17_QUANTUM_MEASUREMENT.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#cyclic-reciprocals)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
