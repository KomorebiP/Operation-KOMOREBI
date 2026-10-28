# 12. Eliminate one block and recover the solution

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: Schur complement](../GLOSSARY.md#schur-complement) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Solve the real system

```math
\begin{pmatrix}2&1\\3&4\end{pmatrix}
\begin{pmatrix}u\\v\end{pmatrix}
=\begin{pmatrix}5\\11\end{pmatrix}.
```

Here each block is a scalar: $A=2$, $B=1$, $C=3$ and $D=4$.

## Eliminate the first unknown

The first equation gives $u=(5-v)/2$. Substitute this into the second:

```math
3(5-v)/2+4v=11,\qquad
(4-3/2)v=11-15/2=7/2.
```

The reduced coefficient is the Schur complement

```math
S=D-CA^{-1}B=4-3\cdot(1/2)\cdot1=5/2.
```

Since $S$ is nonzero, $v=(7/2)/(5/2)=7/5$. Back substitution gives
$u=(5-7/5)/2=9/5$.

## Check both original equations

```math
2(9/5)+7/5=25/5=5,\qquad
3(9/5)+4(7/5)=55/5=11.
```

The matrix factorization displays the same elimination:

```math
\begin{pmatrix}2&1\\3&4\end{pmatrix}
=\begin{pmatrix}1&0\\3/2&1\end{pmatrix}
\begin{pmatrix}2&1\\0&5/2\end{pmatrix}.
```

Its determinant is $2\cdot4-1\cdot3=5$, also the product $2(5/2)$.

## Keep the invertibility assumptions

For compatible square diagonal blocks, the same substitution gives

```math
Sv=g-CA^{-1}f,\qquad u=A^{-1}(f-Bv).
```

This form requires invertible $A$. A unique solution for every right-hand
side additionally requires invertible $S$. If $S$ is singular, a particular
right-hand side can give no solution or multiple solutions.

For example, replace $D=4$ by $D=3/2$. The reduced coefficient becomes zero.
With $f=5$, consistency requires $g=15/2$. If $A$ itself is singular, this
elimination route is unavailable, although a different pivot may work.

## Try it

Keep the original matrix and use the right-hand side $(3,5)^{\mathsf T}$.

**Answer:** $(5/2)v=5-9/2=1/2$, so $v=1/5$ and $u=7/5$.
Substitution gives $2(7/5)+1/5=3$ and $3(7/5)+4/5=5$.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Block matrix](../GLOSSARY.md#block-matrix) · [Schur complement](../GLOSSARY.md#schur-complement) · [Elimination](../GLOSSARY.md#elimination) · [Determinant](../GLOSSARY.md#determinant) · [Inverse](../GLOSSARY.md#inverse)

Paper VI gives elimination background. The collected Gaussian elimination guide retains its pending source qualification and unassessed confidence.

### Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations

[Read](../works/paper-vi.md#read) · [Written proofs](../works/paper-vi.md#written-proofs) · [Lean coverage](../works/paper-vi.md#lean) · [Code and setup](../works/paper-vi.md#code) · [Evidence](../works/paper-vi.md#evidence)

### Gaussian Elimination: collected guide

[Read](../works/gaussian-elimination-guide.md#read) · [Written proofs](../works/gaussian-elimination-guide.md#written-proofs) · [Lean coverage](../works/gaussian-elimination-guide.md#lean) · [Code and setup](../works/gaussian-elimination-guide.md#code) · [Evidence](../works/gaussian-elimination-guide.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: block_elimination()](../../tools/check_hand_examples.py#L225). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Build spectral projectors](11_SPECTRAL_PROJECTORS.md)
- [Next: Reconstruct from residues](13_MODULAR_RECONSTRUCTION.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#elimination)
