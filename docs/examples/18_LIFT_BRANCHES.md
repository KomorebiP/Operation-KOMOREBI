# 18. Follow modular solutions through a lift tree

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: lift branch](../GLOSSARY.md#lift-branch) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Solve $x^2\equiv1\pmod{2^n}$ for four successive positive levels. This is
elementary background for Paper X’s residual and compatibility constructions.
Use the representatives from zero through $2^n-1$.

## List the finite solution sets

| Level | Modulus | Solutions |
|---|---|---|
| 1 | 2 | 1 |
| 2 | 4 | 1, 3 |
| 3 | 8 | 1, 3, 5, 7 |
| 4 | 16 | 1, 7, 9, 15 |

At modulus eight, the odd squares $1,9,25,49$ all have remainder one.
At modulus sixteen, $1^2,7^2,9^2,15^2$ have remainder one, while
$3^2,5^2,11^2,13^2$ have remainder nine. Even squares cannot be odd.

## Check children instead of guessing a branch

A residue $r$ modulo $m$ has exactly two candidate lifts modulo $2m$:
$r$ and $r+m$. Test both against the equation.

| Parent modulo 8 | Candidates modulo 16 | Children that solve the equation |
|---|---|---|
| 1 | 1, 9 | 1, 9 |
| 3 | 3, 11 | None |
| 5 | 5, 13 | None |
| 7 | 7, 15 | 7, 15 |

Thus a solution at one level need not extend to the next. For example,
$3^2-1=8$ is divisible by eight but not sixteen. The other candidate gives
$11^2-1=120$, also not divisible by sixteen.

## Keep reduction compatibility

The sequence $(1,3,7,15)$ at moduli $(2,4,8,16)$ is compatible because
each entry reduces to the preceding one. It is the finite beginning of
$x_n=2^n-1$. This particular formula gives a solution at every level:

```math
(2^n-1)^2-1=2^{2n}-2^{n+1},
```

which is divisible by $2^n$. The constant sequence $x_n=1$ also works at
every level. These explicit formulas supply the all-level argument for
those branches. A finite table does not supply it for an arbitrary branch.

Paper X’s completion statement additionally requires its specified
all-depth inputs and closure conditions. This example makes none of those
arithmetic existence or carrier assumptions for the general paper.

## Try it

Does the solution $9$ modulo sixteen lift to a solution modulo thirty-two?

**Answer:** The candidates are $9$ and $25$. Their squares have remainder
$17$ modulo $32$, so this node has no child. The solutions modulo $32$ are
$1,15,17,31$. The branch reaching $9$ survived to level four but stops at
level five.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Prime power](../GLOSSARY.md#prime-power) · [Modular reduction](../GLOSSARY.md#modular-reduction) · [Lift branch](../GLOSSARY.md#lift-branch) · [Compatible tower](../GLOSSARY.md#compatible-tower) · [p-adic integer](../GLOSSARY.md#padic-integer) · [Survival to a finite level](../GLOSSARY.md#surviving-branch)

Finite lift branches give elementary background for Paper X’s residual constructions. Its completion result requires supplied all-depth data, closure and the other stated inputs.

### Paper X: Universal Residual Seeds and Conditional Occupied-System Completion

[Read](../works/paper-x.md#read) · [Written proofs](../works/paper-x.md#written-proofs) · [Lean coverage](../works/paper-x.md#lean) · [Code and setup](../works/paper-x.md#code) · [Evidence](../works/paper-x.md#evidence)

**Source passages:**

- [Paper X: conditional completion inputs](../../papers/paper-x/current/manuscript/conditional_completion.tex#L8)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#komorebi_mathdeformation). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: lift_branches()](../../tools/check_hand_examples.py#L341). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Calculate quantum measurement and dephasing](17_QUANTUM_MEASUREMENT.md)
- [Next: Compute Frobenius in a quadratic finite field](19_FINITE_FROBENIUS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#lift-branches)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
