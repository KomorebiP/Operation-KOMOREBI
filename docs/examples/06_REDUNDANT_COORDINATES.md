# 6. Reconstruct from redundant coordinates

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: analysis and synthesis](../GLOSSARY.md#analysis-synthesis) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Three measurements can describe a two-dimensional vector. They may reconstruct
it exactly even though their individual reconstruction components are not
projectors.

## Analyze and synthesize

Work over the real numbers and set

```math
A=\begin{pmatrix}1&0\\0&1\\1&1\end{pmatrix},\qquad
S=\frac13\begin{pmatrix}2&-1&1\\-1&2&1\end{pmatrix}.
```

$A$ is $3$ by $2$ and sends a vector to three coordinates. $S$ is $2$ by
$3$ and sends those coordinates back. Multiplication gives

```math
SA=\frac13\begin{pmatrix}2+1&-1+1\\-1+1&2+1\end{pmatrix}
=I_2.
```

For $x=(2,3)^{\mathsf T}$,

```math
Ax=\begin{pmatrix}2\\3\\5\end{pmatrix},\qquad
S(Ax)=\frac13\begin{pmatrix}4-3+5\\-2+6+5\end{pmatrix}
=\begin{pmatrix}2\\3\end{pmatrix}.
```

The third coordinate is redundant because it is the sum of the first two.

## Reconstruct one coordinate at a time

Let $E_i$ keep only coordinate $i$ in the three-dimensional coordinate space.
Define $C_i=SE_iA$. Their contributions to $x$ are

```math
C_1x=\begin{pmatrix}4/3\\-2/3\end{pmatrix},\qquad
C_2x=\begin{pmatrix}-1\\2\end{pmatrix},\qquad
C_3x=\begin{pmatrix}5/3\\5/3\end{pmatrix}.
```

Adding gives

```math
\begin{pmatrix}4/3-1+5/3\\-2/3+2+5/3\end{pmatrix}
=\begin{pmatrix}2\\3\end{pmatrix}.
```

The matrices are

```math
C_1=\frac13\begin{pmatrix}2&0\\-1&0\end{pmatrix},\quad
C_2=\frac13\begin{pmatrix}0&-1\\0&2\end{pmatrix},\quad
C_3=\frac13\begin{pmatrix}1&1\\1&1\end{pmatrix}.
```

They sum to $I_2$. However,

```math
C_1^2=\frac19\begin{pmatrix}4&0\\-2&0\end{pmatrix}
=\frac23C_1\ne C_1.
```

So $C_1$ is not a projector. Exact additive reconstruction alone does not
establish idempotence.

## A left inverse is not a two-sided inverse

In the other order,

```math
AS=\frac13\begin{pmatrix}2&-1&1\\-1&2&1\\1&1&2\end{pmatrix}\ne I_3.
```

For $z=(0,0,1)^{\mathsf T}$, we get
$ASz=(1/3,1/3,2/3)^{\mathsf T}$, not $z$. The original $z$ cannot equal
$Ax$ for any $x$, since valid analyzed coordinates satisfy $z_3=z_1+z_2$.

## Try it

Calculate the three contributions for $x=(1,-1)^{\mathsf T}$.

**Answer:** $Ax=(1,-1,0)^{\mathsf T}$. The contributions are
$(2/3,-1/3)^{\mathsf T}$, $(1/3,-2/3)^{\mathsf T}$ and zero.
They sum to the original vector.

**Continue reading:** [Left inverse](../GLOSSARY.md#left-inverse),
[redundant coordinates](../GLOSSARY.md#redundancy), and
[components versus projectors](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors).

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Analysis and synthesis](../GLOSSARY.md#analysis-synthesis) · [Left inverse](../GLOSSARY.md#left-inverse) · [Redundant coordinates](../GLOSSARY.md#redundancy) · [Reconstruction](../GLOSSARY.md#reconstruction)

Compare the exact packet setting of Paper I with the broader analysis and synthesis construction in the library guide.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](../works/paper-i.md#read) · [Written proofs](../works/paper-i.md#written-proofs) · [Lean coverage](../works/paper-i.md#lean) · [Code and setup](../works/paper-i.md#code) · [Evidence](../works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: redundant_coordinates()](../../tools/check_hand_examples.py#L135). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Refine a signal](05_REFINEMENT.md)
- [Next: Detect lost information](07_OBSTRUCTIONS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#redundancy)
