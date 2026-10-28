# 17. Calculate quantum measurement and dephasing

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: density matrix](../GLOSSARY.md#density-matrix) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Work in $\mathbb C^2$ with its usual inner product. The normalized state

```math
\psi=\begin{pmatrix}3/5\\4i/5\end{pmatrix}
```

has squared norm $9/25+16/25=1$. This is a finite example for reading Paper VII.

## Form the density matrix

Take the conjugate transpose $\psi^*=(3/5,-4i/5)$. Then

```math
\rho=\psi\psi^*
=\begin{pmatrix}9/25&-12i/25\\12i/25&16/25\end{pmatrix}.
```

It is Hermitian and has trace one. Also
$\rho^2=\psi(\psi^*\psi)\psi^*=\rho$, so its purity $\operatorname{tr}(\rho^2)$
is one. Positivity follows from $v^*\rho v=|\psi^*v|^2\ge0$.

## Measure in the coordinate basis

Use $P_0=\operatorname{diag}(1,0)$ and $P_1=\operatorname{diag}(0,1)$.
The outcome probabilities are

```math
p_0=\operatorname{tr}(P_0\rho)=9/25,\qquad
p_1=\operatorname{tr}(P_1\rho)=16/25.
```

If the outcome is recorded, the corresponding normalized density matrices
are $P_0$ and $P_1$. If the outcome is forgotten, the state is

```math
\Phi(\rho)=P_0\rho P_0+P_1\rho P_1
=\begin{pmatrix}9/25&0\\0&16/25\end{pmatrix}.
```

The two projectors are Kraus operators satisfying $P_0^*P_0+P_1^*P_1=I$.
The channel preserves trace. Its output purity is

```math
(9/25)^2+(16/25)^2=337/625<1.
```

## See what a relative phase changes

The unitary $U=\operatorname{diag}(1,-i)$ sends $\psi$ to
$\phi=(3/5,4/5)^{\mathsf T}$. These two states have the same coordinate-basis
probabilities, but they need not agree in another basis.
Apply the Hadamard matrix

```math
H=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}.
```

For $H\psi$, the probabilities are $|3+4i|^2/50=1/2$ and
$|3-4i|^2/50=1/2$. For $H\phi$, they are $7^2/50=49/50$ and
$(-1)^2/50=1/50$. Relative phase therefore matters even when the first
measurement probabilities agree.

## Try it

Repeat the probability and dephasing-purity calculations for
$\chi=(4/5,3/5)^{\mathsf T}$.

**Answer:** Coordinate probabilities are $16/25$ and $9/25$. The dephased
purity is again $337/625$. Applying $H$ gives probabilities $49/50$ and $1/50$.
The calculation concerns this finite system. Paper VII’s continuum targets
require their separately stated constructions.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Complex conjugate](../GLOSSARY.md#complex-conjugate) · [Adjoint matrix](../GLOSSARY.md#adjoint) · [Unitary matrix](../GLOSSARY.md#unitary) · [Quantum amplitude](../GLOSSARY.md#amplitude) · [Density matrix](../GLOSSARY.md#density-matrix) · [Matrix trace](../GLOSSARY.md#trace) · [Born probability](../GLOSSARY.md#born-probability) · [Purity of a density matrix](../GLOSSARY.md#purity) · [Dephasing](../GLOSSARY.md#dephasing) · [Kraus operators](../GLOSSARY.md#kraus-operator) · [Hermitian matrix](../GLOSSARY.md#hermitian) · [Positive semidefinite matrix](../GLOSSARY.md#positive-semidefinite) · [Coherence in a chosen basis](../GLOSSARY.md#coherence)

Paper VII develops finite quantum constructions and separate continuum research targets. This example covers one two-dimensional state, a unitary phase change and a measurement channel.

### Paper VII: Quantum Seed Calculus

[Read](../works/paper-vii.md#read) · [Written proofs](../works/paper-vii.md#written-proofs) · [Lean coverage](../works/paper-vii.md#lean) · [Code and setup](../works/paper-vii.md#code) · [Evidence](../works/paper-vii.md#evidence)

**Source passages:**

- [Paper VII: measurements and channels](../../papers/paper-vii/current/editable/traditional/parts/01_finite_core.tex#L670)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#quantum-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: quantum_measurement()](../../tools/check_hand_examples.py#L305). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Split reciprocal coefficients into cyclic packets](16_CYCLIC_RECIPROCALS.md)
- [Next: Follow a modular lift branch](18_LIFT_BRANCHES.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#quantum-measurement)
