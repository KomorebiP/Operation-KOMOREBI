# 15. Compose operations with matching types

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: typed path](../GLOSSARY.md#typed-path) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Let $V=\mathbb R^2$ and $W=\mathbb R$. Define an observation $A:V\to W$
and an insertion $B:W\to V$ by

```math
A=\begin{pmatrix}1&1\end{pmatrix},\qquad
B=\begin{pmatrix}1\\0\end{pmatrix}.
```

## Follow each legal path

The path $V\xrightarrow A W\xrightarrow B V$ has matrix

```math
BA=\begin{pmatrix}1&1\\0&0\end{pmatrix}=P.
```

The other path $W\xrightarrow B V\xrightarrow A W$ has matrix $AB=(1)=I_W$.
These products act on different spaces. It would be a type error to subtract
them as though they were square matrices of the same size.

For $x=(2,3)^{\mathsf T}$, $Ax=5$ and $B(Ax)=(5,0)^{\mathsf T}$.
For a scalar $s$, $A(Bs)=s$. Thus $B$ is a right inverse of $A$, while $A$
is a left inverse of $B$.

## Use a relation to simplify a path

Since $AB=I_W$, associativity gives

```math
P^2=BABA=B(AB)A=BI_WA=BA=P.
```

So the round trip on $V$ is a projector. It is not the identity, since
it sends $(0,1)^{\mathsf T}$ to $(1,0)^{\mathsf T}$. Exact return on $W$
does not imply exact return on $V$.

The relation $AP=A$ says $A$ intertwines $P$ on $V$ with $I_W$ on $W$.
It is a well-typed equality of maps $V\to W$.

## Compare orders only on one space

On $V$, take $D=\operatorname{diag}(2,3)$. Both $DP$ and $PD$ are defined:

```math
DP=\begin{pmatrix}2&2\\0&0\end{pmatrix},\qquad
PD=\begin{pmatrix}2&3\\0&0\end{pmatrix},\qquad
[D,P]=DP-PD=\begin{pmatrix}0&-1\\0&0\end{pmatrix}.
```

The nonzero commutator records that these two operations do not commute.
Unlike $AB$ and $BA$, the two terms of this subtraction have the same type.

## Try it

Replace $B$ by $B'=(0,1)^{\mathsf T}$. Calculate $AB'$ and $B'A$.

**Answer:** $AB'=1$ and

```math
B'A=\begin{pmatrix}0&0\\1&1\end{pmatrix}.
```
The new round trip sends $(2,3)^{\mathsf T}$ to $(0,5)^{\mathsf T}$.
It is another projector, with a different selected range.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Typed system](../GLOSSARY.md#typed-system) · [Typed path](../GLOSSARY.md#typed-path) · [Operator relation](../GLOSSARY.md#relation) · [Domain and codomain](../GLOSSARY.md#domain-codomain) · [Intertwiner](../GLOSSARY.md#intertwiner) · [Commutator](../GLOSSARY.md#commutator)

Paper I develops typed systems and their realizations. Paper III continues with typed transfer and obstructions.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](../works/paper-i.md#read) · [Written proofs](../works/paper-i.md#written-proofs) · [Lean coverage](../works/paper-i.md#lean) · [Code and setup](../works/paper-i.md#code) · [Evidence](../works/paper-i.md#evidence)

### Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory

[Read](../works/paper-iii.md#read) · [Written proofs](../works/paper-iii.md#written-proofs) · [Lean coverage](../works/paper-iii.md#lean) · [Code and setup](../works/paper-iii.md#code) · [Evidence](../works/paper-iii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: typed_paths()](../../tools/check_hand_examples.py#L263). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Separate averages and details](14_HAAR_PAIRS.md)
- [Next: Split reciprocal coefficients into cyclic packets](16_CYCLIC_RECIPROCALS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#typed-paths)
