# 3. Change coordinates and transport an operator

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: coordinate change](../GLOSSARY.md#coordinate-change) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Let $x$ and $y$ be two coordinate descriptions of the same object, related by
$y=Cx$. This convention fixes the direction of the change.

## Change the coordinates

Take

```math
C=\begin{pmatrix}1&1/2\\0&1\end{pmatrix},\qquad
x=\begin{pmatrix}2\\3\end{pmatrix}.
```

Then

```math
y=Cx=\begin{pmatrix}2+(1/2)3\\3\end{pmatrix}
=\begin{pmatrix}7/2\\3\end{pmatrix}.
```

Undo the added half of the second coordinate with

```math
C^{-1}=\begin{pmatrix}1&-1/2\\0&1\end{pmatrix}.
```

The off-diagonal entry in $C^{-1}C$ is $1/2-1/2=0$, and its diagonal
entries are both one. Applying the inverse to $y$ gives

```math
C^{-1}y=\begin{pmatrix}7/2-3/2\\3\end{pmatrix}
=\begin{pmatrix}2\\3\end{pmatrix}.
```

## Describe the same operation in the new coordinates

In the $x$ coordinates, let the operation double the first coordinate:

```math
D=\begin{pmatrix}2&0\\0&1\end{pmatrix}.
```

Starting from $y$, first recover $x$, then apply $D$, then return to $y$
coordinates. The matrix is therefore $D_y=CDC^{-1}$:

```math
CD=\begin{pmatrix}2&1/2\\0&1\end{pmatrix},\qquad
D_y=\begin{pmatrix}2&1/2\\0&1\end{pmatrix}
\begin{pmatrix}1&-1/2\\0&1\end{pmatrix}
=\begin{pmatrix}2&-1/2\\0&1\end{pmatrix}.
```

## Compare the two routes

Operate first, then change coordinates:

```math
Dx=\begin{pmatrix}4\\3\end{pmatrix},\qquad
CDx=\begin{pmatrix}4+3/2\\3\end{pmatrix}
=\begin{pmatrix}11/2\\3\end{pmatrix}.
```

Change coordinates first, then use the transported operator:

```math
D_yy=\begin{pmatrix}2(7/2)-(1/2)3\\3\end{pmatrix}
=\begin{pmatrix}11/2\\3\end{pmatrix}.
```

Both routes agree. The matrix identity is $D_yC=CD$. Changing coordinates
without changing the operator matrix would generally describe a different
operation.

## Try it

Repeat the two routes for $x=(1,2)^{\mathsf T}$.

**Answer:** $y=(2,2)^{\mathsf T}$ and both routes produce
$(3,2)^{\mathsf T}$ in the new coordinates.

**Continue reading:** [Conjugation](../GLOSSARY.md#conjugation),
[commuting diagram](../GLOSSARY.md#commuting-diagram), and
[operator transport](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport).

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Coordinates](../GLOSSARY.md#coordinates) · [Coordinate change](../GLOSSARY.md#coordinate-change) · [Inverse](../GLOSSARY.md#inverse) · [Operator conjugation](../GLOSSARY.md#conjugation) · [Linear isomorphism](../GLOSSARY.md#isomorphism)

Use Paper I for exact packet coordinates and the library atlas for general coordinate changes.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](../works/paper-i.md#read) · [Written proofs](../works/paper-i.md#written-proofs) · [Lean coverage](../works/paper-i.md#lean) · [Code and setup](../works/paper-i.md#code) · [Evidence](../works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: coordinates()](../../tools/check_hand_examples.py#L84). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Generate a space from one seed](02_SEEDS.md)
- [Next: Assemble transfer blocks](04_TRANSFER.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#coordinates)
