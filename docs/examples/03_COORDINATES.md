# 3. Change coordinates and transport an operator

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: coordinate change](../GLOSSARY.md#coordinate-change)

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

[Previous: seeds](02_SEEDS.md) · [Next: transfer blocks](04_TRANSFER.md) · [All examples](../HAND_WORKED_EXAMPLES.md)
