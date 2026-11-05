# Dynamics, inference, and elimination

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Track finite evolution, probabilistic observations, coarse dynamics, and the memory left by elimination.

The 20 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-119 · Matrix semigroup](#op-119)
- [OP-120 · Packet semigroup transfer](#op-120)
- [OP-121 · Semigroup refinement defect](#op-121)
- [OP-122 · Markov transition operator](#op-122)
- [OP-123 · Continuous Markov generator](#op-123)
- [OP-124 · Markov lumping operator](#op-124)
- [OP-125 · Conditional expectation](#op-125)
- [OP-126 · Bayesian normalization operator](#op-126)
- [OP-127 · Hidden Markov filtering operator](#op-127)
- [OP-128 · Spectral fractional power](#op-128)
- [OP-129 · Green inverse](#op-129)
- [OP-130 · Finite Feynman–Kac transfer](#op-130)
- [OP-131 · Feshbach self-energy](#op-131)
- [OP-132 · Schur complement](#op-132)
- [OP-133 · Memory-kernel operator](#op-133)
- [OP-134 · Rational memory transfer](#op-134)
- [OP-135 · Duhamel perturbation operator](#op-135)
- [OP-136 · Phase-type survival operator](#op-136)
- [OP-179 · Finite observability operator](#op-179)
- [OP-180 · Finite controllability operator](#op-180)

<a id="op-119"></a>

## OP-119. Matrix semigroup

**Kind:** linear.

```math
T_t=e^{tL},\ T_{s+t}=T_sT_t
```

**Scope.** Fixed finite matrix L. Time t>=0 for a semigroup. Finite matrices also define exponentials at negative times, without an unbounded-generator conclusion.

**Keep in view.** Each time slice acts linearly. Exponentiating a varying generator is nonlinear.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A44](CHECKS.md#a44).

**Related entries:** [OP-120](G_DYNAMICS.md#op-120) · [OP-121](G_DYNAMICS.md#op-121) · [OP-123](G_DYNAMICS.md#op-123) · [OP-128](G_DYNAMICS.md#op-128) · [OP-130](G_DYNAMICS.md#op-130) · [OP-136](G_DYNAMICS.md#op-136) · [OP-141](H_QUANTUM.md#op-141) · [OP-145](H_QUANTUM.md#op-145) · [OP-146](H_QUANTUM.md#op-146).


<a id="op-120"></a>

## OP-120. Packet semigroup transfer

**Kind:** linear.

```math
(T_t)_{ij}=P_i e^{tL}P_j
```

**Scope.** Compatible finite packet system

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-010](A_STRUCTURAL.md#op-010) · [OP-119](G_DYNAMICS.md#op-119).


<a id="op-121"></a>

## OP-121. Semigroup refinement defect

**Kind:** linear.

```math
\mathfrak D_t=CT_t-\bar T_tC
```

**Scope.** Declared aggregation $C$ and coarse evolution

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A42](CHECKS.md#a42), [A45](CHECKS.md#a45), [R83](CHECKS.md#r83), [R84](CHECKS.md#r84).

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-124](G_DYNAMICS.md#op-124) · [OP-184](I_COMPUTATIONAL.md#op-184).

**Composition laws:** [Coarse defect composition](RELATIONS.md#rel-10).

**Worked calculation:** [Test coarse descent and compose its defects](../COMPOSITION.md#coarse-defect).


<a id="op-122"></a>

## OP-122. Markov transition operator

**Kind:** linear.

```math
p\longmapsto Kp,\qquad \mathbf1^{\mathsf T}K=\mathbf1^{\mathsf T}
```

**Scope.** Nonnegative column-stochastic K. When a source uses row-stochastic P, use K=P^T.

**Keep in view.** The displayed action adopts column probabilities. A row-stochastic source matrix must be transposed.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A41](CHECKS.md#a41).

**Related entries:** [OP-123](G_DYNAMICS.md#op-123).


<a id="op-123"></a>

## OP-123. Continuous Markov generator

**Kind:** linear.

```math
\dot p=Qp,\quad \mathbf1^{\mathsf T}Q=0,\quad Q_{ij}\ge0\ (i\ne j)
```

**Scope.** Finite column-probability generator. A row-rate source uses its transpose in this action.

**Keep in view.** Column-probability convention fixes the conservation equation and the placement of a transpose.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A41](CHECKS.md#a41).

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-122](G_DYNAMICS.md#op-122) · [OP-130](G_DYNAMICS.md#op-130).


<a id="op-124"></a>

## OP-124. Markov lumping operator

**Kind:** linear.

```math
C K=\bar K C
```

**Scope.** Exact only for compatible/lumpable partition

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A42](CHECKS.md#a42), [R37](CHECKS.md#r37).

**Related entries:** [OP-121](G_DYNAMICS.md#op-121) · [OP-184](I_COMPUTATIONAL.md#op-184).


<a id="op-125"></a>

## OP-125. Conditional expectation

**Kind:** linear.

```math
E[f\mid\mathcal P]
```

**Scope.** Fixed finite probability weights and partition. Every explicitly averaged cell has positive total mass, or a null-cell convention is stated.

**Keep in view.** Positive block mass is required for the elementary weighted-average formula.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A39](CHECKS.md#a39).

**Related entries:** [OP-193](L_INTEGRATION.md#op-193).


<a id="op-126"></a>

## OP-126. Bayesian normalization operator

**Kind:** nonlinear.

```math
p\mapsto (\ell\odot p)/(\mathbf1^\top(\ell\odot p))
```

**Scope.** Nonnegative likelihood and strictly positive evidence

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A40](CHECKS.md#a40), [R78](CHECKS.md#r78).

**Related entries:** [OP-127](G_DYNAMICS.md#op-127).


<a id="op-127"></a>

## OP-127. Hidden Markov filtering operator

**Kind:** nonlinear.

```math
p\mapsto (\ell\odot Kp)/(\mathbf1^\top(\ell\odot Kp))
```

**Scope.** Finite transition/likelihood and positive denominator

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-126](G_DYNAMICS.md#op-126).


<a id="op-128"></a>

## OP-128. Spectral fractional power

**Kind:** linear.

```math
L^\alpha=V\operatorname{diag}(\lambda_j^\alpha)V^{-1}
```

**Scope.** Diagonalizable finite $L$ with a chosen scalar branch. For nonnegative Hermitian $L$ and $\alpha>0$, set $0^\alpha=0$. Set $L^0=I$ separately. Negative powers require invertibility.

**Keep in view.** Fractional matrix power is linear on state vectors for fixed L and alpha, but nonlinear in L. Branches and zero eigenvalues require guards.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-013](A_STRUCTURAL.md#op-013) · [OP-119](G_DYNAMICS.md#op-119).


<a id="op-129"></a>

## OP-129. Green inverse

**Kind:** linear.

```math
G=L^{-1}
```

**Scope.** Invertible finite boundary value operator; boundary conditions matter

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-132](G_DYNAMICS.md#op-132).


<a id="op-130"></a>

## OP-130. Finite Feynman–Kac transfer

**Kind:** linear.

```math
e^{t(Q-\operatorname{diag}V)}
```

**Scope.** Fixed finite column generator Q and real diagonal potential V. Transpose a row-generator source before using this formula. No continuum path-integral claim is included.

**Keep in view.** The formula is fixed to the column-probability convention used in OP-122 and OP-123.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-123](G_DYNAMICS.md#op-123).


<a id="op-131"></a>

## OP-131. Feshbach self-energy

**Kind:** linear action; rational formation.

```math
\Sigma(z)=B(zI-D)^{-1}C
```

**Scope.** B maps hidden to retained space, C maps retained to hidden space, and zI-D is invertible.

**Keep in view.** At fixed blocks and resolvent point, self-energy is a linear operator on the retained space. Its formation is nonlinear in D and rational in z.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-132](G_DYNAMICS.md#op-132) · [OP-134](G_DYNAMICS.md#op-134) · [OP-144](H_QUANTUM.md#op-144).


<a id="op-132"></a>

## OP-132. Schur complement

**Kind:** linear action; nonlinear construction.

```math
A-BD^{-1}C
```

**Scope.** Compatible finite block matrix with invertible D. The reduced equation also transforms the right-hand side.

**Keep in view.** The Schur complement acts linearly on retained vectors. Building it from variable blocks is nonlinear.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A43](CHECKS.md#a43).

**Related entries:** [OP-112](F_NONLINEAR.md#op-112) · [OP-129](G_DYNAMICS.md#op-129) · [OP-131](G_DYNAMICS.md#op-131) · [OP-144](H_QUANTUM.md#op-144).


<a id="op-133"></a>

## OP-133. Memory-kernel operator

**Kind:** linear.

```math
(K*x)(t)=\int_0^tK(t-s)x(s)\,ds
```

**Scope.** Finite matrix realization and chosen evolution sign convention

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Finite checks linked:** [A46](CHECKS.md#a46).

**Related entries:** [OP-134](G_DYNAMICS.md#op-134) · [OP-135](G_DYNAMICS.md#op-135) · [OP-205](E_SIGNAL.md#op-205).


<a id="op-134"></a>

## OP-134. Rational memory transfer

**Kind:** linear action; rational matrix family.

```math
\widehat K(z)=B(zI-D)^{-1}C
```

**Scope.** Fixed compatible finite B,C,D and resolvent point z. A sufficient Laplace domain is Re(z)>max Re(spec D), separately from algebraic invertibility.

**Keep in view.** The algebraic resolvent is not automatically the Laplace transform of a convergent time kernel.

**Sources:** [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A47](CHECKS.md#a47).

**Related entries:** [OP-131](G_DYNAMICS.md#op-131) · [OP-133](G_DYNAMICS.md#op-133).


<a id="op-135"></a>

## OP-135. Duhamel perturbation operator

**Kind:** linear.

```math
\mathcal D_f(t)=\int_0^t e^{(t-s)L}f(s)\,ds
```

**Scope.** Finite semigroup and integrable forcing

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A45](CHECKS.md#a45).

**Related entries:** [OP-133](G_DYNAMICS.md#op-133).


<a id="op-136"></a>

## OP-136. Phase-type survival operator

**Kind:** linear functional in initial distribution.

```math
S(t)=\alpha e^{tQ}\mathbf1
```

**Scope.** Fixed finite transient row subgenerator Q and time t>=0. The row convention is intentional and differs from column-state formulas above.

**Keep in view.** For fixed t and Q this is a linear functional of the initial row distribution alpha, not a linear map of Q.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-119](G_DYNAMICS.md#op-119).


<a id="op-179"></a>

## OP-179. Finite observability operator

**Kind:** linear.

```math
\mathcal O_m x=(Cx,CAx,\ldots,CA^{m-1}x)
```

**Scope.** Fixed finite state transition A, observation C, horizon $m\ge1$, and zero input or known input contribution subtracted.

**Keep in view.** Exact state recovery requires full column rank. A long observation list alone does not imply observability.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R28](CHECKS.md#r28), [R29](CHECKS.md#r29).

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-157](I_COMPUTATIONAL.md#op-157) · [OP-178](C_COORDINATES.md#op-178) · [OP-180](G_DYNAMICS.md#op-180) · [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-182](J_REPRESENTATIONS.md#op-182).


<a id="op-180"></a>

## OP-180. Finite controllability operator

**Kind:** linear.

```math
\mathcal C_m(u_0,\ldots,u_{m-1})=\sum_{j=0}^{m-1}A^{m-1-j}Bu_j
```

**Scope.** Fixed finite A and B, horizon $m\ge1$, zero initial state. For nonzero initial state add $A^m x_0$.

**Keep in view.** The displayed order is chronological input order. Reversing columns without reversing inputs changes the action.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R30](CHECKS.md#r30), [R31](CHECKS.md#r31).

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-157](I_COMPUTATIONAL.md#op-157) · [OP-178](C_COORDINATES.md#op-178) · [OP-179](G_DYNAMICS.md#op-179).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
