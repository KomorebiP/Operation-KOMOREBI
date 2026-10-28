# 11. Build projectors from an operator

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: spectral projector](../GLOSSARY.md#spectral-projector) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Work over the real numbers with

```math
T=\begin{pmatrix}2&1\\0&3\end{pmatrix}.
```

## Find two invariant directions

For eigenvalue $2$, solving $(T-2I)v=0$ forces the second coordinate to zero.
Choose $v_2=(1,0)^{\mathsf T}$. For eigenvalue $3$, solving $(T-3I)v=0$
gives equal coordinates. Choose $v_3=(1,1)^{\mathsf T}$.

These vectors form a basis, and direct multiplication gives $Tv_2=2v_2$
and $Tv_3=3v_3$. The operator is diagonalizable.

## Interpolate the selectors

The polynomial $3-t$ equals one at $2$ and zero at $3$. The polynomial
$t-2$ does the opposite. Substitute the matrix into these polynomials:

```math
P_2=3I-T=\begin{pmatrix}1&-1\\0&0\end{pmatrix},\qquad
P_3=T-2I=\begin{pmatrix}0&1\\0&1\end{pmatrix}.
```

The identity

```math
(T-2I)(T-3I)=
\begin{pmatrix}0&1\\0&1\end{pmatrix}
\begin{pmatrix}-1&1\\0&0\end{pmatrix}=0
```

implies $T^2-5T+6I=0$. An annihilating polynomial must vanish at both
eigenvalues, so no degree-one polynomial suffices. Thus $(t-2)(t-3)$ is
the minimal polynomial. Using the displayed identity,

```math
P_2^2=9I-6T+T^2=3I-T=P_2,\qquad
P_3^2=T^2-4T+4I=T-2I=P_3.
```

Also $P_2P_3=P_3P_2=0$, $P_2+P_3=I$ and $T=2P_2+3P_3$.

## Compute through the packets

For $x=(2,3)^{\mathsf T}$, the components are
$P_2x=(-1,0)^{\mathsf T}$ and $P_3x=(3,3)^{\mathsf T}$. Therefore

```math
Tx=2(-1,0)^{\mathsf T}+3(3,3)^{\mathsf T}=(7,9)^{\mathsf T}.
```

These are the oblique projectors from Example 1. Their eigenspaces are not
perpendicular in the ordinary inner product. Diagonalizability alone does
not imply orthogonal spectral projectors.

## Try it

Use the decomposition to calculate $T^2x$.

**Answer:** $T^2=4P_2+9P_3$, so $T^2x=(23,27)^{\mathsf T}$.
Direct multiplication gives

```math
T^2=\begin{pmatrix}4&5\\0&9\end{pmatrix}.
```

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Eigenvector](../GLOSSARY.md#eigenvector) · [Eigenvalue](../GLOSSARY.md#eigenvalue) · [Eigenspace](../GLOSSARY.md#eigenspace) · [Diagonalizable operator](../GLOSSARY.md#diagonalizable) · [Polynomial in an operator](../GLOSSARY.md#polynomial-in-operator) · [Minimal polynomial](../GLOSSARY.md#minimal-polynomial) · [Spectral projector](../GLOSSARY.md#spectral-projector)

The example uses a diagonalizable two-dimensional matrix. The works develop wider packet and spectral constructions with additional hypotheses.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](../works/paper-i.md#read) · [Written proofs](../works/paper-i.md#written-proofs) · [Lean coverage](../works/paper-i.md#lean) · [Code and setup](../works/paper-i.md#code) · [Evidence](../works/paper-i.md#evidence)

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](../works/paper-ii.md#read) · [Written proofs](../works/paper-ii.md#written-proofs) · [Lean coverage](../works/paper-ii.md#lean) · [Code and setup](../works/paper-ii.md#code) · [Evidence](../works/paper-ii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: spectral_projectors()](../../tools/check_hand_examples.py#L212). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Find a kernel and its fibers](10_KERNELS.md)
- [Next: Eliminate a block of unknowns](12_BLOCK_ELIMINATION.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#spectral)
