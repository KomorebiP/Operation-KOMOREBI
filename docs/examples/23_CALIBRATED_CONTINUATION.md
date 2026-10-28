# 23. Find the part of a calibration that can be reused

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: reusable calibrated core](../GLOSSARY.md#reusable-core) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

This example expands the three-coordinate calibration in Grounded Abstraction.
Work over the rational numbers with basis $e_1,e_2,e_3$. The unknown operation
$T$ is linear. Exact measurements supply only

```math
Te_1=e_1,\qquad Te_2=e_3.
```

Every linear extension consistent with those measurements is allowed. There
is no additional assumption of symmetry, invertibility or a norm bound.

## Determine the known inputs

The calibrated input span is $U=\mathrm{span}(e_1,e_2)$. Linearity determines

```math
T(ae_1+be_2)=ae_1+be_3.
```

For example, $T(2e_1-e_2)=2e_1-e_3$. A claimed measurement
$T(e_1+e_2)=e_1$ would contradict the supplied data, because linearity forces
$e_1+e_3$.

## Test the next use of the operation

The image of $e_2$ is $e_3$, which lies outside $U$. Its next image has not
been calibrated. Consider two compatible matrices, with images of basis
vectors written as columns:

```math
T_0=\begin{pmatrix}1&0&0\\0&0&0\\0&1&0\end{pmatrix},\qquad
T_1=\begin{pmatrix}1&0&1\\0&0&0\\0&1&0\end{pmatrix}.
```

Both send $e_1$ to $e_1$ and $e_2$ to $e_3$. But

```math
T_0^2e_2=0,\qquad T_1^2e_2=e_1.
```

Each matrix stays fixed throughout its own two-step calculation. The
disagreement does not rely on changing the unknown model between steps.

## Compute the reusable core

Let $S$ denote the known restriction of $T$ to $U$. Start with $U_0=U$ and
retain inputs whose known images stay inside the preceding domain:

```math
U_{j+1}=\{v\in U:Sv\in U_j\}.
```

For $v=ae_1+be_2$, its image $ae_1+be_3$ lies in $U$ exactly when $b=0$.
Consequently

```math
U_1=\mathrm{span}(e_1),\qquad U_2=U_1.
```

The iteration has stabilized. Every compatible extension fixes $e_1$, so
$T^n(ae_1)=ae_1$ for every nonnegative integer $n$. The reusable core is a
line even though the one-step calibrated domain is a plane.

## Try it

A new exact experiment supplies $Te_3=0$. What is now known? Compute
$T^2(2e_1+3e_2)$.

**Answer:** The three calibrated inputs span the full space, so the whole
operator is now $T_0$. The first image is $2e_1+3e_3$ and the second is
$2e_1$. Every input can now be followed for any number of steps.

The extra conclusion uses a new measurement. It was not implied by the
original two measurements. With a different declared class of admissible
models, the identifiable domain must be reconsidered under that class.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Exact operator calibration](../GLOSSARY.md#calibration) · [Calibration span](../GLOSSARY.md#calibration-span) · [Compatible model](../GLOSSARY.md#compatible-model) · [Linear extension](../GLOSSARY.md#linear-extension) · [Reusable calibrated core](../GLOSSARY.md#reusable-core) · [Identifiability relative to a model class](../GLOSSARY.md#identifiability)

Grounded Abstraction supplies the three-coordinate calibration used here. The reusable domain is computed for exact full-state output and the unrestricted class of compatible linear extensions.

### Grounded Abstraction

[Read](../works/monographs-grounded-abstraction.md#read) · [Written proofs](../works/monographs-grounded-abstraction.md#written-proofs) · [Lean coverage](../works/monographs-grounded-abstraction.md#lean) · [Code and setup](../works/monographs-grounded-abstraction.md#code) · [Evidence](../works/monographs-grounded-abstraction.md#evidence)

**Source passages:**

- [Grounded Abstraction: the calibrated continuation domain](../../monographs/grounded-abstraction/Grounded_Abstraction_v1.0.0.tex#L611)
- [Grounded Abstraction: the three-coordinate example](../../monographs/grounded-abstraction/Grounded_Abstraction_v1.0.0.tex#L638)


[Edition guide and reproduction instructions](../../monographs/grounded-abstraction/README.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: calibrated_continuation()](../../tools/check_hand_examples.py#L444). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Recover the memory hidden by a summary](22_HIDDEN_MEMORY.md)
- [Next: Calculate coefficients of contracted feedback](24_CONTRACTED_FEEDBACK.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#calibrated-continuation)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
