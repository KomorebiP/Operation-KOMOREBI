# 2. Generate a space from one seed

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: seed](../GLOSSARY.md#seed)

The same vector space can require different generating data under different
allowed operations. Here the allowed operations are real linear combinations
of powers of one matrix, including the identity.

## Choose the action and a seed

On $\mathbb R^2$, let

```math
N=\begin{pmatrix}0&1\\0&0\end{pmatrix},\qquad
v=\begin{pmatrix}0\\1\end{pmatrix}.
```

Apply the operator repeatedly:

```math
N^0v=v=\begin{pmatrix}0\\1\end{pmatrix},\qquad
Nv=\begin{pmatrix}1\\0\end{pmatrix},\qquad
N^2v=\begin{pmatrix}0\\0\end{pmatrix}.
```

In fact $N^2=0$, so further applications give zero too.

## Recover every vector

For any real numbers $a,b$,

```math
\begin{pmatrix}a\\b\end{pmatrix}
=b\,v+a\,Nv=(bI_2+aN)v.
```

Thus one seed generates the whole space under this action. For the input
$(2,3)^{\mathsf T}$, the coefficients are $b=3$ and $a=2$.

An empty seed set spans only the zero vector. Our space is nonzero, so one is
also the minimum number of seeds for this particular action.

## A poor seed and a different action

If we choose $w=(1,0)^{\mathsf T}$ instead, then $Nw=0$. Its generated space
contains only multiples of $w$, so it misses $(0,1)^{\mathsf T}$.

Now change the allowed operator to the zero matrix. Every positive power of
that operator kills every vector. The identity still preserves the supplied
seeds, but no new directions appear. One seed spans at most a line, while
the two standard basis vectors span $\mathbb R^2$. The minimum is now two.

The seed count therefore belongs to the space **and its declared action**.
It is not automatically the dimension of the vector space.

## Try it

Which single seeds $v=(a,b)^{\mathsf T}$ generate $\mathbb R^2$ under $N$?

**Answer:** Exactly those with $b\ne0$. Here $Nv=(b,0)^{\mathsf T}$, and the
matrix with columns $v,Nv$ has determinant $-b^2$. It is invertible precisely
when $b\ne0$. If $b=0$, both vectors lie on the first coordinate axis.

**Continue reading:** [Span](../GLOSSARY.md#span),
[seed rank](../GLOSSARY.md#seed-rank), and the
[seed operations guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed).
Paper I's broader definitions may use modules, topology and cardinalities.

[Previous: packets](01_PACKETS.md) · [Next: coordinates](03_COORDINATES.md) · [All examples](../HAND_WORKED_EXAMPLES.md)
