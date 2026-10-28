# 19. Compute Frobenius in a quadratic finite field

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: finite-field Frobenius](../GLOSSARY.md#frobenius) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

The square residues modulo five are $0,1,4$. Since $3$ is absent,
$t^2-3$ is irreducible over $\mathbb F_5$. We can form the field

```math
\mathbb F_{25}=\mathbb F_5[\alpha],\qquad \alpha^2=3.
```

Every element has a unique form $a+b\alpha$ with $a,b$ modulo five. This
provides finite-field background for Paper XI’s finite packet theory.

## Multiply in the declared basis

Use the basis $(1,\alpha)$. The rule is

```math
(a+b\alpha)(c+d\alpha)=(ac+3bd)+(ad+bc)\alpha,
```

with both coefficients reduced modulo five. For $\beta=1+\alpha$,
$\beta^2=4+2\alpha$.

## Calculate Frobenius and its orbit

The characteristic-five binomial identity gives
$(a+b\alpha)^5=a^5+b^5\alpha^5$. In the base field $a^5=a$, and

```math
\alpha^5=\alpha(\alpha^2)^2=9\alpha=4\alpha=-\alpha.
```

Consequently $F(a+b\alpha)=a-b\alpha$. Applying $F$ twice is the identity.
The element $\beta$ has the two-element orbit $1+\alpha,1-\alpha$.

## Compute trace, norm and inverse

```math
\mathrm{Tr}(\beta)=\beta+\beta^5=2,\qquad
\mathrm{N}(\beta)=\beta\beta^5=1-3=3\quad\text{in }\mathbb F_5.
```

Since the inverse of $3$ modulo five is $2$,

```math
\beta^{-1}=2(1-\alpha)=2+3\alpha.
```

Indeed, $(1+\alpha)(2+3\alpha)=11+5\alpha=1$ in this field.

## Verify the operator comparison

Multiplication by $\beta$ and Frobenius have matrices

```math
M_\beta=\begin{pmatrix}1&3\\1&1\end{pmatrix},\qquad
C=\begin{pmatrix}1&0\\0&4\end{pmatrix},\qquad C^{-1}=C.
```

Direct multiplication modulo five gives

```math
CM_\beta C^{-1}=\begin{pmatrix}1&2\\4&1\end{pmatrix}=M_{\beta^5}.
```

The matrix trace is $2$ and its determinant is $1-3=3$, agreeing with
the field trace and norm. This constructs and checks a particular finite
comparison map. Paper XI’s arithmetic realization and comparison obligations
require their own supplied objects and hypotheses.

## Try it

For $\gamma=2+\alpha$, find its Frobenius conjugate, trace, norm and inverse.

**Answer:** $\gamma^5=2-\alpha$, trace $4$, norm $4-3=1$, and
$\gamma^{-1}=2-\alpha$. All scalars in this answer are read modulo five.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Prime field](../GLOSSARY.md#prime-field) · [Extension field](../GLOSSARY.md#extension-field) · [Finite-field Frobenius](../GLOSSARY.md#frobenius) · [Field trace](../GLOSSARY.md#field-trace) · [Field norm](../GLOSSARY.md#field-norm) · [Irreducible polynomial](../GLOSSARY.md#irreducible-polynomial)

This is finite-field background for Paper XI’s finite packet theory. Conjecture 66 separately asks for an actual arithmetic realizer with its declared comparison data.

### Paper XI: Packets, Arithmetic Realization, and Conditional Comparison

[Read](../works/paper-xi.md#read) · [Written proofs](../works/paper-xi.md#written-proofs) · [Lean coverage](../works/paper-xi.md#lean) · [Code and setup](../works/paper-xi.md#code) · [Evidence](../works/paper-xi.md#evidence)

**Source passages:**

- [Paper XI: finite theory and the comparison boundary](../../papers/paper-xi/current/publication/source/traditional/reader_route.tex#L17)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#komorebi_mathlanglandslocal). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: finite_frobenius()](../../tools/check_hand_examples.py#L354). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Follow a modular lift branch](18_LIFT_BRANCHES.md)
- [Next: Separate support from multiplicity](20_SUPPORT_AND_MULTIPLICITY.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#finite-frobenius)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
