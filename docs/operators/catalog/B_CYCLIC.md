# Cyclic, spectral, and arithmetic projectors

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Select residues, characters, eigenspaces, or arithmetic components under their stated scalar assumptions.

The 15 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-025 · Residue coefficient projector](#op-025)
- [OP-026 · Roots-of-unity projector](#op-026)
- [OP-027 · One-dimensional character projector](#op-027)
- [OP-028 · Multi-index residue projector](#op-028)
- [OP-029 · Polynomial spectral projector](#op-029)
- [OP-030 · Cyclic product routing](#op-030)
- [OP-031 · Differentiation residue transport](#op-031)
- [OP-032 · Translation packet transfer](#op-032)
- [OP-033 · Residue refinement](#op-033)
- [OP-034 · CRT idempotent selector](#op-034)
- [OP-035 · CRT reconstruction](#op-035)
- [OP-036 · Cartier decimation](#op-036)
- [OP-037 · Frobenius endomorphism](#op-037)
- [OP-038 · Finite-field packet selector](#op-038)
- [OP-039 · Finite group representation projector](#op-039)

<a id="op-025"></a>

## OP-025. Residue coefficient projector

**Kind:** linear.

```math
\mathcal B_{N,r}\sum_n a_nz^n=\sum_{n\equiv r\ (N)}a_nz^n
```

**Scope.** Formal series; $N\ge1$

**Sources:** [FL: Factorial lanes worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/FACTORIAL_LANES.md) · [IV: Paper IV overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-iv.md).

**Finite checks linked:** [A11](CHECKS.md#a11), [A27](CHECKS.md#a27), [L01](CHECKS.md#l01), [L02](CHECKS.md#l02), [R08](CHECKS.md#r08), [R09](CHECKS.md#r09).

**Related entries:** [OP-026](B_CYCLIC.md#op-026) · [OP-028](B_CYCLIC.md#op-028) · [OP-031](B_CYCLIC.md#op-031) · [OP-033](B_CYCLIC.md#op-033) · [OP-036](B_CYCLIC.md#op-036) · [OP-173](C_COORDINATES.md#op-173).


<a id="op-026"></a>

## OP-026. Roots-of-unity projector

**Kind:** linear.

```math
P_r^{(N)}f(z)=N^{-1}\sum_{j=0}^{N-1}\zeta^{-rj}f(\zeta^jz)
```

**Scope.** Field containing a primitive Nth root of unity, with N nonzero and invertible. Coefficient masking OP-025 does not require roots of unity.

**Keep in view.** The displayed Fourier projector needs inverses of N and the cyclotomic character orthogonality law.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [FL: Factorial lanes worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/FACTORIAL_LANES.md).

**Finite checks linked:** [A11](CHECKS.md#a11).

**Related entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-173](C_COORDINATES.md#op-173).


<a id="op-027"></a>

## OP-027. One-dimensional character projector

**Kind:** linear.

```math
P_\chi=|G|^{-1}\sum_{g\in G}\overline{\chi(g)}\,\rho(g)
```

**Scope.** Finite group G, a complex representation rho and a one-dimensional character chi. The result is algebraically idempotent; it is an orthogonal projection when rho is unitary.

**Keep in view.** The formula applies to a one-dimensional character of any finite group, not only a cyclic group.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-039](B_CYCLIC.md#op-039).


<a id="op-028"></a>

## OP-028. Multi-index residue projector

**Kind:** linear.

```math
P_{\mathbf r}=\prod_{j}P^{(N_j)}_{r_j}
```

**Scope.** Independent multivariate coefficient coordinates, or explicitly commuting residue selectors. Each modulus is positive.

**Keep in view.** Products of selectors are projectors only with the requisite commutation, supplied here by independent coordinates.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A02](CHECKS.md#a02).

**Related entries:** [OP-025](B_CYCLIC.md#op-025).


<a id="op-029"></a>

## OP-029. Polynomial spectral projector

**Kind:** linear.

```math
P_j=\prod_{k\ne j}(T-\lambda_kI)/(\lambda_j-\lambda_k)
```

**Scope.** Finite operator whose minimal polynomial splits with no repeated roots. The listed lambdas are all its distinct eigenvalues.

**Keep in view.** Distinct eigenvalues in the formula mean distinct spectral values. Diagonalizability is essential for this simple Lagrange formula.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [R18](CHECKS.md#r18).

**Related entries:** [OP-176](C_COORDINATES.md#op-176).


<a id="op-030"></a>

## OP-030. Cyclic product routing

**Kind:** bilinear.

```math
\mathcal B_{N,r}(fg)=\sum_{\substack{0\le a,b<N\\a+b\equiv r\ (N)}}(\mathcal B_{N,a}f)(\mathcal B_{N,b}g)
```

**Scope.** Formal series over commutative ring

**Keep in view.** The sum is over the finite residue set. All cross-packet products, including carries, are retained.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [FL: Factorial lanes worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/FACTORIAL_LANES.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-174](C_COORDINATES.md#op-174).


<a id="op-031"></a>

## OP-031. Differentiation residue transport

**Kind:** linear.

```math
D\mathcal B_{N,r}=\mathcal B_{N,r-1}D
```

**Scope.** Formal derivatives; residue indices modulo $N$

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Finite checks linked:** [R10](CHECKS.md#r10).

**Related entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-053](C_COORDINATES.md#op-053).


<a id="op-032"></a>

## OP-032. Translation packet transfer

**Kind:** linear.

```math
T_{ab}(h)=P_a\tau_hP_b,\ (\tau_hf)(x)=f(x+h)
```

**Scope.** Polynomial coefficients; generally mixes residue packets

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-033"></a>

## OP-033. Residue refinement

**Kind:** linear.

```math
P_r^{(N)}=\sum_{j=0}^{M-1}P_{r+jN}^{(MN)}
```

**Scope.** Coefficient projection for integer $M\ge1$

**Sources:** [FL: Factorial lanes worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/FACTORIAL_LANES.md) · [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-173](C_COORDINATES.md#op-173).


<a id="op-034"></a>

## OP-034. CRT idempotent selector

**Kind:** linear.

```math
P_i(x)=e_ix\quad\text{in }\mathbb Z/M\mathbb Z,\qquad e_i^2=e_i
```

**Scope.** Pairwise coprime positive moduli m_i with M their product. The e_i are the CRT idempotents. P_i is linear over Z/MZ.

**Keep in view.** The operator is multiplication by an idempotent class, not the scalar class in isolation.

**Sources:** [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [L13](CHECKS.md#l13).

**Related entries:** [OP-035](B_CYCLIC.md#op-035).


<a id="op-035"></a>

## OP-035. CRT reconstruction

**Kind:** ring isomorphism; module map.

```math
x=\sum_ir_ie_i\pmod M
```

**Scope.** Product of rings $\mathbb Z/m_i\mathbb Z$ for pairwise coprime $m_i$, with $M=\prod_i m_i$. The output is a class modulo $M$, not a unique unrestricted integer.

**Keep in view.** CRT reconstruction is a ring isomorphism and a Z-module map. It is not a vector-space change over mismatched fields.

**Sources:** [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [L14](CHECKS.md#l14).

**Related entries:** [OP-034](B_CYCLIC.md#op-034).


<a id="op-036"></a>

## OP-036. Cartier decimation

**Kind:** linear.

```math
\Lambda_r\bigl(\sum_na_nz^n\bigr)=\sum_na_{pn+r}z^n
```

**Scope.** Formal series over a declared coefficient ring, integer radix p>=2 and 0<=r<p. No characteristic-p hypothesis is needed for decimation itself.

**Keep in view.** Decimation reindexes retained coefficients. It is not the same as the degree-preserving projector OP-025.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A27](CHECKS.md#a27).

**Related entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-073](D_ARITHMETIC.md#op-073).


<a id="op-037"></a>

## OP-037. Frobenius endomorphism

**Kind:** ring map.

```math
\operatorname{Fr}(x)=x^p
```

**Scope.** Commutative ring of prime characteristic $p$. Frobenius is $\mathbb F_p$-linear and is an automorphism on finite fields. Relative to a larger field of scalars it is generally semilinear.

**Keep in view.** Primality and commutativity are needed for the standard Frobenius ring endomorphism. Over extension fields it need not be linear over that whole field.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [IX: Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md).

**Finite checks linked:** [A28](CHECKS.md#a28), [A29](CHECKS.md#a29), [A30](CHECKS.md#a30).

**Related entries:** [OP-167](J_REPRESENTATIONS.md#op-167).


<a id="op-038"></a>

## OP-038. Finite-field packet selector

**Kind:** linear.

```math
P:V\to V,\ P^2=P
```

**Scope.** Specified finite-field vector space and idempotent endomorphism. Specialization of OP-009.

**Keep in view.** This is a finite-field specialization of the general idempotent operator, not a separately counted new discovery.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-009](A_STRUCTURAL.md#op-009).


<a id="op-039"></a>

## OP-039. Finite group representation projector

**Kind:** linear.

```math
P_\rho=\frac{d_\rho}{|G|}\sum_{g\in G}\overline{\chi_\rho(g)}U_g
```

**Scope.** Irreducible complex character $\chi_\rho$ of dimension $d_\rho$ and a finite representation $U$. The projector selects the isotypic component. It is orthogonal if $U$ is unitary.

**Keep in view.** The dimension factor is for an irreducible character. Unitarity distinguishes orthogonal from merely algebraic projection.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-027](B_CYCLIC.md#op-027) · [OP-137](H_QUANTUM.md#op-137).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
