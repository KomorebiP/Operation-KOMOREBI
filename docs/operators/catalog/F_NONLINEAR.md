# Nonlinear, obstruction, and deformation operators

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Retain mixed terms, identify obstruction spaces, and state the hypotheses for a correction or reduction.

The 17 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-102 · Directional derivative](#op-102)
- [OP-103 · Packet jet](#op-103)
- [OP-104 · Faà di Bruno composition](#op-104)
- [OP-105 · Rooted-tree evaluation](#op-105)
- [OP-106 · Polynomial fixed-point Picard operator](#op-106)
- [OP-107 · Graded packet operation](#op-107)
- [OP-108 · Finite Maurer–Cartan evaluation](#op-108)
- [OP-109 · Hilbert obstruction projector](#op-109)
- [OP-110 · Right-inverse correction operator](#op-110)
- [OP-111 · Lyapunov–Schmidt reduction](#op-111)
- [OP-112 · Nonlinear Schur elimination](#op-112)
- [OP-113 · Finite filtered correction](#op-113)
- [OP-114 · Finite spectral-sequence differential](#op-114)
- [OP-115 · Kato moving-packet transport](#op-115)
- [OP-116 · Nonlinear residue product](#op-116)
- [OP-117 · Contraction pullback](#op-117)
- [OP-118 · Coupled feedback operator](#op-118)

<a id="op-102"></a>

## OP-102. Directional derivative

**Kind:** multilinear.

```math
D^rF(x)[h_1,\ldots,h_r]
```

**Scope.** Differentiable map and declared derivative order

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Finite checks linked:** [R66](CHECKS.md#r66).

**Related entries:** [OP-103](F_NONLINEAR.md#op-103) · [OP-199](L_INTEGRATION.md#op-199).

**Composition laws:** [Fixed-weight derivatives](RELATIONS.md#rel-25).


<a id="op-103"></a>

## OP-103. Packet jet

**Kind:** multilinear.

```math
J_{b;a_1\ldots a_r}=Q_bD^rF(x)(P_{a_1}\cdot,\ldots,P_{a_r}\cdot)
```

**Scope.** Source/target packet families and differentiability

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-010](A_STRUCTURAL.md#op-010) · [OP-102](F_NONLINEAR.md#op-102) · [OP-104](F_NONLINEAR.md#op-104) · [OP-199](L_INTEGRATION.md#op-199).


<a id="op-104"></a>

## OP-104. Faà di Bruno composition

**Kind:** multilinear.

```math
D^n(F\circ G)(x)[h]=\sum_{\pi}D^{|\pi|}F(G(x))\bigl[D^{|B|}G(x)[h_B]\bigr]_{B\in\pi}
```

**Scope.** Compatible sufficiently differentiable maps. The index $\pi$ runs over set partitions of $\{1,\ldots,n\}$. The tuple $h_B$ contains directions indexed by the block $B$.

**Keep in view.** The expansion needs the evaluation point G(x) and the individual direction sets. It is multilinear in directions, not jointly in arbitrary F and G.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Finite checks linked:** [A60](CHECKS.md#a60).

**Related entries:** [OP-103](F_NONLINEAR.md#op-103).


<a id="op-105"></a>

## OP-105. Rooted-tree evaluation

**Kind:** tree construction; multilinear leaf action.

```math
\text{tree}\mapsto\text{composition of vertex multilinear maps}
```

**Scope.** Finite ordered rooted tree, fixed multilinear maps at internal vertices and independent leaf inputs. Diagonal seed specialization is nonlinear.

**Keep in view.** A fixed tree is multilinear in independent leaf inputs. Reusing the same seed at all leaves gives a polynomial, usually nonlinear, map of the seed.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Finite checks linked:** [A59](CHECKS.md#a59).

**Related entries:** [OP-106](F_NONLINEAR.md#op-106).


<a id="op-106"></a>

## OP-106. Polynomial fixed-point Picard operator

**Kind:** nonlinear.

```math
\Psi(x)=s+\sum_{r\in\mathcal A}B_r(x,\ldots,x)
```

**Scope.** Finite arity set A and supplied r-linear operations B_r. Picard iteration starts from a declared seed or initial state. Convergence requires separate norm and contraction bounds.

**Keep in view.** Source-level correction: PolynomialFixedPointProblem.map sums supplied operations directly. It does not divide them by arity factorials. Derivative tensors must first be converted to B_r=T_r/r!.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md) · [TREE: Polynomial fixed-point source: supplied multilinear operation convention](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/nonlinear/trees.py#L534-L650).

**Finite checks linked:** [A58](CHECKS.md#a58), [A59](CHECKS.md#a59).

**Related entries:** [OP-105](F_NONLINEAR.md#op-105) · [OP-108](F_NONLINEAR.md#op-108).


<a id="op-107"></a>

## OP-107. Graded packet operation

**Kind:** multilinear.

```math
T(V_{a_1},\ldots,V_{a_r})\subseteq V_{a_1+\cdots+a_r}
```

**Scope.** Specified finite grading group

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-108"></a>

## OP-108. Finite Maurer–Cartan evaluation

**Kind:** nonlinear.

```math
x\mapsto\sum_{r=1}^R\ell_r(x,\ldots,x)/r!
```

**Scope.** Supplied finite family $\ell_r$; no existence claim for missing terms

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-106](F_NONLINEAR.md#op-106).


<a id="op-109"></a>

## OP-109. Hilbert obstruction projector

**Kind:** linear.

```math
Q_{\mathrm{obs}}=I-LL^+
```

**Scope.** Fixed finite map $L:X\to Y$. In orthonormal coordinates use the ordinary Moore–Penrose inverse. In nonorthonormal coordinates use the declared metric adjoints and weighted inverse. The projector acts on $Y$.

**Keep in view.** This projector acts on the residual codomain, not on the domain of L.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-005](A_STRUCTURAL.md#op-005) · [OP-110](F_NONLINEAR.md#op-110) · [OP-185](K_METRICS.md#op-185).


<a id="op-110"></a>

## OP-110. Right-inverse correction operator

**Kind:** nonlinear.

```math
u\mapsto u-RF(u)
```

**Scope.** F:X to Y and fixed R:Y to X. A right-inverse construction is relative to a stated linearization. A root follows only with the required invariant-ball and contraction hypotheses.

**Keep in view.** The correction uses a fixed map R from residual space to state space. Contractivity is an extra hypothesis.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-109](F_NONLINEAR.md#op-109).


<a id="op-111"></a>

## OP-111. Lyapunov–Schmidt reduction

**Kind:** nonlinear.

```math
P_{\operatorname{ran}L}F(k+w(k))=0,\qquad g(k)=Q_{\mathrm{obs}}F(k+w(k))
```

**Scope.** Finite differentiable map and derivative L after a chosen recentering. The state splits into kernel coordinate k and complementary coordinate w. The range equation must admit the stated local implicit solution w(k).

**Keep in view.** The range solver w and reduced obstruction g are different nonlinear maps. A solution of the range equation alone is not a zero of F.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-102](F_NONLINEAR.md#op-102) · [OP-109](F_NONLINEAR.md#op-109) · [OP-110](F_NONLINEAR.md#op-110) · [OP-112](F_NONLINEAR.md#op-112).


<a id="op-112"></a>

## OP-112. Nonlinear Schur elimination

**Kind:** nonlinear.

```math
y=y(x)\text{ solving }G(x,y)=0
```

**Scope.** Local implicit derivative invertibility and solver validity

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-132](G_DYNAMICS.md#op-132).


<a id="op-113"></a>

## OP-113. Finite filtered correction

**Kind:** partial set-valued solver.

```math
[b]\longmapsto\{[\delta]:\operatorname{gr}(L)[\delta]=[b]\}
```

**Scope.** Specified finite filtration and associated graded map. A nonempty correction coset need not determine a unique lift or an infinite compatible branch.

**Keep in view.** The operation takes a residual class to a set or coset of corrections, not a preselected correction to itself.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-078](D_ARITHMETIC.md#op-078).


<a id="op-114"></a>

## OP-114. Finite spectral-sequence differential

**Kind:** linear.

```math
d_r:E_r^{p,q}\to E_r^{p+r,q-r+1}
```

**Scope.** Specified finite filtered cochain complex, with decreasing filtration and cohomological indexing. Each page and differential requires the defining quotient spaces.

**Keep in view.** This is the cohomological indexing convention. A source using a different filtration convention must be translated.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-169](J_REPRESENTATIONS.md#op-169).


<a id="op-115"></a>

## OP-115. Kato moving-packet transport

**Kind:** linear.

```math
\dot U(t)=K(t)U(t),\ K(t)=\sum_a\dot P_a(t)P_a(t)
```

**Scope.** Differentiable finite complete orthogonal projector family with initial condition U(0)=I. K is skew-adjoint. Exact evolution and midpoint exponential approximation are distinct.

**Keep in view.** The evolution is linear in its initial vector. Dependence on the moving projector family is nonlinear, and discretization is separate.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A38](CHECKS.md#a38), [L17](CHECKS.md#l17).

**Related entries:** [OP-009](A_STRUCTURAL.md#op-009).


<a id="op-116"></a>

## OP-116. Nonlinear residue product

**Kind:** nonlinear.

```math
Q_rF(P_ax,P_by)
```

**Scope.** Specified two-input map F and input/output selectors. A reconstruction identity must be derived from multilinearity, jets or additional structure; it is not automatic.

**Keep in view.** For a general nonlinear map, inserting separately projected inputs does not justify additive reconstruction.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Finite checks linked:** [A61](CHECKS.md#a61).


<a id="op-117"></a>

## OP-117. Contraction pullback

**Kind:** linear.

```math
(C_qf)(z)=f(qz)
```

**Scope.** Fixed q on formal series or entire functions. For functions on a bounded domain require q times that domain to lie in the function domain.

**Keep in view.** Pullback itself does not require contraction on entire functions. Contraction is an analytic guard for specific feedback theorems.

**Sources:** [SF: Special Functions reader](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/SPECIAL_FUNCTIONS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-058](C_COORDINATES.md#op-058) · [OP-060](C_COORDINATES.md#op-060) · [OP-118](F_NONLINEAR.md#op-118).


<a id="op-118"></a>

## OP-118. Coupled feedback operator

**Kind:** nonlinear.

```math
(U,V)\mapsto(U(qz)V(rz),U(az)V(bz))
```

**Scope.** Pairs of formal series or entire functions with fixed q,r,a,b. Claims of canonical entire feedback solutions retain the source hypotheses and are not proved by this entry.

**Keep in view.** The nonlinear field is distinct from a solution of its differential equation. Strict contraction is a hypothesis of the global solution results, not of the algebraic product itself.

**Sources:** [SF: Special Functions reader](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/SPECIAL_FUNCTIONS.md) · [F: Special Functions formal scope](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/SPECIAL_FUNCTIONS_FORMAL_SOURCES.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-117](F_NONLINEAR.md#op-117).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
