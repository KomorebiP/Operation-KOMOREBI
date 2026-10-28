# 9. Round a binary number by hand

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: precision](../GLOSSARY.md#precision) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Consider positive binary floating-point numbers with three significant bits,
including the leading one. We stay away from exponent limits and subnormal
values. The rounding rule is nearest, with exact ties going to the candidate
whose last retained significand bit is zero.

## List the representable values in one interval

Between one and two, the three-bit significands are

| Binary | Exact value |
|---|---|
| $1.00_2$ | $1$ |
| $1.01_2$ | $1+1/4=5/4$ |
| $1.10_2$ | $1+1/2=3/2$ |
| $1.11_2$ | $1+1/2+1/4=7/4$ |

The spacing within this interval is $1/4$.

## Round an exact midpoint

Take

```math
x=\frac{13}{8}=1+\frac12+\frac18=1.101_2.
```

Its two nearest three-bit neighbors are $3/2=12/8$ and $7/4=14/8$.
Both are at distance $1/8$.

The lower candidate has retained significand bits $110$, whose integer value
six is even. The upper has bits $111$, whose integer value seven is odd.
Ties to even therefore chooses

```math
\widehat x=\frac32,\qquad
\widehat x-x=\frac{12}{8}-\frac{13}{8}=-\frac18.
```

The stored result is below the exact value. A numerical ternary return using
the stored-minus-exact convention would have negative sign.

## Change the precision

With four significant bits, $1.101_2$ is representable, so this particular
number is stored exactly. That does not mean every rational number becomes
exact at four bits.

For instance, $1/10$ has reduced denominator ten. Every finite binary fraction
has a reduced denominator that is a power of two. Since ten has a factor of
five, $1/10$ has no finite binary expansion at any finite precision.

Precision is the capacity of the representation. Accuracy depends on the
value, the operation and its error.

## Spacing is local

In the next interval, from two to four, three-bit values have the form
$1.xx_2\times2$. Their spacing is $1/2$, twice the previous spacing.
An ULP must be interpreted at a specified precision and exponent.

## Try it

Round $11/8=1.011_2$ to three significant bits using the same rule.

**Answer:** It is halfway between $5/4=10/8$ and $3/2=12/8$. The
significands are $101$ and $110$. The even choice is $3/2$, so the
stored-minus-exact error is $+1/8$.

**Continue reading:** [Dyadic rational](../GLOSSARY.md#dyadic-rational),
[ULP](../GLOSSARY.md#ulp), and
[Polyphase Float's numerical glossary](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md).
Library range behavior, error sentinels and diagnostic flags have additional
contracts beyond this small rounding model.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Precision](../GLOSSARY.md#precision) · [Dyadic rational](../GLOSSARY.md#dyadic-rational) · [Rounding](../GLOSSARY.md#rounding) · [ULP](../GLOSSARY.md#ulp) · [Numerical ternary](../GLOSSARY.md#ternary) · [Exact](../GLOSSARY.md#exact) · [Numerical](../GLOSSARY.md#numerical)

Paper IX supplies dyadic arithmetic background. The rounding implementation and its contracts belong to Polyphase Float.

### Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation

[Read](../works/paper-ix.md#read) · [Written proofs](../works/paper-ix.md#written-proofs) · [Lean coverage](../works/paper-ix.md#lean) · [Code and setup](../works/paper-ix.md#code) · [Evidence](../works/paper-ix.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/chapters/06_arithmetic_ranges.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: binary_rounding()](../../tools/check_hand_examples.py#L182). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Previous: Average with unequal weights](08_WEIGHTED_AVERAGES.md) · [Next: Find a kernel and its fibers](10_KERNELS.md) · [All examples](../HAND_WORKED_EXAMPLES.md) · [Topic map](../LEARNING_MAP.md#rounding)
