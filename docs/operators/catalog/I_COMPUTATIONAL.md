# Computational and finite model operators

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Describe structured matrix actions, finite rewrites, summary maps, and computational realizations.

The 20 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-149 · Dense matrix operator](#op-149)
- [OP-150 · Diagonal operator](#op-150)
- [OP-151 · Block diagonal operator](#op-151)
- [OP-152 · Toeplitz operator](#op-152)
- [OP-153 · Circulant operator](#op-153)
- [OP-154 · Kronecker structured operator](#op-154)
- [OP-155 · Low-rank factor operator](#op-155)
- [OP-156 · Low-rank recompression](#op-156)
- [OP-157 · Krylov subspace construction](#op-157)
- [OP-158 · Packet support propagation](#op-158)
- [OP-159 · Typed expression replay](#op-159)
- [OP-160 · Certified finite rewrite](#op-160)
- [OP-161 · Finite packet-tree compiler](#op-161)
- [OP-162 · Carrier factorization](#op-162)
- [OP-163 · Signed mass packet completion](#op-163)
- [OP-164 · Tropical residual reconstruction](#op-164)
- [OP-165 · Finite convex gauge operator](#op-165)
- [OP-166 · K-COS coefficient extraction](#op-166)
- [OP-183 · Joint query encoding](#op-183)
- [OP-184 · Descended coarse operator](#op-184)

<a id="op-149"></a>

## OP-149. Dense matrix operator

**Kind:** linear.

```math
x\mapsto Ax
```

**Scope.** Finite dense array; exactness depends on numeric backend

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-150](I_COMPUTATIONAL.md#op-150) · [OP-151](I_COMPUTATIONAL.md#op-151) · [OP-152](I_COMPUTATIONAL.md#op-152) · [OP-153](I_COMPUTATIONAL.md#op-153) · [OP-155](I_COMPUTATIONAL.md#op-155).


<a id="op-150"></a>

## OP-150. Diagonal operator

**Kind:** linear.

```math
x_i\mapsto d_ix_i
```

**Scope.** Finite coordinate carrier

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-149](I_COMPUTATIONAL.md#op-149).


<a id="op-151"></a>

## OP-151. Block diagonal operator

**Kind:** linear.

```math
\operatorname{diag}(A_1,\ldots,A_m)
```

**Scope.** Finite compatible direct sums

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-149](I_COMPUTATIONAL.md#op-149).


<a id="op-152"></a>

## OP-152. Toeplitz operator

**Kind:** linear.

```math
T_{ij}=t_{i-j}
```

**Scope.** Finite constant diagonal matrix

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-081](E_SIGNAL.md#op-081) · [OP-149](I_COMPUTATIONAL.md#op-149).


<a id="op-153"></a>

## OP-153. Circulant operator

**Kind:** linear.

```math
C_{ij}=c_{(i-j)\bmod n}
```

**Scope.** Finite cyclic matrix

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-090](E_SIGNAL.md#op-090) · [OP-149](I_COMPUTATIONAL.md#op-149).


<a id="op-154"></a>

## OP-154. Kronecker structured operator

**Kind:** linear.

```math
A\otimes B
```

**Scope.** Fixed finite factors A and B. Implementation specialization of OP-006.

**Keep in view.** This is a structured implementation of OP-006, not a second mathematically inequivalent tensor operator.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-006](A_STRUCTURAL.md#op-006).


<a id="op-155"></a>

## OP-155. Low-rank factor operator

**Kind:** linear.

```math
T=UV^*
```

**Scope.** Finite factorization with prescribed rank

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-149](I_COMPUTATIONAL.md#op-149) · [OP-156](I_COMPUTATIONAL.md#op-156).


<a id="op-156"></a>

## OP-156. Low-rank recompression

**Kind:** algorithmic.

```math
UV^*\mapsto\widetilde U\widetilde V^*
```

**Scope.** Finite factors and declared rank or tolerance. Dropped singular directions contribute an error; no exactness claim follows from a low-rank representation alone.

**Keep in view.** Recompression is a rank/tolerance-dependent algorithm, generally nonlinear and approximate.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-155](I_COMPUTATIONAL.md#op-155).


<a id="op-157"></a>

## OP-157. Krylov subspace construction

**Kind:** construction.

```math
\mathcal K_k(A,v)=\operatorname{span}\{v,Av,\ldots,A^{k-1}v\}
```

**Scope.** Fixed finite matrix A, starting vector v and integer k>=1. No projection or restriction operator is defined until a basis and coordinate maps are supplied.

**Keep in view.** The span is a subspace construction. A restriction or compression requires additional analysis and synthesis maps.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-179](G_DYNAMICS.md#op-179) · [OP-180](G_DYNAMICS.md#op-180).


<a id="op-158"></a>

## OP-158. Packet support propagation

**Kind:** combinatorial.

```math
\operatorname{supp}(UT)\subseteq\operatorname{supp}(U)\circ\operatorname{supp}(T)
```

**Scope.** Finite matrices or blocks with a specified nonzero-support notion. Boolean propagation does not detect cancellation of path sums.

**Keep in view.** Composed structural support is only an upper bound over rings with cancellation. Equality can fail.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [A51](CHECKS.md#a51).

**Related entries:** [OP-012](A_STRUCTURAL.md#op-012) · [OP-162](I_COMPUTATIONAL.md#op-162).


<a id="op-159"></a>

## OP-159. Typed expression replay

**Kind:** algorithmic.

```math
\text{typed AST}\mapsto\text{exact rational matrix normal form}
```

**Scope.** Closed well-typed expression in the supported finite rational language. Each primitive and its side conditions must be replayed.

**Keep in view.** Exact normal-form evaluation has a deliberately finite semantic domain. It is not an algorithm for equality of arbitrary analytic functions.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R79](CHECKS.md#r79), [R80](CHECKS.md#r80), [R81](CHECKS.md#r81), [R82](CHECKS.md#r82).

**Related entries:** [OP-160](I_COMPUTATIONAL.md#op-160).


<a id="op-160"></a>

## OP-160. Certified finite rewrite

**Kind:** algorithmic.

```math
e\rightsquigarrow e'\text{ with exact normal form equality}
```

**Scope.** Declared finite typing and replayed side conditions

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-159](I_COMPUTATIONAL.md#op-159).


<a id="op-161"></a>

## OP-161. Finite packet-tree compiler

**Kind:** algorithmic.

```math
\text{additive block tree}\mapsto\text{finite operator schedule}
```

**Scope.** Exact finite tree semantics; cost estimates are not hardware guarantees

**Sources:** [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-162"></a>

## OP-162. Carrier factorization

**Kind:** partial factorization construction.

```math
\phi(s(x))=t(x)
```

**Scope.** Maps s:X to S and t:X to T with s(x)=s(y) implying t(x)=t(y). Homomorphism claims additionally require the source maps to preserve the relevant operations.

**Keep in view.** Fiber constancy gives a well-defined observation on $\operatorname{im}s$. Replacing a state space for future updates additionally requires every required update to preserve those fibers.

**Sources:** [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [A51](CHECKS.md#a51), [A53](CHECKS.md#a53), [L18](CHECKS.md#l18), [R38](CHECKS.md#r38).

**Related entries:** [OP-158](I_COMPUTATIONAL.md#op-158) · [OP-163](I_COMPUTATIONAL.md#op-163) · [OP-164](I_COMPUTATIONAL.md#op-164) · [OP-183](I_COMPUTATIONAL.md#op-183) · [OP-184](I_COMPUTATIONAL.md#op-184).

**Composition laws:** [Coarse descent](RELATIONS.md#rel-09).

**Worked calculation:** [Test coarse descent and compose its defects](../COMPOSITION.md#coarse-defect).


<a id="op-163"></a>

## OP-163. Signed mass packet completion

**Kind:** additive observation; signed carrier construction.

```math
(p,n)\mapsto p-n
```

**Scope.** Nonnegative mass pairs (p,n), with value p-n. Pair product is (p1*p2+n1*n2, p1*n2+n1*p2). This completion is not asserted minimal for all future queries.

**Keep in view.** Positive and negative masses lie in a cone. The observation extends linearly to a vector space, but the completed carrier also needs its multiplication law.

**Sources:** [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [A52](CHECKS.md#a52).

**Related entries:** [OP-162](I_COMPUTATIONAL.md#op-162) · [OP-183](I_COMPUTATIONAL.md#op-183).


<a id="op-164"></a>

## OP-164. Tropical residual reconstruction

**Kind:** nonlinear.

```math
\tau\log\sum_i e^{x_i/\tau}=m+\tau\log r
```

**Scope.** Finite scores, $\tau>0$; preserves scalar sum and max, not argmax provenance

**Sources:** [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [A54](CHECKS.md#a54).

**Related entries:** [OP-162](I_COMPUTATIONAL.md#op-162) · [OP-183](I_COMPUTATIONAL.md#op-183).


<a id="op-165"></a>

## OP-165. Finite convex gauge operator

**Kind:** nonlinear.

```math
\gamma_K(x)=\inf\{t>0:x\in tK\}
```

**Scope.** Finite dimensional real space and convex absorbing K with 0 in its interior. A compact K symmetric about the origin gives a norm; without symmetry the gauge may be asymmetric.

**Keep in view.** A general convex gauge is not a norm without balance or symmetry. In the symmetric real case it is a norm.

**Sources:** [X: Convex packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CONVEX_PACKETS.md).

**Finite checks linked:** [A55](CHECKS.md#a55).


<a id="op-166"></a>

## OP-166. K-COS coefficient extraction

**Kind:** linear.

```math
c_k=\frac{2}{b-a}\int_a^bf(x)\cos\frac{k\pi(x-a)}{b-a}\,dx
```

**Scope.** Integrable f on [a,b], a<b. Reconstruction uses c_0/2 plus the nonzero cosine terms where convergence is justified. Finite truncation and tail or floating-point error require separate bounds.

**Keep in view.** The zero-frequency coefficient is half-weighted in the cosine reconstruction. Exact interval coefficients must not be conflated with characteristic-function approximations.

**Sources:** [K: K-COS work and scope](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/monographs-cos-method.md).

**Finite checks linked:** [A56](CHECKS.md#a56).

**Related entries:** [OP-091](E_SIGNAL.md#op-091).


<a id="op-183"></a>

## OP-183. Joint query encoding

**Kind:** map; linear when the queries are linear.

```math
J(x)=(s(x),t(x)),\qquad\ker J=\ker s\cap\ker t
```

**Scope.** For linear maps the displayed kernels are subspaces. For general maps read the equality as intersection of fiber-equivalence relations.

**Keep in view.** The joint observation retains both queries. It need not retain all information about the original object or every future query.

**Source relationship.** Explicit source construction.

**Sources:** [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [R36](CHECKS.md#r36).

**Related entries:** [OP-162](I_COMPUTATIONAL.md#op-162) · [OP-163](I_COMPUTATIONAL.md#op-163) · [OP-164](I_COMPUTATIONAL.md#op-164) · [OP-184](I_COMPUTATIONAL.md#op-184).


<a id="op-184"></a>

## OP-184. Descended coarse operator

**Kind:** linear when well-defined.

```math
\overline T(qx)=q(Tx)
```

**Scope.** Surjective linear observation $q:X\to Y$. A unique $\overline T$ exists exactly when $T(\ker q)\subseteq\ker q$.

**Keep in view.** Pointwise recovery of one query is weaker than closure under all future updates. The kernel condition is necessary and sufficient here.

**Source relationship.** Linear specialization of the source fiber-factorization criterion.

**Sources:** [B: Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md).

**Finite checks linked:** [R37](CHECKS.md#r37), [R38](CHECKS.md#r38), [R83](CHECKS.md#r83), [R84](CHECKS.md#r84).

**Related entries:** [OP-015](A_STRUCTURAL.md#op-015) · [OP-121](G_DYNAMICS.md#op-121) · [OP-124](G_DYNAMICS.md#op-124) · [OP-162](I_COMPUTATIONAL.md#op-162) · [OP-183](I_COMPUTATIONAL.md#op-183).

**Composition laws:** [Coarse descent](RELATIONS.md#rel-09) · [Coarse defect composition](RELATIONS.md#rel-10).

**Worked calculation:** [Test coarse descent and compose its defects](../COMPOSITION.md#coarse-defect).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
