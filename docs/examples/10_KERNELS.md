# 10. Find a kernel and describe the lost information

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: kernel](../GLOSSARY.md#kernel) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Consider the real linear map from three coordinates to two given by

```math
T=\begin{pmatrix}1&1&0\\0&1&1\end{pmatrix},\qquad
T(x_1,x_2,x_3)^{\mathsf T}=(x_1+x_2,x_2+x_3)^{\mathsf T}.
```

## Find the erased directions

Set both outputs to zero. The equations are $x_1+x_2=0$ and $x_2+x_3=0$.
Writing $x_2=t$ gives

```math
x=(-t,t,-t)^{\mathsf T}=t(-1,1,-1)^{\mathsf T}.
```

Thus the kernel has basis $(-1,1,-1)^{\mathsf T}$ and dimension one.
The map is not injective.

## Find the image

The first and third columns are $(1,0)^{\mathsf T}$ and $(0,1)^{\mathsf T}$.
They span the entire target, so $T$ is surjective and its rank is two.
The dimensions satisfy

```math
\dim\mathbb R^3=3=2+1=\mathrm{rank}T+\mathrm{nullity}T.
```

## Describe every input with the same output

For output $(5,7)^{\mathsf T}$, choose $x_2=t$. Then

```math
x=(5-t,t,7-t)^{\mathsf T}
=(5,0,7)^{\mathsf T}+t(-1,1,-1)^{\mathsf T}.
```

For instance, $(5,0,7)^{\mathsf T}$ and $(3,2,5)^{\mathsf T}$ give the same
output. The entire fiber is one translate of the kernel. In the quotient
space $\mathbb R^3/\ker T$, these inputs represent the same coset.

This describes precisely what this linear observation loses. An arbitrary
nonlinear observation need not have fibers that are translates of a subspace.

## Try it

Describe all inputs sent to $(1,-1)^{\mathsf T}$.

**Answer:** $(1-t,t,-1-t)^{\mathsf T}$ for arbitrary real $t$. Setting $t=1$
gives $(0,1,-2)^{\mathsf T}$, whose output is $(1,-1)^{\mathsf T}$.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Kernel](../GLOSSARY.md#kernel) · [Image](../GLOSSARY.md#image) · [Rank](../GLOSSARY.md#rank) · [Nullity](../GLOSSARY.md#nullity) · [Rank–nullity identity](../GLOSSARY.md#rank-nullity) · [Injective map](../GLOSSARY.md#injective) · [Surjective map](../GLOSSARY.md#surjective) · [Quotient space](../GLOSSARY.md#quotient-space) · [Subspace](../GLOSSARY.md#subspace)

These finite linear calculations give background for typed realizations and information loss. Read each work for its own claims.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](../works/paper-i.md#read) · [Written proofs](../works/paper-i.md#written-proofs) · [Lean coverage](../works/paper-i.md#lean) · [Code and setup](../works/paper-i.md#code) · [Evidence](../works/paper-i.md#evidence)

### Information Realization

[Read](../works/information-realization.md#read) · [Written proofs](../works/information-realization.md#written-proofs) · [Lean coverage](../works/information-realization.md#lean) · [Code and setup](../works/information-realization.md#code) · [Evidence](../works/information-realization.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: kernels()](../../tools/check_hand_examples.py#L202). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Round a binary number](09_BINARY_ROUNDING.md)
- [Next: Build spectral projectors](11_SPECTRAL_PROJECTORS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#kernels)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
