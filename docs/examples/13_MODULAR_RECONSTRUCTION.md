# 13. Reconstruct an integer from residues

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: Chinese remainder theorem](../GLOSSARY.md#chinese-remainder) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Find an integer with remainder $2$ modulo $3$ and remainder $3$ modulo $5$:

```math
x\equiv2\pmod3,\qquad x\equiv3\pmod5.
```

The moduli are coprime. The answer is a unique class modulo $15$, not a
unique unrestricted integer.

## Construct residue selectors

The number $5$ vanishes modulo $5$. Its residue modulo $3$ is $2$, whose
inverse modulo $3$ is $2$ because $2\cdot2\equiv1$. Thus take $e_3=10$.
Likewise, $3$ has inverse $2$ modulo $5$, so take $e_5=6$.

| Selector | Modulo 3 | Modulo 5 |
|---|---|---|
| $e_3=10$ | 1 | 0 |
| $e_5=6$ | 0 | 1 |

Combine the requested residues:

```math
x\equiv2e_3+3e_5=20+18=38\equiv8\pmod{15}.
```

The representative in $0\le x<15$ is $8$. Indeed, $8=2\cdot3+2$
and $8=1\cdot5+3$. All integer solutions are $8+15k$ with integer $k$.

## Check the packet pattern in the residue ring

In $\mathbb Z/15\mathbb Z$,

```math
10^2\equiv10,\quad6^2\equiv6,\quad10\cdot6\equiv0,\quad10+6\equiv1.
```

Multiplication by these classes therefore gives two idempotent selectors.
These are congruences in a ring. For example, $10^2=10$ is false as an
ordinary integer equality. The ring $\mathbb Z/15\mathbb Z$ is not a field.

## What changes when moduli are not coprime

For moduli $4$ and $6$, the residues must agree modulo their greatest common
divisor $2$. The demands $x\equiv1\pmod4$ and $x\equiv2\pmod6$ conflict
in parity and have no solution. The two demands with residue $1$ are
compatible, and their solutions form the class $1$ modulo $12$.

## Try it

Find the representative between $0$ and $14$ with residues $1$ modulo $3$
and $4$ modulo $5$.

**Answer:** $10+4\cdot6=34\equiv4\pmod{15}$. The representative is $4$.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Integer congruence](../GLOSSARY.md#congruence) · [Coprime integers](../GLOSSARY.md#coprime) · [Modular inverse](../GLOSSARY.md#modular-inverse) · [Chinese remainder theorem](../GLOSSARY.md#chinese-remainder) · [Residue class](../GLOSSARY.md#residue-class)

The example is ordinary integer CRT. Paper IX develops arithmetic packets and local deformation beyond this calculation.

### Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation

[Read](../works/paper-ix.md#read) · [Written proofs](../works/paper-ix.md#written-proofs) · [Lean coverage](../works/paper-ix.md#lean) · [Code and setup](../works/paper-ix.md#code) · [Evidence](../works/paper-ix.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: modular_reconstruction()](../../tools/check_hand_examples.py#L237). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Previous: Eliminate a block of unknowns](12_BLOCK_ELIMINATION.md) · [Next: Separate averages and details](14_HAAR_PAIRS.md) · [All examples](../HAND_WORKED_EXAMPLES.md) · [Topic map](../LEARNING_MAP.md#modular)
