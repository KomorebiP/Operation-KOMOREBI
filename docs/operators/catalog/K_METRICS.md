# Metric transport and compatibility

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

Carry the metric with the coordinates and compare adjoints, distortion, propagation, and defects.

The 8 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-185 · Metric adjoint](#op-185)
- [OP-186 · Metric-whitened representation](#op-186)
- [OP-187 · Intrinsic distortion functional](#op-187)
- [OP-188 · Determinant normalization](#op-188)
- [OP-189 · Conformal metric residual](#op-189)
- [OP-190 · Metric holonomy residual](#op-190)
- [OP-191 · Metric propagation along an edge](#op-191)
- [OP-192 · Quadratic metric-defect composition](#op-192)

<a id="op-185"></a>

## OP-185. Metric adjoint

**Kind:** linear action; conjugate-linear formation.

```math
T^\sharp=Q_X^{-1}T^*Q_Y
```

**Scope.** Positive-definite Hermitian metrics on finite source and target spaces. Here star means the raw conjugate transpose in the stored coordinates.

**Keep in view.** A singular coefficient metric cannot be inverted this way. Pass to the synthesis quotient or use an explicitly justified generalized inverse.

**Source relationship.** Explicit finite-dimensional consequence of the source metric-pairing laws.

**Sources:** [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md) · [R: Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md).

**Finite checks linked:** [R39](CHECKS.md#r39), [R40](CHECKS.md#r40), [R41](CHECKS.md#r41), [R42](CHECKS.md#r42).

**Related entries:** [OP-005](A_STRUCTURAL.md#op-005) · [OP-023](A_STRUCTURAL.md#op-023) · [OP-109](F_NONLINEAR.md#op-109) · [OP-186](K_METRICS.md#op-186) · [OP-189](K_METRICS.md#op-189) · [OP-190](K_METRICS.md#op-190) · [OP-191](K_METRICS.md#op-191).

**Composition laws:** [Metric adjoint](RELATIONS.md#rel-11).


<a id="op-186"></a>

## OP-186. Metric-whitened representation

**Kind:** linear in the represented map.

```math
B_Q(T)=R_YTR_X^{-1},\qquad Q_X=R_X^*R_X,\ Q_Y=R_Y^*R_Y
```

**Scope.** Positive-definite finite metrics and invertible metric factors. The underlying map is typed between those metric spaces.

**Keep in view.** Changing metric factors changes B only by unitary factors. It does not change its singular values.

**Source relationship.** Explicit source construction.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md).

**Finite checks linked:** [R42](CHECKS.md#r42), [R43](CHECKS.md#r43).

**Related entries:** [OP-171](A_STRUCTURAL.md#op-171) · [OP-185](K_METRICS.md#op-185) · [OP-187](K_METRICS.md#op-187).

**Composition laws:** [Metric whitening](RELATIONS.md#rel-12) · [Metric distortion](RELATIONS.md#rel-13).


<a id="op-187"></a>

## OP-187. Intrinsic distortion functional

**Kind:** nonlinear scalar functional.

```math
D_Q(T)=\frac{\sigma_{\max}(B_Q(T))}{\sigma_{\min}(B_Q(T))}
```

**Scope.** Invertible map between spaces of the same finite dimension $n\ge1$, with positive-definite Hermitian metrics. Singular maps do not receive a finite value under this contract.

**Keep in view.** Distortion is submultiplicative. Its logarithm is subadditive, not an exact additive cocycle.

**Source relationship.** Explicit source construction.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md).

**Finite checks linked:** [R43](CHECKS.md#r43), [R44](CHECKS.md#r44), [R45](CHECKS.md#r45), [R46](CHECKS.md#r46).

**Related entries:** [OP-186](K_METRICS.md#op-186) · [OP-188](K_METRICS.md#op-188) · [OP-189](K_METRICS.md#op-189) · [OP-192](K_METRICS.md#op-192).

**Composition laws:** [Metric distortion](RELATIONS.md#rel-13).


<a id="op-188"></a>

## OP-188. Determinant normalization

**Kind:** nonlinear map on invertible operators.

```math
T\longmapsto\widehat T=|\det T|^{-1/n}T
```

**Scope.** Invertible n by n real or complex matrix, $n\ge1$. The positive real nth root is used.

**Keep in view.** This sets determinant modulus to one. A negative real determinant or complex phase is not changed to +1. It removes volume scale, not shear.

**Source relationship.** Explicit source construction.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md).

**Finite checks linked:** [R47](CHECKS.md#r47).

**Related entries:** [OP-013](A_STRUCTURAL.md#op-013) · [OP-187](K_METRICS.md#op-187) · [OP-189](K_METRICS.md#op-189).


<a id="op-189"></a>

## OP-189. Conformal metric residual

**Kind:** linear in the metric pair for fixed T and scale; quadratic-affine in T.

```math
\mathcal R_{T,\lambda}(Q_X,Q_Y)=T^*Q_YT-\lambda^2Q_X
```

**Scope.** Fixed finite map T, positive scale $\lambda$, and positive-definite metrics for the geometric interpretation.

**Keep in view.** A zero residual certifies that edge under the chosen data. Common metric completion requires compatible equations across all relevant paths.

**Source relationship.** Residual form of the source conformal metric equation.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md).

**Finite checks linked:** [R45](CHECKS.md#r45), [R46](CHECKS.md#r46), [R48](CHECKS.md#r48), [R52](CHECKS.md#r52), [R53](CHECKS.md#r53).

**Related entries:** [OP-024](A_STRUCTURAL.md#op-024) · [OP-185](K_METRICS.md#op-185) · [OP-187](K_METRICS.md#op-187) · [OP-188](K_METRICS.md#op-188) · [OP-191](K_METRICS.md#op-191) · [OP-192](K_METRICS.md#op-192).

**Composition laws:** [Quadratic metric defect](RELATIONS.md#rel-14).


<a id="op-190"></a>

## OP-190. Metric holonomy residual

**Kind:** nonlinear scalar functional.

```math
\mathcal H_Q(H)=\operatorname{tr}\bigl(Q^{-1}(H-I)^*Q(H-I)\bigr)
```

**Scope.** Finite holonomy H and positive-definite Hermitian root metric Q. The result is the squared metric Hilbert–Schmidt norm.

**Keep in view.** Coordinate invariance transports both $H\mapsto gHg^{-1}$ and $Q\mapsto g^{-*}Qg^{-1}$. Keeping Q fixed gives a different comparison.

**Source relationship.** Explicit source construction.

**Sources:** [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md).

**Finite checks linked:** [R50](CHECKS.md#r50), [R51](CHECKS.md#r51).

**Related entries:** [OP-007](A_STRUCTURAL.md#op-007) · [OP-024](A_STRUCTURAL.md#op-024) · [OP-185](K_METRICS.md#op-185) · [OP-191](K_METRICS.md#op-191).

**Composition laws:** [Holonomy covariance](RELATIONS.md#rel-16).


<a id="op-191"></a>

## OP-191. Metric propagation along an edge

**Kind:** linear in the metric for fixed edge.

```math
Q_Y=T^{-*}Q_XT^{-1}
```

**Scope.** Invertible finite edge T and positive-definite source metric. This is the isometric scale-one convention.

**Keep in view.** Propagation along a path is exact. Distinct paths give the same metric only when their loop holonomy preserves the root metric.

**Source relationship.** Explicit rearrangement of the source metric-compatibility equation.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md) · [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md).

**Finite checks linked:** [R45](CHECKS.md#r45), [R48](CHECKS.md#r48), [R49](CHECKS.md#r49), [R52](CHECKS.md#r52).

**Related entries:** [OP-024](A_STRUCTURAL.md#op-024) · [OP-185](K_METRICS.md#op-185) · [OP-189](K_METRICS.md#op-189) · [OP-190](K_METRICS.md#op-190) · [OP-192](K_METRICS.md#op-192).

**Composition laws:** [Metric propagation](RELATIONS.md#rel-15).


<a id="op-192"></a>

## OP-192. Quadratic metric-defect composition

**Kind:** Hermitian residual construction.

```math
\mathcal E(UT)=\mathcal E(T)+T^*\mathcal E(U)T
```

**Scope.** $\mathcal E(T)=T^*Q_YT-Q_X$ for composable finite maps $T:X\to Y$ and $U:Y\to Z$, with the same intermediate metric.

**Keep in view.** This is an exact matrix identity. It is distinct from the scalar log-distortion inequality. Dropping the pullback factor gives a false law.

**Source relationship.** Derived composition identity proved in this compendium, not a claim of a new source theorem.

**Sources:** [DC: Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md) · [MP: Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md).

**Finite checks linked:** [R53](CHECKS.md#r53), [R54](CHECKS.md#r54).

**Related entries:** [OP-024](A_STRUCTURAL.md#op-024) · [OP-171](A_STRUCTURAL.md#op-171) · [OP-187](K_METRICS.md#op-187) · [OP-189](K_METRICS.md#op-189) · [OP-191](K_METRICS.md#op-191).

**Composition laws:** [Quadratic metric defect](RELATIONS.md#rel-14).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
