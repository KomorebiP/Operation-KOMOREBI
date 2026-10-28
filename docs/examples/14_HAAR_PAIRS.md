# 14. Separate averages and differences

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: Haar pair](../GLOSSARY.md#haar-pair) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Take the real signal $(2,6,10,14)$. For each neighboring pair $(u,v)$, define

```math
a=(u+v)/2,\qquad d=(u-v)/2.
```

We use the averaging normalization throughout this example.

## Analyze the first level

For $(2,6)$, the average is $4$ and the detail is $-2$. For $(10,14)$,
they are $12$ and $-2$. The averaging transform and its inverse are

```math
H=\frac12\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad
H^{-1}=\begin{pmatrix}1&1\\1&-1\end{pmatrix}.
```

Multiplying gives $H^{-1}H=HH^{-1}=I$. The inverse rule is $u=a+d$ and
$v=a-d$. It recovers $(4-2,4+2)=(2,6)$ and $(12-2,12+2)=(10,14)$.

## Analyze the averages once more

The pair $(4,12)$ has average $8$ and detail $-4$. Store coefficients in
the declared order

```math
(a_{\mathrm{top}},d_{\mathrm{top}},d_{\mathrm{left}},d_{\mathrm{right}})
=(8,-4,-2,-2).
```

To invert, first reconstruct $(8-4,8+4)=(4,12)$. Then combine each of these
averages with its saved detail. The result is the original four samples.

## Track the effect of the normalization

For one pair, $u^2+v^2=2(a^2+d^2)$. Applying this at both levels gives

```math
2^2+6^2+10^2+14^2=336
=4(8^2+(-4)^2)+2((-2)^2+(-2)^2).
```

The unweighted sum of the four stored coefficient squares is only $88$.
This $H$ is not an orthogonal matrix: $H^{\mathsf T}H=I/2$.
Using $\sqrt2H$ for a single pair gives an orthogonal matrix instead.
Do not mix the two normalization conventions in reconstruction or energy checks.

## Drop fine details and measure the loss

Set the two first-level details to zero, while keeping $8$ and $-4$.
Reconstruction gives $(4,4,12,12)$. The residual is $(-2,2,-2,2)$ and its
squared Euclidean norm is $16$. The reconstructed squared norm is $320$,
so $336=320+16$.

## Try it

Transform $(1,3,5,7)$ in the same coefficient order.

**Answer:** The first averages are $(2,6)$ and the details are $(-1,-1)$.
The stored coefficients are $(4,-2,-1,-1)$. Their weighted energy is
$4(16+4)+2(1+1)=84$, the original squared norm.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Haar pair](../GLOSSARY.md#haar-pair) · [Detail coefficient](../GLOSSARY.md#detail-coefficient) · [Normalization](../GLOSSARY.md#normalization) · [Orthogonal matrix](../GLOSSARY.md#orthogonal-matrix) · [Refinement](../GLOSSARY.md#refinement)

Paper V supplies signal background. Information Realization includes a finite Haar contract within its recorded formal core.

### Paper V: Polyphase Signal Calculus

[Read](../works/paper-v.md#read) · [Written proofs](../works/paper-v.md#written-proofs) · [Lean coverage](../works/paper-v.md#lean) · [Code and setup](../works/paper-v.md#code) · [Evidence](../works/paper-v.md#evidence)

### Information Realization

[Read](../works/information-realization.md#read) · [Written proofs](../works/information-realization.md#written-proofs) · [Lean coverage](../works/information-realization.md#lean) · [Code and setup](../works/information-realization.md#code) · [Evidence](../works/information-realization.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: haar_pairs()](../../tools/check_hand_examples.py#L248). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Reconstruct from residues](13_MODULAR_RECONSTRUCTION.md)
- [Next: Compose typed operations](15_TYPED_PATHS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#haar)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
