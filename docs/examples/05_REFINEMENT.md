# 5. Refine a signal into smaller packets

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: polyphase](../GLOSSARY.md#polyphase) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Take the finite list

```math
x=(1,2,3,4,5,6,7,8).
```

Index its entries from zero through seven. Thus $x_0=1$ and $x_7=8$.
We only rearrange this finite list. No boundary extension or convolution is
needed.

## Separate even and odd addresses

For remainder $r=0,1$, collect the entries $x_{2k+r}$:

```math
x^{(2)}_0=(1,3,5,7),\qquad x^{(2)}_1=(2,4,6,8).
```

These are compact coordinate lists. To view them as vectors in the original
eight positions, put zeros in the other slots:

```math
P_0x=(1,0,3,0,5,0,7,0),\qquad
P_1x=(0,2,0,4,0,6,0,8).
```

Their sum is $x$.

## Refine from two address classes to four

Now collect entries $x_{4k+r}$:

| Remainder $r$ | Original indices | Compact list |
|---|---|---|
| 0 | 0, 4 | $(1,5)$ |
| 1 | 1, 5 | $(2,6)$ |
| 2 | 2, 6 | $(3,7)$ |
| 3 | 3, 7 | $(4,8)$ |

Let $F_r$ select those positions in the original eight-dimensional space.
The even positions split into remainders 0 and 2. The odd positions split into
remainders 1 and 3. Therefore

```math
P_0=F_0+F_2,\qquad P_1=F_1+F_3.
```

For example,

```math
F_0x=(1,0,0,0,5,0,0,0),\qquad
F_2x=(0,0,3,0,0,0,7,0).
```

Adding these gives $P_0x$. Interleaving the four compact lists recovers
$(1,2,3,4,5,6,7,8)$.

## What happens if one packet is dropped?

Discard remainder 2 and retain the other three. The reconstructed list is

```math
\widehat x=(1,2,0,4,5,6,0,8).
```

The residual, defined here as original minus reconstructed, is

```math
r=x-\widehat x=(0,0,3,0,0,0,7,0),\qquad
\|r\|_2^2=3^2+7^2=58.
```

Rearranging all packets is exact. Discarding a nonzero packet changes the
signal, and the residual records the missing values.

## Try it

Keep only remainders 0 and 2.

**Answer:** The retained signal is $(1,0,3,0,5,0,7,0)$. Its residual is
$(0,2,0,4,0,6,0,8)$, whose squared Euclidean norm is
$4+16+36+64=120$.

**Continue reading:** [Refinement](../GLOSSARY.md#refinement),
[residue class](../GLOSSARY.md#residue-class), and the
[signal realization guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization).

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Refinement](../GLOSSARY.md#refinement) · [Coarsening](../GLOSSARY.md#coarsening) · [Polyphase decomposition](../GLOSSARY.md#polyphase) · [Residue class](../GLOSSARY.md#residue-class) · [Compatibility](../GLOSSARY.md#compatibility)

Read Paper II for refinement and Paper V for signal and polyphase constructions.

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](../works/paper-ii.md#read) · [Written proofs](../works/paper-ii.md#written-proofs) · [Lean coverage](../works/paper-ii.md#lean) · [Code and setup](../works/paper-ii.md#code) · [Evidence](../works/paper-ii.md#evidence)

### Paper V: Polyphase Signal Calculus

[Read](../works/paper-v.md#read) · [Written proofs](../works/paper-v.md#written-proofs) · [Lean coverage](../works/paper-v.md#lean) · [Code and setup](../works/paper-v.md#code) · [Evidence](../works/paper-v.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: refinement()](../../tools/check_hand_examples.py#L118). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Assemble transfer blocks](04_TRANSFER.md)
- [Next: Use redundant coordinates](06_REDUNDANT_COORDINATES.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#refinement)
