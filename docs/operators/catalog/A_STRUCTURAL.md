# Structural operators, projectors, and transfer

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

Specify an operation, split its inputs, reconstruct its output, and compare coordinate descriptions.

The 27 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-001 · Identity operator](#op-001)
- [OP-002 · Zero operator](#op-002)
- [OP-003 · Operator composition](#op-003)
- [OP-004 · Operator sum and scaling](#op-004)
- [OP-005 · Adjoint operator](#op-005)
- [OP-006 · Tensor or Kronecker operator](#op-006)
- [OP-007 · Commutator](#op-007)
- [OP-008 · Similarity transport](#op-008)
- [OP-009 · Complete algebraic packet projectors](#op-009)
- [OP-010 · Packet block](#op-010)
- [OP-011 · Transfer block reconstruction](#op-011)
- [OP-012 · Transfer block composition](#op-012)
- [OP-013 · Operator polynomial](#op-013)
- [OP-014 · Generated operator algebra](#op-014)
- [OP-015 · Intertwining map](#op-015)
- [OP-016 · Analysis map](#op-016)
- [OP-017 · Synthesis map](#op-017)
- [OP-018 · Canonical coefficient projection](#op-018)
- [OP-019 · Canonical coefficient lift](#op-019)
- [OP-020 · Presentation bridge](#op-020)
- [OP-021 · Physical frame component](#op-021)
- [OP-022 · Sandwiched coefficient block](#op-022)
- [OP-023 · Coefficient metric transport](#op-023)
- [OP-024 · Transported bilinear form](#op-024)
- [OP-170 · Synthesis-kernel projector](#op-170)
- [OP-171 · Two-endpoint coordinate transport](#op-171)
- [OP-202 · Canonical dual frame synthesis](#op-202)

<a id="op-001"></a>

## OP-001. Identity operator

**Kind:** linear.

```math
I_X(x)=x
```

**Scope.** Identity on a declared module or vector space. In other categories it is an identity morphism, not automatically a linear map.

**Keep in view.** The linear label requires a module or vector space, rather than an arbitrary unstructured object.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-002"></a>

## OP-002. Zero operator

**Kind:** linear.

```math
0_{X,Y}(x)=0
```

**Scope.** Typed source and target spaces

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-003"></a>

## OP-003. Operator composition

**Kind:** bilinear.

```math
(U\circ T)(x)=U(Tx)
```

**Scope.** Requires matching intermediate spaces

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [R04](CHECKS.md#r04), [R40](CHECKS.md#r40).


<a id="op-004"></a>

## OP-004. Operator sum and scaling

**Kind:** linear action; operator combination.

```math
(aT+bU)x=aTx+bUx
```

**Scope.** Fixed scalars a,b and maps T,U with the same source and target over one coefficient field or ring.

**Keep in view.** This is a linear combination of compatible operators, not a claim of joint linearity in all coefficients and operators.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R80](CHECKS.md#r80).


<a id="op-005"></a>

## OP-005. Adjoint operator

**Kind:** linear action; conjugate-linear formation.

```math
\langle Tx,y\rangle_Y=\langle x,T^*y\rangle_X,\qquad (aT)^*=\overline a\,T^*
```

**Scope.** Fixed nondegenerate inner products and finite dimensional spaces. Over the reals adjoint formation is linear.

**Keep in view.** An adjoint acts linearly on vectors, but adjoint formation is conjugate-linear in a complex operator.

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [A07](CHECKS.md#a07), [R39](CHECKS.md#r39).

**Related entries:** [OP-109](F_NONLINEAR.md#op-109) · [OP-185](K_METRICS.md#op-185).

**Composition laws:** [Metric adjoint](RELATIONS.md#rel-11).


<a id="op-006"></a>

## OP-006. Tensor or Kronecker operator

**Kind:** linear action; bilinear formation.

```math
(T\otimes U)(x\otimes y)=Tx\otimes Uy
```

**Scope.** Tensor-compatible spaces

**Keep in view.** The fixed tensor operator is linear. Formation is bilinear in T and U, not jointly linear.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-154](I_COMPUTATIONAL.md#op-154) · [OP-196](L_INTEGRATION.md#op-196).


<a id="op-007"></a>

## OP-007. Commutator

**Kind:** bilinear.

```math
[T,U]=TU-UT
```

**Scope.** Endomorphisms of same space

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Finite checks linked:** [R15](CHECKS.md#r15).

**Related entries:** [OP-190](K_METRICS.md#op-190).


<a id="op-008"></a>

## OP-008. Similarity transport

**Kind:** linear.

```math
T\mapsto CTC^{-1}
```

**Scope.** Invertible coordinate change $C$

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R03](CHECKS.md#r03).

**Related entries:** [OP-171](A_STRUCTURAL.md#op-171).

**Composition laws:** [Coordinate transport](RELATIONS.md#rel-03).


<a id="op-009"></a>

## OP-009. Complete algebraic packet projectors

**Kind:** linear.

```math
P_i^2=P_i,\ P_iP_j=0\ (i\ne j),\ \sum_iP_i=I
```

**Scope.** Complete algebraic decomposition; orthogonality in an inner product is additional

**Keep in view.** Algebraic orthogonality means pairwise annihilation. It does not assert self-adjointness.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [R08](CHECKS.md#r08).

**Related entries:** [OP-038](B_CYCLIC.md#op-038) · [OP-115](F_NONLINEAR.md#op-115) · [OP-140](H_QUANTUM.md#op-140).

**Composition laws:** [Typed packet composition](RELATIONS.md#rel-01).


<a id="op-010"></a>

## OP-010. Packet block

**Kind:** linear.

```math
T_{ji}=Q_jTP_i,\qquad T:X\to Y
```

**Scope.** Complete algebraic packet families P on X and Q on Y. Both source and target are explicit.

**Keep in view.** Source and target packets must not be conflated when T is rectangular.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A01](CHECKS.md#a01), [L03](CHECKS.md#l03).

**Related entries:** [OP-103](F_NONLINEAR.md#op-103) · [OP-120](G_DYNAMICS.md#op-120).

**Composition laws:** [Typed packet composition](RELATIONS.md#rel-01).


<a id="op-011"></a>

## OP-011. Transfer block reconstruction

**Kind:** linear.

```math
T=\sum_{j,i}Q_jTP_i
```

**Scope.** Finite complete algebraic packet decompositions on the source and target.

**Keep in view.** The two inserted resolutions of identity may be on different spaces.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A01](CHECKS.md#a01), [L03](CHECKS.md#l03).


<a id="op-012"></a>

## OP-012. Transfer block composition

**Kind:** bilinear.

```math
(UT)_{ki}=\sum_j U_{kj}T_{ji}
```

**Scope.** T:X to Y, U:Y to Z, and one complete algebraic packet system on the common middle space Y.

**Keep in view.** Every intermediate packet is retained. Pairwise annihilation, not Hilbert orthogonality, supplies the multiplication law.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A01](CHECKS.md#a01), [A06](CHECKS.md#a06), [A34](CHECKS.md#a34), [L04](CHECKS.md#l04), [R04](CHECKS.md#r04).

**Related entries:** [OP-083](E_SIGNAL.md#op-083) · [OP-158](I_COMPUTATIONAL.md#op-158).

**Composition laws:** [Typed packet composition](RELATIONS.md#rel-01).


<a id="op-013"></a>

## OP-013. Operator polynomial

**Kind:** linear action; polynomial formation.

```math
p(T)=\sum_{k=0}^{d}a_kT^k
```

**Scope.** Endomorphism, finite polynomial

**Keep in view.** p(T) is linear on vectors for fixed T. Evaluation as a function of T is generally nonlinear.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [A10](CHECKS.md#a10).

**Related entries:** [OP-061](C_COORDINATES.md#op-061) · [OP-128](G_DYNAMICS.md#op-128) · [OP-188](K_METRICS.md#op-188).


<a id="op-014"></a>

## OP-014. Generated operator algebra

**Kind:** construction.

```math
\operatorname{Alg}(T_1,\ldots,T_r)
```

**Scope.** Finite dimensional represented algebra. Specify whether the generated algebra is unital. A basis computation is a separate algorithm.

**Keep in view.** An algebra generated by operators is an algebraic construction, not a single extra endomorphism.

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-015"></a>

## OP-015. Intertwining map

**Kind:** linear.

```math
BT=TA
```

**Scope.** A:X to X, B:Y to Y and T:X to Y over the same coefficient field.

**Keep in view.** The intertwining equation has typed endpoints.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [R37](CHECKS.md#r37).

**Related entries:** [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-184](I_COMPUTATIONAL.md#op-184).


<a id="op-016"></a>

## OP-016. Analysis map

**Kind:** linear.

```math
A_X:X\longrightarrow K_X
```

**Scope.** Finite frame/analysis presentation

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [AS: Analysis and synthesis systems](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md).

**Finite checks linked:** [A35](CHECKS.md#a35), [L05](CHECKS.md#l05), [L07](CHECKS.md#l07), [R01](CHECKS.md#r01).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-094](E_SIGNAL.md#op-094) · [OP-202](A_STRUCTURAL.md#op-202).


<a id="op-017"></a>

## OP-017. Synthesis map

**Kind:** linear.

```math
S_X:K_X\longrightarrow X,\ S_XA_X=I_X
```

**Scope.** Finite analysis-synthesis pair

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [AS: Analysis and synthesis systems](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md).

**Finite checks linked:** [A03](CHECKS.md#a03), [A35](CHECKS.md#a35), [L05](CHECKS.md#l05), [L07](CHECKS.md#l07), [R01](CHECKS.md#r01), [R71](CHECKS.md#r71).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-094](E_SIGNAL.md#op-094) · [OP-202](A_STRUCTURAL.md#op-202).


<a id="op-018"></a>

## OP-018. Canonical coefficient projection

**Kind:** linear.

```math
P_X=A_XS_X,\quad P_X^2=P_X,\quad \ker P_X=\ker S_X
```

**Scope.** Finite analysis and synthesis with S_X A_X=I_X. I-P_X projects onto the synthesis kernel.

**Keep in view.** AS selects canonical represented coefficients. The complementary gauge projector is I-AS.

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [A03](CHECKS.md#a03), [R01](CHECKS.md#r01), [R02](CHECKS.md#r02), [R71](CHECKS.md#r71).

**Related entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017) · [OP-019](A_STRUCTURAL.md#op-019) · [OP-020](A_STRUCTURAL.md#op-020) · [OP-023](A_STRUCTURAL.md#op-023) · [OP-170](A_STRUCTURAL.md#op-170) · [OP-202](A_STRUCTURAL.md#op-202).

**Composition laws:** [Gauge complement](RELATIONS.md#rel-07).


<a id="op-019"></a>

## OP-019. Canonical coefficient lift

**Kind:** linear.

```math
\widehat T=A_YTS_X
```

**Scope.** Physical map $T:X\to Y$; coefficient lift

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [A04](CHECKS.md#a04), [L08](CHECKS.md#l08).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-023](A_STRUCTURAL.md#op-023) · [OP-170](A_STRUCTURAL.md#op-170).

**Composition laws:** [Presentation bridge](RELATIONS.md#rel-02).


<a id="op-020"></a>

## OP-020. Presentation bridge

**Kind:** linear.

```math
R=A_{Y,\mathrm{in}}S_{Y,\mathrm{out}}
```

**Scope.** Different presentations of same physical intermediate space

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [A05](CHECKS.md#a05), [L08](CHECKS.md#l08).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-023](A_STRUCTURAL.md#op-023) · [OP-170](A_STRUCTURAL.md#op-170).

**Composition laws:** [Presentation bridge](RELATIONS.md#rel-02).


<a id="op-021"></a>

## OP-021. Physical frame component

**Kind:** linear.

```math
C_i=S_XE_iA_X
```

**Scope.** Sums to identity; need not be idempotent for redundant frames

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [AS: Analysis and synthesis systems](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md).

**Finite checks linked:** [A06](CHECKS.md#a06), [L06](CHECKS.md#l06).

**Related entries:** [OP-089](E_SIGNAL.md#op-089).


<a id="op-022"></a>

## OP-022. Sandwiched coefficient block

**Kind:** linear.

```math
E_j\widehat T E_i
```

**Scope.** Aligned coefficient partition; supports exact block composition

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [A04](CHECKS.md#a04).


<a id="op-023"></a>

## OP-023. Coefficient metric transport

**Kind:** metric construction; linear pullback.

```math
H_X=S_X^*S_X,\ R^*H_YR=H_X
```

**Scope.** Finite presentations of one physical inner-product space in orthonormal physical coordinates. For a physical metric $Q$, use $H_X=S_X^*QS_X$. Its kernel is $\ker S_X$ when $Q$ is positive definite.

**Keep in view.** The metric is quadratic in S. Pullback is linear in the metric for a fixed bridge R.

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [A05](CHECKS.md#a05), [R41](CHECKS.md#r41).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-019](A_STRUCTURAL.md#op-019) · [OP-020](A_STRUCTURAL.md#op-020) · [OP-024](A_STRUCTURAL.md#op-024) · [OP-170](A_STRUCTURAL.md#op-170) · [OP-185](K_METRICS.md#op-185).


<a id="op-024"></a>

## OP-024. Transported bilinear form

**Kind:** linear.

```math
G\mapsto C^{-\mathsf T}GC^{-1}\quad\text{(bilinear)}
```

**Scope.** Fixed invertible coordinate change $C$. For a complex Hermitian form use $H\mapsto C^{-*}HC^{-1}$, where $C^{-*}=(C^{-1})^*$.

**Keep in view.** Transpose is correct for bilinear forms. Hermitian forms require conjugate transpose.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R06](CHECKS.md#r06), [R49](CHECKS.md#r49), [R50](CHECKS.md#r50).

**Related entries:** [OP-023](A_STRUCTURAL.md#op-023) · [OP-171](A_STRUCTURAL.md#op-171) · [OP-172](C_COORDINATES.md#op-172) · [OP-189](K_METRICS.md#op-189) · [OP-190](K_METRICS.md#op-190) · [OP-191](K_METRICS.md#op-191) · [OP-192](K_METRICS.md#op-192).

**Composition laws:** [Metric propagation](RELATIONS.md#rel-15) · [Holonomy covariance](RELATIONS.md#rel-16).


<a id="op-170"></a>

## OP-170. Synthesis-kernel projector

**Kind:** linear.

```math
G_X=I_{K_X}-A_XS_X,\qquad \operatorname{im}G_X=\ker S_X
```

**Scope.** Finite maps $A_X:X\to K_X$, $S_X:K_X\to X$ with $S_XA_X=I_X$.

**Keep in view.** This complementary idempotent isolates coefficient changes invisible to synthesis. It is generally oblique, not an orthogonal projector.

**Source relationship.** Explicit source construction.

**Sources:** [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md).

**Finite checks linked:** [R01](CHECKS.md#r01), [R02](CHECKS.md#r02).

**Related entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-019](A_STRUCTURAL.md#op-019) · [OP-020](A_STRUCTURAL.md#op-020) · [OP-023](A_STRUCTURAL.md#op-023) · [OP-202](A_STRUCTURAL.md#op-202).

**Composition laws:** [Gauge complement](RELATIONS.md#rel-07).


<a id="op-171"></a>

## OP-171. Two-endpoint coordinate transport

**Kind:** linear in the represented map.

```math
T\longmapsto C_YTC_X^{-1}
```

**Scope.** $T:X\to Y$ may be rectangular. $C_X$ and $C_Y$ are invertible coordinate changes on the source and target separately.

**Keep in view.** Similarity is the endomorphism specialization. A rectangular map cannot be transported using one arbitrary conjugating matrix.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R03](CHECKS.md#r03), [R04](CHECKS.md#r04), [R05](CHECKS.md#r05), [R53](CHECKS.md#r53), [R83](CHECKS.md#r83).

**Related entries:** [OP-008](A_STRUCTURAL.md#op-008) · [OP-024](A_STRUCTURAL.md#op-024) · [OP-040](C_COORDINATES.md#op-040) · [OP-172](C_COORDINATES.md#op-172) · [OP-186](K_METRICS.md#op-186) · [OP-192](K_METRICS.md#op-192).

**Composition laws:** [Coordinate transport](RELATIONS.md#rel-03) · [Metric whitening](RELATIONS.md#rel-12).


<a id="op-202"></a>

## OP-202. Canonical dual frame synthesis

**Kind:** linear action; nonlinear construction.

```math
S_A=(A^*A)^{-1}A^*,\qquad S_AA=I
```

**Scope.** Finite full-column-rank analysis A with specified inner products and orthonormal stored coordinates for this formula.

**Keep in view.** This is the general frame construction behind OP-094. It is not counted as an inequivalent primitive. Rank-deficient A requires a different reconstruction claim.

**Source relationship.** Explicit source construction.

**Sources:** [AS: Analysis and synthesis systems](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md) · [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md).

**Finite checks linked:** [R71](CHECKS.md#r71), [R72](CHECKS.md#r72).

**Related entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017) · [OP-018](A_STRUCTURAL.md#op-018) · [OP-094](E_SIGNAL.md#op-094) · [OP-170](A_STRUCTURAL.md#op-170).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
