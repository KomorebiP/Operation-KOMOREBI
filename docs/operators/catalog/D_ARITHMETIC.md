# Prime-power and digit operators

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Follow finite prime-power data, digit carries, local masks, and lift corrections.

The 11 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-068 · Prime-power reduction](#op-068)
- [OP-069 · Truncated local p-adic coefficient operator](#op-069)
- [OP-070 · Local Mahler mask transform](#op-070)
- [OP-071 · Local mask recovery](#op-071)
- [OP-072 · Digit carry transfer matrix](#op-072)
- [OP-073 · Cartier linear representation](#op-073)
- [OP-074 · Digit Cauchy product compilation](#op-074)
- [OP-075 · Prime-free factorial unit extraction](#op-075)
- [OP-076 · Kummer carry statistic and layer transfer](#op-076)
- [OP-077 · Prime-power kernel compiler](#op-077)
- [OP-078 · Finite linear lift correction](#op-078)

<a id="op-068"></a>

## OP-068. Prime-power reduction

**Kind:** ring map.

```math
\pi_r:\mathbb Z\to\mathbb Z/p^r\mathbb Z
```

**Scope.** Prime $p$ and positive depth $r$

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md) · [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-069](D_ARITHMETIC.md#op-069).


<a id="op-069"></a>

## OP-069. Truncated local p-adic coefficient operator

**Kind:** coefficientwise ring/module map.

```math
a\mapsto a\bmod p^r
```

**Scope.** Integral coefficients reduced modulo a declared prime power p^r. It is not a precision-raising map.

**Keep in view.** This is coefficientwise application of OP-068, with a Z-module rather than field-linear interpretation.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md) · [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-068](D_ARITHMETIC.md#op-068).


<a id="op-070"></a>

## OP-070. Local Mahler mask transform

**Kind:** nonlinear.

```math
\mathcal M_p[R](z)=\prod_{j\ge0}R(z^{p^j})
```

**Scope.** Normalized unit mask R in 1+z A[[z]] over a commutative ring A, with integer radix p>=2. Each coefficient stabilizes after finitely many factors.

**Keep in view.** The infinite formal product needs R(0)=1. An arbitrary invertible constant term is insufficient.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A24](CHECKS.md#a24), [A26](CHECKS.md#a26).

**Related entries:** [OP-071](D_ARITHMETIC.md#op-071) · [OP-072](D_ARITHMETIC.md#op-072).


<a id="op-071"></a>

## OP-071. Local mask recovery

**Kind:** nonlinear.

```math
R(z)=\frac{F(z)}{F(z^p)},\qquad \mathcal M_p[R]=\frac{F(z)}{F(0)}
```

**Scope.** Formal unit F over a commutative ring. This is inverse to OP-070 on normalized series F(0)=1. Otherwise retain F(0) as separate data.

**Keep in view.** The quotient loses F(0). It reconstructs F/F(0), not an arbitrary unnormalized unit series.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A24](CHECKS.md#a24), [A25](CHECKS.md#a25).

**Related entries:** [OP-065](C_COORDINATES.md#op-065) · [OP-070](D_ARITHMETIC.md#op-070).


<a id="op-072"></a>

## OP-072. Digit carry transfer matrix

**Kind:** linear.

```math
(T_d)_{qq'}=r_{d+pq'-q}
```

**Scope.** Finite normalized local mask R with r_0=1, radix p>=2, digits 0<=d<p and a finite carry set closed under permitted transitions. Out-of-range r_t are zero.

**Keep in view.** The carry state set and terminal convention are part of the representation.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A32](CHECKS.md#a32).

**Related entries:** [OP-070](D_ARITHMETIC.md#op-070) · [OP-073](D_ARITHMETIC.md#op-073) · [OP-074](D_ARITHMETIC.md#op-074).


<a id="op-073"></a>

## OP-073. Cartier linear representation

**Kind:** finite linear representation; scalar evaluation.

```math
a_n=\mathbf uT_{d_0}\cdots T_{d_k}\mathbf v
```

**Scope.** Fixed boundary vectors and transition matrices. The digit order is least significant first. The representation and its zero-index convention must be declared.

**Keep in view.** Reading a digit word is a scalar evaluation of a represented state, not a linear map of the integer index n.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A32](CHECKS.md#a32).

**Related entries:** [OP-036](B_CYCLIC.md#op-036) · [OP-072](D_ARITHMETIC.md#op-072).


<a id="op-074"></a>

## OP-074. Digit Cauchy product compilation

**Kind:** bilinear product; algorithmic compilation.

```math
c_n=\sum_{k=0}^na_kb_{n-k}
```

**Scope.** Finite digit-local representations with explicit addition carries. This is ordinary Cauchy multiplication, not the Hurwitz product.

**Keep in view.** The Cauchy product is bilinear in sequences. Producing an automaton implementing it is an algorithmic construction.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-067](C_COORDINATES.md#op-067) · [OP-072](D_ARITHMETIC.md#op-072).


<a id="op-075"></a>

## OP-075. Prime-free factorial unit extraction

**Kind:** arithmetic.

```math
n! = p^{v_p(n!)}u_p(n!)
```

**Scope.** Units and powers modulo $p^r$

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-076"></a>

## OP-076. Kummer carry statistic and layer transfer

**Kind:** arithmetic statistic; transfer construction.

```math
v_p\binom nk=\#\{\text{carries in }k+(n-k)\text{ in base }p\}
```

**Scope.** Prime p and integers 0<=k<=n. Transfer matrices require specified carry states and count the layers of this statistic.

**Keep in view.** A valuation count is an arithmetic statistic. A layer-counting transfer matrix is a different representation of that statistic.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A31](CHECKS.md#a31).


<a id="op-077"></a>

## OP-077. Prime-power kernel compiler

**Kind:** arithmetic.

```math
k\mapsto\binom nk^s\pmod{p^r}
```

**Scope.** Integer $s\ge0$, optional defined unit twists

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A31](CHECKS.md#a31).


<a id="op-078"></a>

## OP-078. Finite linear lift correction

**Kind:** partial set-valued solver.

```math
b\longmapsto\{\delta:L\delta=b\pmod{p^r}\}
```

**Scope.** Finite modules and fixed L. A chosen right inverse needs additional solvability and selection hypotheses.

**Keep in view.** The input is the residual b and the output is a solution set, possibly empty. It is not a single-valued linear inverse without a choice.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md) · [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-113](F_NONLINEAR.md#op-113) · [OP-182](J_REPRESENTATIONS.md#op-182).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
