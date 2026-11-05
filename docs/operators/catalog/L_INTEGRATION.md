# Finite integration and observation

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

Separate exact weighted sums, moment identities, pushforwards, quadrature errors, and boundary terms.

The 9 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-193 · Atomic integration functional](#op-193)
- [OP-194 · Moment integration covector](#op-194)
- [OP-195 · Finite measure pushforward](#op-195)
- [OP-196 · Partial integration on a product](#op-196)
- [OP-197 · Signed quadrature functional](#op-197)
- [OP-198 · Moment discrepancy functional](#op-198)
- [OP-199 · Fixed-weight derivative averaging](#op-199)
- [OP-200 · Integration-by-parts boundary functional](#op-200)
- [OP-201 · Affine density transport](#op-201)

<a id="op-193"></a>

## OP-193. Atomic integration functional

**Kind:** linear in the integrand.

```math
I_\mu f=\sum_{j=1}^{m}w_j f(x_j)
```

**Scope.** Fixed finite nodes and weights. Nonnegative weights define a positive atomic measure. Signed weights define a functional without an automatic positivity claim.

**Keep in view.** Vector-valued finite sums are interpreted componentwise. Exact arithmetic applies only to exact supplied evaluations and weights.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R55](CHECKS.md#r55), [R56](CHECKS.md#r56), [R59](CHECKS.md#r59), [R64](CHECKS.md#r64), [R66](CHECKS.md#r66).

**Related entries:** [OP-055](C_COORDINATES.md#op-055) · [OP-125](G_DYNAMICS.md#op-125) · [OP-172](C_COORDINATES.md#op-172) · [OP-194](L_INTEGRATION.md#op-194) · [OP-195](L_INTEGRATION.md#op-195) · [OP-196](L_INTEGRATION.md#op-196) · [OP-197](L_INTEGRATION.md#op-197) · [OP-198](L_INTEGRATION.md#op-198) · [OP-199](L_INTEGRATION.md#op-199).

**Composition laws:** [Pushforward duality](RELATIONS.md#rel-23).


<a id="op-194"></a>

## OP-194. Moment integration covector

**Kind:** linear.

```math
I_\mu p=\sum_\alpha c_\alpha m_\alpha,\qquad m_\alpha=\int x^\alpha\,d\mu
```

**Scope.** Finite polynomial support and exact known moments. In a different polynomial basis the covector must be transformed with the basis witness.

**Keep in view.** For monomial-to-basis synthesis B, the row is m transposed times B. Arbitrary weights labelled with a basis name are not a basis proof.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R56](CHECKS.md#r56), [R57](CHECKS.md#r57), [R60](CHECKS.md#r60), [R65](CHECKS.md#r65).

**Related entries:** [OP-040](C_COORDINATES.md#op-040) · [OP-056](C_COORDINATES.md#op-056) · [OP-172](C_COORDINATES.md#op-172) · [OP-193](L_INTEGRATION.md#op-193) · [OP-196](L_INTEGRATION.md#op-196) · [OP-197](L_INTEGRATION.md#op-197) · [OP-198](L_INTEGRATION.md#op-198).

**Composition laws:** [Covector pullback](RELATIONS.md#rel-08) · [Moment exactness](RELATIONS.md#rel-24) · [Finite Fubini](RELATIONS.md#rel-27).


<a id="op-195"></a>

## OP-195. Finite measure pushforward

**Kind:** linear in the measure for fixed map.

```math
\int f\,d(\phi_*\mu)=\int f\circ\phi\,d\mu
```

**Scope.** Finite atomic measures, or the declared exact affine polynomial setting. The source does not implement arbitrary nonlinear change-of-variables certification.

**Keep in view.** Noninjective maps may merge atoms and still preserve mass. A density formula requires additional hypotheses.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R58](CHECKS.md#r58), [R59](CHECKS.md#r59), [R69](CHECKS.md#r69), [R70](CHECKS.md#r70).

**Related entries:** [OP-058](C_COORDINATES.md#op-058) · [OP-060](C_COORDINATES.md#op-060) · [OP-172](C_COORDINATES.md#op-172) · [OP-193](L_INTEGRATION.md#op-193) · [OP-201](L_INTEGRATION.md#op-201).

**Composition laws:** [Pushforward duality](RELATIONS.md#rel-23).


<a id="op-196"></a>

## OP-196. Partial integration on a product

**Kind:** linear.

```math
(I_\nu^{(y)}p)(x)=\int p(x,y)\,d\nu(y)
```

**Scope.** Finite polynomial p and supplied product measures with the required moments. Finite atomic products and bounded rational interval products are covered.

**Keep in view.** The remaining x dependence is retained. A general joint measure cannot be replaced by a product of marginals without changing its correlations.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R60](CHECKS.md#r60), [R61](CHECKS.md#r61).

**Related entries:** [OP-006](A_STRUCTURAL.md#op-006) · [OP-056](C_COORDINATES.md#op-056) · [OP-193](L_INTEGRATION.md#op-193) · [OP-194](L_INTEGRATION.md#op-194).

**Composition laws:** [Finite Fubini](RELATIONS.md#rel-27).


<a id="op-197"></a>

## OP-197. Signed quadrature functional

**Kind:** linear.

```math
Q(f)=\sum_{j=1}^{m}\omega_j f(\xi_j)
```

**Scope.** Fixed finite nodes and possibly signed weights. Exact evaluation of the sum is distinct from equality with a target integral.

**Keep in view.** A degree-of-exactness certificate compares moments. It does not certify all functions or every higher polynomial degree.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R55](CHECKS.md#r55), [R62](CHECKS.md#r62), [R63](CHECKS.md#r63), [R64](CHECKS.md#r64).

**Related entries:** [OP-193](L_INTEGRATION.md#op-193) · [OP-194](L_INTEGRATION.md#op-194) · [OP-198](L_INTEGRATION.md#op-198).

**Composition laws:** [Moment exactness](RELATIONS.md#rel-24).


<a id="op-198"></a>

## OP-198. Moment discrepancy functional

**Kind:** linear.

```math
\mathcal E_{\mu,Q}(p)=I_\mu p-Q(p)=\sum_\alpha c_\alpha\bigl(m_\alpha-Q(x^\alpha)\bigr)
```

**Scope.** Fixed measure, quadrature rule, and finite polynomial space. Every basis moment in that space must be checked.

**Keep in view.** The functional vanishes on the whole space exactly when its moment residual vector is zero. One successful integrand is not sufficient.

**Source relationship.** Explicit residual form of the source moment-exactness criterion.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R62](CHECKS.md#r62), [R63](CHECKS.md#r63), [R65](CHECKS.md#r65).

**Related entries:** [OP-056](C_COORDINATES.md#op-056) · [OP-193](L_INTEGRATION.md#op-193) · [OP-194](L_INTEGRATION.md#op-194) · [OP-197](L_INTEGRATION.md#op-197).

**Composition laws:** [Moment exactness](RELATIONS.md#rel-24).


<a id="op-199"></a>

## OP-199. Fixed-weight derivative averaging

**Kind:** linear in a family of providers.

```math
D^r\!\left(\sum_jw_jF_j\right)(x)=\sum_jw_jD^rF_j(x)
```

**Scope.** Finite compatible differentiable maps, fixed parameter-independent weights, matching domains, target shapes, and derivative order.

**Keep in view.** Moving weights require extra product-rule terms. The source adapter intentionally does not supply differentiation of a varying measure.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md) · [AD: Atomic integrated derivative provider](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/integration/adapters.py).

**Finite checks linked:** [R66](CHECKS.md#r66), [R67](CHECKS.md#r67).

**Related entries:** [OP-102](F_NONLINEAR.md#op-102) · [OP-103](F_NONLINEAR.md#op-103) · [OP-193](L_INTEGRATION.md#op-193).

**Composition laws:** [Fixed-weight derivatives](RELATIONS.md#rel-25).


<a id="op-200"></a>

## OP-200. Integration-by-parts boundary functional

**Kind:** bilinear.

```math
\mathcal B_{a,b,\rho}(f,g)=\rho\bigl(f(b)g(b)-f(a)g(a)\bigr)
```

**Scope.** Polynomials on $[a,b]$ and constant density $\rho$. Integration by parts states $I(fg')+I(f'g)=\mathcal B(f,g)$.

**Keep in view.** The boundary term is part of the operator identity. Dropping it changes the bilinear pairing.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R68](CHECKS.md#r68).

**Related entries:** [OP-053](C_COORDINATES.md#op-053) · [OP-054](C_COORDINATES.md#op-054) · [OP-055](C_COORDINATES.md#op-055) · [OP-056](C_COORDINATES.md#op-056) · [OP-057](C_COORDINATES.md#op-057).

**Composition laws:** [Integration by parts](RELATIONS.md#rel-26).


<a id="op-201"></a>

## OP-201. Affine density transport

**Kind:** linear in the source measure for fixed affine map.

```math
\phi_*(\rho\,1_{[a,b]}dx)=\frac{\rho}{|s|}\,1_{\phi([a,b])}dy,\qquad\phi(x)=sx+t
```

**Scope.** $a\le b$, $\rho\ge0$ and $s\ne0$. The image interval is ordered increasingly. At $s=0$, the pushforward is an atom, not this density.

**Keep in view.** Absolute slope is required for a positive measure. Oriented integration is a different convention.

**Source relationship.** Explicit source construction.

**Sources:** [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R69](CHECKS.md#r69), [R70](CHECKS.md#r70).

**Related entries:** [OP-058](C_COORDINATES.md#op-058) · [OP-195](L_INTEGRATION.md#op-195).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
