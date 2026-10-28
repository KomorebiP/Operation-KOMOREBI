# 8. Average with unequal weights

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: conditional expectation](../GLOSSARY.md#conditional-expectation) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Take three real values $x=(2,6,9)^{\mathsf T}$, with positive weights
$w=(1,3,2)$. Group the first two positions together and leave the third alone.
We want a value that is constant within each group.

## Compute each group's mean

The first group's weighted mean is

```math
\frac{1\cdot2+3\cdot6}{1+3}=\frac{20}{4}=5.
```

The second group has only the value 9. The averaged vector is therefore

```math
Ex=\begin{pmatrix}5\\5\\9\end{pmatrix},\qquad
E=\begin{pmatrix}1/4&3/4&0\\1/4&3/4&0\\0&0&1\end{pmatrix}.
```

Normalizing all weights by their total, six, would give the same group means.
This is finite conditional expectation with respect to the chosen partition.

## Average again

The first group now contains two copies of five. Its mean remains
$(1\cdot5+3\cdot5)/4=5$. The third coordinate also stays fixed.

More generally, $E$ fixes every vector of the form $(a,a,b)^{\mathsf T}$,
and every output of $E$ has that form. Hence $E^2=E$.

## Measure the residual using the stated weights

The residual is

```math
r=x-Ex=\begin{pmatrix}-3\\1\\0\end{pmatrix}.
```

Use the weighted inner product

```math
\langle u,v\rangle_w=u_1v_1+3u_2v_2+2u_3v_3.
```

For every group-constant vector $y=(a,a,b)^{\mathsf T}$,

```math
\langle r,y\rangle_w=(-3)a+3(1)a+2(0)b=0.
```

The residual is orthogonal to the retained subspace in this inner product.
The matrix $E$ is not symmetric in ordinary coordinates, so the choice of
inner product matters.

## Check the squared lengths

```math
\|x\|_w^2=2^2+3\cdot6^2+2\cdot9^2=274,
```

```math
\|Ex\|_w^2=5^2+3\cdot5^2+2\cdot9^2=262,\qquad
\|r\|_w^2=(-3)^2+3\cdot1^2=12.
```

As expected from orthogonality, $274=262+12$.

## Try it

Use equal weights $(1,1,1)$ with the same input and partition.

**Answer:** The averaged vector is $(4,4,9)^{\mathsf T}$ and the residual
is $(-2,2,0)^{\mathsf T}$. The ordinary squared lengths satisfy
$121=113+8$.

**Continue reading:** [Inner product](../GLOSSARY.md#inner-product),
[norm](../GLOSSARY.md#norm), and
[finite projection operations](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project).
This calculation assumes known positive weights and a fixed finite partition.
It does not estimate either from data.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Finite conditional expectation](../GLOSSARY.md#conditional-expectation) · [Inner product](../GLOSSARY.md#inner-product) · [Orthogonal projector](../GLOSSARY.md#orthogonal-projector) · [Residual](../GLOSSARY.md#residual)

Paper VI includes stochastic and Bayesian realizations. Its assumptions extend beyond this finite partition.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations | [Read](../works/paper-vi.md#read) | [Proofs](../works/paper-vi.md#written-proofs) | [Coverage and sources](../works/paper-vi.md#lean) | [Code and setup](../works/paper-vi.md#code) | [Status](../works/paper-vi.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: weighted_averages()](../../tools/check_hand_examples.py#L165). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Previous: Detect lost information](07_OBSTRUCTIONS.md) · [Next: Round a binary number](09_BINARY_ROUNDING.md) · [All examples](../HAND_WORKED_EXAMPLES.md) · [Topic map](../LEARNING_MAP.md#averages)
