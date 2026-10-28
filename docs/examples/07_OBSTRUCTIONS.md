# 7. Find an obstruction to recovering information

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: obstruction](../GLOSSARY.md#obstruction)

Suppose a coarse description keeps only the sum of two real coordinates:

```math
R(x_1,x_2)=x_1+x_2.
```

We want to recover the first coordinate, $F(x_1,x_2)=x_1$, using only that
sum. A successful recovery rule would be a function $G:\mathbb R\to\mathbb R$
satisfying $F=G\circ R$ for every input.

## Find a collision

Take

```math
u=(1,0),\qquad v=(0,1).
```

Both coarse values are one:

```math
R(u)=1=R(v).
```

But the requested answers differ:

```math
F(u)=1,\qquad F(v)=0.
```

The rule would have to satisfy both $G(1)=1$ and $G(1)=0$. That is impossible.
This pair is a concrete obstruction. It rules out every recovery function
from the sum alone, including nonlinear ones.

## The same issue in kernel notation

The difference $w=u-v=(1,-1)$ satisfies

```math
Rw=0,\qquad Fw=1.
```

Thus $w$ lies in $\ker R$ but not in $\ker F$. For these linear maps,
recovering $F$ through $R$ would require
$\ker R\subseteq\ker F$.

In ordinary language, the coarse description must not identify two inputs
that the requested observation needs to distinguish.

## A compatible question

Instead ask for $H(x_1,x_2)=2x_1+2x_2$. This does factor through the sum:

```math
G_H(s)=2s,\qquad G_H(R(x_1,x_2))=2(x_1+x_2)=H(x_1,x_2).
```

Whether information has been lost depends on the question we want to answer.
The sum suffices for $H$ and fails for $F$.

## Try it

Could the product $K(x_1,x_2)=x_1x_2$ be recovered from the sum alone?

**Answer:** No. The inputs $(1,1)$ and $(2,0)$ both sum to two, but their
products are one and zero.

**Continue reading:** [Fiber](../GLOSSARY.md#fiber),
[factorization](../GLOSSARY.md#factorization), and the
[carrier-change criterion](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion).

[Previous: redundant coordinates](06_REDUNDANT_COORDINATES.md) · [Next: weighted averages](08_WEIGHTED_AVERAGES.md) · [All examples](../HAND_WORKED_EXAMPLES.md)
