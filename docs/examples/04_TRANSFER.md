# 4. Assemble an operator from transfer blocks

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: transfer block](../GLOSSARY.md#transfer-block) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Use the coordinate projectors $P_1,P_2$ from
[Example 1](01_PACKETS.md), and let

```math
T=\begin{pmatrix}1&2\\3&4\end{pmatrix},\qquad
x=\begin{pmatrix}2\\3\end{pmatrix}.
```

The block $T_{ji}=P_jTP_i$ selects source component $i$, applies $T$ and
selects target component $j$. The source selection acts first.

## Calculate the four blocks

Right multiplication keeps one column. Left multiplication keeps one row:

```math
T_{11}=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad
T_{12}=\begin{pmatrix}0&2\\0&0\end{pmatrix},\quad
T_{21}=\begin{pmatrix}0&0\\3&0\end{pmatrix},\quad
T_{22}=\begin{pmatrix}0&0\\0&4\end{pmatrix}.
```

Adding these four matrices gives $T$.

## Track the contribution of each block

| Route | Contribution to the output |
|---|---|
| Source 1 to target 1 | $T_{11}x=(2,0)^{\mathsf T}$ |
| Source 2 to target 1 | $T_{12}x=(6,0)^{\mathsf T}$ |
| Source 1 to target 2 | $T_{21}x=(0,6)^{\mathsf T}$ |
| Source 2 to target 2 | $T_{22}x=(0,12)^{\mathsf T}$ |

The sum is $(8,18)^{\mathsf T}$. Direct multiplication gives the same answer:

```math
Tx=\begin{pmatrix}1\cdot2+2\cdot3\\3\cdot2+4\cdot3\end{pmatrix}
=\begin{pmatrix}8\\18\end{pmatrix}.
```

The reconstruction law comes from inserting the complete family on both sides:

```math
T=(P_1+P_2)T(P_1+P_2)=\sum_{j=1}^{2}\sum_{i=1}^{2}P_jTP_i.
```

## Compose another operation

Let $U$ exchange the two coordinates:

```math
U=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
UT=\begin{pmatrix}3&4\\1&2\end{pmatrix}.
```

The two-step output is $U(Tx)=(18,8)^{\mathsf T}$, which also equals
$(UT)x$. More generally, inserting the identity between the operations gives

```math
P_kUTP_i=\sum_{j=1}^{2}(P_kUP_j)(P_jTP_i).
```

Here $P_j^2=P_j$ makes the repeated middle selection harmless. The sum runs
over the intermediate packets.

## Try it

Compute the four contributions for $x=(1,-1)^{\mathsf T}$.

**Answer:** They are $(1,0)^{\mathsf T}$, $(-2,0)^{\mathsf T}$,
$(0,3)^{\mathsf T}$ and $(0,-4)^{\mathsf T}$. The output is
$(-1,-1)^{\mathsf T}$.

**Continue reading:** [Composition](../GLOSSARY.md#composition) and the
[transfer operations guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#5-transfer).
The example checks finite matrix identities. It makes no claim about the cost
of a particular hardware implementation.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Transfer block](../GLOSSARY.md#transfer-block) · [Composition](../GLOSSARY.md#composition) · [Block matrix](../GLOSSARY.md#block-matrix)

Paper II supplies transfer background. Paper VIII develops operator algorithms and compilation.

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](../works/paper-ii.md#read) · [Written proofs](../works/paper-ii.md#written-proofs) · [Lean coverage](../works/paper-ii.md#lean) · [Code and setup](../works/paper-ii.md#code) · [Evidence](../works/paper-ii.md#evidence)

### Paper VIII: Packet Operator Algorithms, Exact Compilation, and GPU Realization

[Read](../works/paper-viii.md#read) · [Written proofs](../works/paper-viii.md#written-proofs) · [Lean coverage](../works/paper-viii.md#lean) · [Code and setup](../works/paper-viii.md#code) · [Evidence](../works/paper-viii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#transfer-blocks). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: transfer()](../../tools/check_hand_examples.py#L99). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Change coordinates](03_COORDINATES.md)
- [Next: Refine a signal](05_REFINEMENT.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#transfer)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
