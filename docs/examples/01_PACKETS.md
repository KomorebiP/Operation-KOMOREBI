# 1. Split and reconstruct a vector

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: projector](../GLOSSARY.md#projector)

We will split a vector into two components and put it back together. Work over
the real numbers and take

```math
x=\begin{pmatrix}2\\3\end{pmatrix},\qquad
P_1=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
P_2=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
```

## Select the components

Multiply each row by the column vector:

```math
P_1x=\begin{pmatrix}1\cdot2+0\cdot3\\0\cdot2+0\cdot3\end{pmatrix}
=\begin{pmatrix}2\\0\end{pmatrix},\qquad
P_2x=\begin{pmatrix}0\\3\end{pmatrix}.
```

The first matrix keeps the first coordinate. The second keeps the second.

## Check the packet identities

Multiplying the matrices gives

```math
P_1^2=P_1,\qquad P_2^2=P_2,\qquad
P_1P_2=P_2P_1=0,\qquad
P_1+P_2=\begin{pmatrix}1&0\\0&1\end{pmatrix}=I_2.
```

Idempotence says selecting a component twice has the same effect as selecting
it once. The zero products say the two selections annihilate each other.
The sum-to-identity equation gives reconstruction:

```math
P_1x+P_2x=\begin{pmatrix}2\\0\end{pmatrix}
+\begin{pmatrix}0\\3\end{pmatrix}
=\begin{pmatrix}2\\3\end{pmatrix}=x.
```

This last identity holds for every vector in this two-dimensional space because
$P_1+P_2=I_2$, not just because it worked for the chosen input.

## An oblique decomposition

A projector need not be orthogonal. Replace the matrices by

```math
Q_1=\begin{pmatrix}1&-1\\0&0\end{pmatrix},\qquad
Q_2=\begin{pmatrix}0&1\\0&1\end{pmatrix}.
```

For example,

```math
Q_1Q_2=\begin{pmatrix}0&1-1\\0&0\end{pmatrix}=0.
```

Likewise $Q_2Q_1=0$, $Q_1^2=Q_1$, $Q_2^2=Q_2$ and $Q_1+Q_2=I_2$.
The components of the same input are now

```math
Q_1x=\begin{pmatrix}-1\\0\end{pmatrix},\qquad
Q_2x=\begin{pmatrix}3\\3\end{pmatrix}.
```

They still add to $x$. Their ordinary dot product is $-3$, so they are not
perpendicular. Algebraic reconstruction and orthogonality are different
requirements.

## Try it

Use $x=(4,-1)^{\mathsf T}$ with both families.

**Answer:** The $P$ components are $(4,0)^{\mathsf T}$ and
$(0,-1)^{\mathsf T}$. The $Q$ components are $(5,0)^{\mathsf T}$ and
$(-1,-1)^{\mathsf T}$. Both pairs sum to $(4,-1)^{\mathsf T}$.

**Continue reading:** [Packet family](../GLOSSARY.md#complete-packet-family),
[orthogonal projector](../GLOSSARY.md#orthogonal-projector), and the
[library's first packet program](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction).

[Next: generate a space from a seed](02_SEEDS.md) · [All examples](../HAND_WORKED_EXAMPLES.md)
