# Coordinate, polynomial, and sequence transforms

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

Move between polynomial bases, sequence coordinates, differences, recurrences, and formal operations.

The 37 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-040 · Coordinate change](#op-040)
- [OP-041 · Monomial to falling-factorial transport](#op-041)
- [OP-042 · Stirling second-kind transform](#op-042)
- [OP-043 · Signed Stirling first-kind inverse](#op-043)
- [OP-044 · Binomial transform](#op-044)
- [OP-045 · Inverse binomial transform](#op-045)
- [OP-046 · Lah coordinate transform](#op-046)
- [OP-047 · Forward finite difference](#op-047)
- [OP-048 · Newton sample-difference transform](#op-048)
- [OP-049 · Divisor Möbius inversion](#op-049)
- [OP-050 · Subset zeta transform and Mobius inverse](#op-050)
- [OP-051 · Ordinary to exponential coefficient normalization](#op-051)
- [OP-052 · General normalized basis transport](#op-052)
- [OP-053 · Formal derivative](#op-053)
- [OP-054 · Basepoint antiderivative](#op-054)
- [OP-055 · Point evaluation](#op-055)
- [OP-056 · Interval integration functional](#op-056)
- [OP-057 · Integration-constant defect projector](#op-057)
- [OP-058 · Affine pullback](#op-058)
- [OP-059 · Multiplication by coordinate](#op-059)
- [OP-060 · Formal composition operator](#op-060)
- [OP-061 · Shift polynomial](#op-061)
- [OP-062 · Appell basis change](#op-062)
- [OP-063 · Recurrence companion transfer](#op-063)
- [OP-064 · Recurrence defect extraction](#op-064)
- [OP-065 · Formal series reciprocal](#op-065)
- [OP-066 · Formal logarithm operator](#op-066)
- [OP-067 · Hurwitz product](#op-067)
- [OP-172 · Covector pullback](#op-172)
- [OP-173 · Falling-factorial residue projector](#op-173)
- [OP-174 · Transported polynomial product](#op-174)
- [OP-175 · Falling-factorial raising operator](#op-175)
- [OP-176 · Falling-factorial degree operator](#op-176)
- [OP-177 · Formal compositional inversion](#op-177)
- [OP-178 · Recurrence reconstruction](#op-178)
- [OP-203 · Formal exponential](#op-203)
- [OP-204 · Normalized coefficient multiplication](#op-204)

<a id="op-040"></a>

## OP-040. Coordinate change

**Kind:** linear.

```math
C_{S\to T}=B_T^{-1}B_S
```

**Scope.** Square invertible basis matrices for the same finite dimensional space. A rectangular full-column-rank basis is not inverted as a square matrix.

**Keep in view.** The inverse formula presupposes square bases of the same space. Rectangular subspace charts require a different coordinate solve.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [A13](CHECKS.md#a13), [R03](CHECKS.md#r03), [R57](CHECKS.md#r57).

**Related entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-062](C_COORDINATES.md#op-062) · [OP-090](E_SIGNAL.md#op-090) · [OP-091](E_SIGNAL.md#op-091) · [OP-092](E_SIGNAL.md#op-092) · [OP-171](A_STRUCTURAL.md#op-171) · [OP-194](L_INTEGRATION.md#op-194).

**Composition laws:** [Coordinate transport](RELATIONS.md#rel-03).


<a id="op-041"></a>

## OP-041. Monomial to falling-factorial transport

**Kind:** linear.

```math
\Phi(z^k)=x^{\underline{k}}
```

**Scope.** Polynomial rings over any commutative unital coefficient ring. The basis matrix and inverse are unitriangular with integer entries. Newton quotient and spectral interpolation formulas require additional units.

**Keep in view.** $\Phi$ is a linear isomorphism in positive characteristic too. It is not an algebra homomorphism for ordinary multiplication.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [A11](CHECKS.md#a11), [A12](CHECKS.md#a12), [L09](CHECKS.md#l09), [R07](CHECKS.md#r07), [R09](CHECKS.md#r09), [R18](CHECKS.md#r18).

**Related entries:** [OP-040](C_COORDINATES.md#op-040) · [OP-042](C_COORDINATES.md#op-042) · [OP-046](C_COORDINATES.md#op-046) · [OP-048](C_COORDINATES.md#op-048) · [OP-173](C_COORDINATES.md#op-173) · [OP-174](C_COORDINATES.md#op-174) · [OP-175](C_COORDINATES.md#op-175) · [OP-176](C_COORDINATES.md#op-176).

**Composition laws:** [Transported differentiation](RELATIONS.md#rel-05) · [Transported product](RELATIONS.md#rel-06).


<a id="op-042"></a>

## OP-042. Stirling second-kind transform

**Kind:** linear.

```math
(\mathcal Sa)_n=\sum_{k\le n}S(n,k)a_k
```

**Scope.** Locally finite sequence transform. For polynomial coefficients $a_n$, the falling-factorial coefficients are $b_k=\sum_{n=k}^{d}S(n,k)a_n$. This uses the transposed index orientation.

**Keep in view.** This entry is the lower-triangular sequence transform. Polynomial coordinate conversion uses the transposed index orientation.

**Sources:** [SB: Stirling Bell Fubini worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/STIRLING_BELL_FUBINI.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R07](CHECKS.md#r07).

**Related entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-043](C_COORDINATES.md#op-043) · [OP-046](C_COORDINATES.md#op-046) · [OP-173](C_COORDINATES.md#op-173).


<a id="op-043"></a>

## OP-043. Signed Stirling first-kind inverse

**Kind:** linear.

```math
(\mathcal S^{-1}b)_n=\sum_{k\le n}s(n,k)b_k
```

**Scope.** Inverse of the lower-triangular sequence transform OP-042. Polynomial coordinate conversion uses the corresponding upper-triangular connection matrix.

**Keep in view.** As for OP-042, do not identify sequence-matrix orientation with polynomial coefficient orientation.

**Sources:** [SB: Stirling Bell Fubini worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/STIRLING_BELL_FUBINI.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R07](CHECKS.md#r07).

**Related entries:** [OP-042](C_COORDINATES.md#op-042) · [OP-046](C_COORDINATES.md#op-046).


<a id="op-044"></a>

## OP-044. Binomial transform

**Kind:** linear.

```math
b_n=\sum_{k=0}^n\binom nk a_k
```

**Scope.** Sequences with triangular exact coefficients

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-045](C_COORDINATES.md#op-045).


<a id="op-045"></a>

## OP-045. Inverse binomial transform

**Kind:** linear.

```math
a_n=\sum_{k=0}^n(-1)^{n-k}\binom nk b_k
```

**Scope.** Finite triangular inverse

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-044](C_COORDINATES.md#op-044).


<a id="op-046"></a>

## OP-046. Lah coordinate transform

**Kind:** linear.

```math
x^{\overline n}=\sum_{k=0}^{n}L(n,k)x^{\underline k},\qquad b_k=\sum_{n=k}^{d}L(n,k)a_n
```

**Scope.** Coefficients a_n in the rising-factorial basis become b_k in the falling-factorial basis through degree d.

**Keep in view.** The original sequence formula did not give the claimed polynomial coordinate conversion. The source uses row k, column n equal to L(n,k).

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [COMB: Exact combinatorial coordinate source: matrix orientation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/coordinates/combinatorial.py#L69-L250).

**Finite checks linked:** [A14](CHECKS.md#a14), [A15](CHECKS.md#a15).

**Related entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-042](C_COORDINATES.md#op-042) · [OP-043](C_COORDINATES.md#op-043).


<a id="op-047"></a>

## OP-047. Forward finite difference

**Kind:** linear.

```math
(\Delta f)(x)=f(x+1)-f(x)
```

**Scope.** Polynomial or sequence carrier

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [A12](CHECKS.md#a12), [A16](CHECKS.md#a16), [R10](CHECKS.md#r10), [R12](CHECKS.md#r12), [R13](CHECKS.md#r13), [R15](CHECKS.md#r15), [R16](CHECKS.md#r16).

**Related entries:** [OP-048](C_COORDINATES.md#op-048) · [OP-173](C_COORDINATES.md#op-173) · [OP-174](C_COORDINATES.md#op-174) · [OP-175](C_COORDINATES.md#op-175) · [OP-176](C_COORDINATES.md#op-176).

**Composition laws:** [Transported differentiation](RELATIONS.md#rel-05) · [Transported product](RELATIONS.md#rel-06) · [Raising and lowering](RELATIONS.md#rel-17).


<a id="op-048"></a>

## OP-048. Newton sample-difference transform

**Kind:** linear.

```math
d_k=\Delta^kf(0),\qquad f(x)=\sum_{k=0}^{d}d_k\binom{x}{k}
```

**Scope.** Polynomials of degree at most $d$ over a $\mathbb Q$-algebra. The binomial coefficient is $d_k$ and the falling-factorial coefficient is $d_k/k!$. This quotient is not valid where $k!$ is a nonunit.

**Keep in view.** Forward differences are coefficients of binomial polynomials. Falling-factorial coefficients require division by k!.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [COMB: Exact combinatorial coordinate source: matrix orientation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/coordinates/combinatorial.py#L69-L250).

**Finite checks linked:** [A16](CHECKS.md#a16), [A17](CHECKS.md#a17).

**Related entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-047](C_COORDINATES.md#op-047) · [OP-173](C_COORDINATES.md#op-173).


<a id="op-049"></a>

## OP-049. Divisor Möbius inversion

**Kind:** linear.

```math
b(n)=\sum_{d\mid n}a(d),\ a(n)=\sum_{d\mid n}\mu(n/d)b(d)
```

**Scope.** Arithmetic functions on divisibility poset

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-050"></a>

## OP-050. Subset zeta transform and Mobius inverse

**Kind:** linear.

```math
b(S)=\sum_{T\subseteq S}a(T),\qquad a(S)=\sum_{T\subseteq S}(-1)^{|S\setminus T|}b(T)
```

**Scope.** Finite Boolean subset lattice with coefficients in a commutative ring.

**Keep in view.** The displayed forward sum was a zeta transform, not the signed Mobius inverse. Both directions are now explicit.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [COMB: Exact combinatorial coordinate source: matrix orientation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/coordinates/combinatorial.py#L69-L250).

**Finite checks linked:** [A18](CHECKS.md#a18).


<a id="op-051"></a>

## OP-051. Ordinary to exponential coefficient normalization

**Kind:** linear.

```math
\sum a_nz^n\longleftrightarrow\sum (n!a_n)z^n/n!
```

**Scope.** Q-algebra, or a finite degree range in which every required factorial is a unit. There is no general invertible ordinary/EGF normalization in characteristic p at degree p and above.

**Keep in view.** Invertibility of factorial normalization is stronger than characteristic zero. Divided-power multiplication in characteristic p does not make this change of basis invertible.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A19](CHECKS.md#a19), [L15](CHECKS.md#l15).

**Related entries:** [OP-052](C_COORDINATES.md#op-052) · [OP-067](C_COORDINATES.md#op-067) · [OP-203](C_COORDINATES.md#op-203) · [OP-204](C_COORDINATES.md#op-204).


<a id="op-052"></a>

## OP-052. General normalized basis transport

**Kind:** linear.

```math
b_n=(\eta_n/\gamma_n)a_n
```

**Scope.** Same finite polynomial or series truncation with invertible gamma_n and eta_n in the coefficient ring.

**Keep in view.** Normalizers must be units in the actual coefficient ring, not merely nonzero formal labels.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A19](CHECKS.md#a19), [A33](CHECKS.md#a33), [R24](CHECKS.md#r24).

**Related entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-204](C_COORDINATES.md#op-204).


<a id="op-053"></a>

## OP-053. Formal derivative

**Kind:** linear.

```math
D:f(x)\mapsto f'(x)
```

**Scope.** Degree bounded polynomial maps $\mathcal P_n\to\mathcal P_{n-1}$

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [A12](CHECKS.md#a12), [A13](CHECKS.md#a13), [L10](CHECKS.md#l10), [L11](CHECKS.md#l11), [R68](CHECKS.md#r68).

**Related entries:** [OP-031](B_CYCLIC.md#op-031) · [OP-054](C_COORDINATES.md#op-054) · [OP-057](C_COORDINATES.md#op-057) · [OP-200](L_INTEGRATION.md#op-200).

**Composition laws:** [Integration constant](RELATIONS.md#rel-04) · [Integration by parts](RELATIONS.md#rel-26).


<a id="op-054"></a>

## OP-054. Basepoint antiderivative

**Kind:** linear.

```math
J_a:f\mapsto\int_a^x f(t)\,dt
```

**Scope.** Polynomial map P_{n-1} to P_n over Q or a Q-algebra, with declared basepoint a. Output has value zero at a.

**Keep in view.** Antidifferentiation divides by positive integers. A Q-algebra supplies these inverses.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [L10](CHECKS.md#l10), [L11](CHECKS.md#l11).

**Related entries:** [OP-053](C_COORDINATES.md#op-053) · [OP-057](C_COORDINATES.md#op-057) · [OP-200](L_INTEGRATION.md#op-200).

**Composition laws:** [Integration constant](RELATIONS.md#rel-04).


<a id="op-055"></a>

## OP-055. Point evaluation

**Kind:** linear.

```math
e_a:f\mapsto f(a)
```

**Scope.** Polynomial covector; exact rational $a$

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R05](CHECKS.md#r05).

**Related entries:** [OP-057](C_COORDINATES.md#op-057) · [OP-172](C_COORDINATES.md#op-172) · [OP-193](L_INTEGRATION.md#op-193) · [OP-200](L_INTEGRATION.md#op-200).

**Composition laws:** [Covector pullback](RELATIONS.md#rel-08).


<a id="op-056"></a>

## OP-056. Interval integration functional

**Kind:** linear.

```math
\ell_{[a,b],\rho}(f)=\rho\int_a^b f(x)\,dx
```

**Scope.** Finite rational polynomial spaces, rational endpoints and fixed rational density. For a positive-measure interpretation impose a<=b and rho>=0.

**Keep in view.** The linear functional exists for signed constant densities as well. Nonnegative density is needed only for measure-positivity interpretations.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [R68](CHECKS.md#r68).

**Related entries:** [OP-172](C_COORDINATES.md#op-172) · [OP-194](L_INTEGRATION.md#op-194) · [OP-196](L_INTEGRATION.md#op-196) · [OP-198](L_INTEGRATION.md#op-198) · [OP-200](L_INTEGRATION.md#op-200).

**Composition laws:** [Integration by parts](RELATIONS.md#rel-26).


<a id="op-057"></a>

## OP-057. Integration-constant defect projector

**Kind:** linear.

```math
C_a=I-J_aD=\mathbf1 e_a,\qquad C_a^2=C_a
```

**Scope.** Polynomials of degree at most $n$ over a $\mathbf Q$-algebra, or over a coefficient ring where the denominators used by $J_a$ are units. The derivative lowers the degree bound and $J_a$ restores it with value zero at $a$.

**Keep in view.** The defect operator is I-JD, rather than JD itself. Its image is the constants.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md).

**Finite checks linked:** [L10](CHECKS.md#l10).

**Related entries:** [OP-053](C_COORDINATES.md#op-053) · [OP-054](C_COORDINATES.md#op-054) · [OP-055](C_COORDINATES.md#op-055) · [OP-200](L_INTEGRATION.md#op-200).

**Composition laws:** [Integration constant](RELATIONS.md#rel-04).


<a id="op-058"></a>

## OP-058. Affine pullback

**Kind:** linear.

```math
(\phi_{a,b}^*f)(x)=f(ax+b)
```

**Scope.** Polynomial carrier over a declared field, with fixed a,b. Invertible exactly when a!=0 on the full polynomial coordinate change.

**Keep in view.** Pullback is linear in f even though the input substitution is affine. Invertibility additionally requires nonzero slope.

**Sources:** [T: Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R58](CHECKS.md#r58).

**Related entries:** [OP-060](C_COORDINATES.md#op-060) · [OP-117](F_NONLINEAR.md#op-117) · [OP-195](L_INTEGRATION.md#op-195) · [OP-201](L_INTEGRATION.md#op-201).


<a id="op-059"></a>

## OP-059. Multiplication by coordinate

**Kind:** linear.

```math
(M_xf)(x)=xf(x)
```

**Scope.** Polynomial degree grows by one

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R14](CHECKS.md#r14).

**Related entries:** [OP-175](C_COORDINATES.md#op-175).


<a id="op-060"></a>

## OP-060. Formal composition operator

**Kind:** linear.

```math
\mathcal C_g(f)=f\circ g
```

**Scope.** For infinite formal series require g(0)=0. Polynomial outer functions can be substituted more generally. A finite jet substitution must respect its truncation ideal.

**Keep in view.** An arbitrary infinite formal composition is not defined at a nonzero constant term without extra convergence or nilpotence assumptions.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [A21](CHECKS.md#a21), [R19](CHECKS.md#r19).

**Related entries:** [OP-058](C_COORDINATES.md#op-058) · [OP-117](F_NONLINEAR.md#op-117) · [OP-177](C_COORDINATES.md#op-177) · [OP-195](L_INTEGRATION.md#op-195).

**Composition laws:** [Compositional inversion](RELATIONS.md#rel-19).


<a id="op-061"></a>

## OP-061. Shift polynomial

**Kind:** linear.

```math
q(L)=\sum_jq_jL^j
```

**Scope.** Canonical coefficient shift $L$; finite polynomial

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-013](A_STRUCTURAL.md#op-013).


<a id="op-062"></a>

## OP-062. Appell basis change

**Kind:** linear.

```math
P_n(x)=\sum_{k\le n}\binom nk a_{n-k}x^k
```

**Scope.** Polynomial coefficient ring with the needed binomial identities and a_0 a unit. The displayed family is triangular with leading coefficient a_0.

**Keep in view.** An Appell sequence is a basis only with a nonzero, invertible leading normalization.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-040](C_COORDINATES.md#op-040).


<a id="op-063"></a>

## OP-063. Recurrence companion transfer

**Kind:** affine state update; joint linear map.

```math
s_{n+1}=Cs_n+u_n
```

**Scope.** Fixed companion matrix C. Forcing u_n may be fixed externally, or included as a separate input. Homogeneous update uses u_n=0.

**Keep in view.** A fixed nonzero forcing term makes the state update affine, not linear. Joint dependence on state and forcing is linear.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [A09](CHECKS.md#a09), [R26](CHECKS.md#r26), [R30](CHECKS.md#r30), [R74](CHECKS.md#r74), [R76](CHECKS.md#r76).

**Related entries:** [OP-064](C_COORDINATES.md#op-064) · [OP-157](I_COMPUTATIONAL.md#op-157) · [OP-178](C_COORDINATES.md#op-178) · [OP-179](G_DYNAMICS.md#op-179) · [OP-180](G_DYNAMICS.md#op-180) · [OP-205](E_SIGNAL.md#op-205).

**Composition laws:** [Recurrence coordinates](RELATIONS.md#rel-21) · [Recursive filter continuation](RELATIONS.md#rel-28).


<a id="op-064"></a>

## OP-064. Recurrence defect extraction

**Kind:** linear.

```math
\delta_n=a_{n+d}-\sum_{j<d}c_ja_{n+j}
```

**Scope.** Finite stream and prescribed recurrence coefficients

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R26](CHECKS.md#r26), [R27](CHECKS.md#r27).

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-178](C_COORDINATES.md#op-178).

**Composition laws:** [Recurrence coordinates](RELATIONS.md#rel-21).


<a id="op-065"></a>

## OP-065. Formal series reciprocal

**Kind:** nonlinear.

```math
\mathcal R(f)=f^{-1},\ \mathcal R(f)f=1
```

**Scope.** Unit formal series; constant coefficient invertible

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [IV: Paper IV overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-iv.md).

**Finite checks linked:** [A22](CHECKS.md#a22), [A23](CHECKS.md#a23).

**Related entries:** [OP-066](C_COORDINATES.md#op-066) · [OP-071](D_ARITHMETIC.md#op-071) · [OP-177](C_COORDINATES.md#op-177) · [OP-203](C_COORDINATES.md#op-203).


<a id="op-066"></a>

## OP-066. Formal logarithm operator

**Kind:** nonlinear.

```math
\log(1+u)=\sum_{k\ge1}(-1)^{k+1}u^k/k
```

**Scope.** Q-algebra with u(0)=0, or a declared finite truncation in which each required denominator k is invertible.

**Keep in view.** Characteristic zero alone does not guarantee that 1/k exists in the coefficient ring.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A20](CHECKS.md#a20), [R21](CHECKS.md#r21).

**Related entries:** [OP-065](C_COORDINATES.md#op-065) · [OP-203](C_COORDINATES.md#op-203).

**Composition laws:** [Exponential and logarithm](RELATIONS.md#rel-20).


<a id="op-067"></a>

## OP-067. Hurwitz product

**Kind:** bilinear.

```math
(a\star_Hb)_n=\sum_k\binom nk a_kb_{n-k}
```

**Scope.** Sequences over a commutative ring, with integer binomial structure constants. The ordinary analytic EGF interpretation requires its own normalization and convergence hypotheses.

**Keep in view.** Hurwitz multiplication can be defined directly by integer binomial coefficients, even when formal factorial denominators do not exist.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md) · [SB: Stirling Bell Fubini worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/STIRLING_BELL_FUBINI.md).

**Finite checks linked:** [A33](CHECKS.md#a33), [L15](CHECKS.md#l15), [R24](CHECKS.md#r24).

**Related entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-074](D_ARITHMETIC.md#op-074) · [OP-204](C_COORDINATES.md#op-204).


<a id="op-172"></a>

## OP-172. Covector pullback

**Kind:** linear.

```math
\ell\longmapsto\ell A,\qquad (\ell A)(x)=\ell(Ax)
```

**Scope.** $A:X\to Y$ fixed and $\ell\in Y^*$. Pullback needs no inverse. For a change $y=Cx$, the same functional has target row $\ell C^{-1}$.

**Keep in view.** Pulling a functional back along a map is not the same direction as changing the coordinates used to store that functional.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [MI: Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md).

**Finite checks linked:** [R05](CHECKS.md#r05), [R06](CHECKS.md#r06), [R57](CHECKS.md#r57), [R58](CHECKS.md#r58).

**Related entries:** [OP-024](A_STRUCTURAL.md#op-024) · [OP-055](C_COORDINATES.md#op-055) · [OP-056](C_COORDINATES.md#op-056) · [OP-171](A_STRUCTURAL.md#op-171) · [OP-193](L_INTEGRATION.md#op-193) · [OP-194](L_INTEGRATION.md#op-194) · [OP-195](L_INTEGRATION.md#op-195).

**Composition laws:** [Covector pullback](RELATIONS.md#rel-08) · [Pushforward duality](RELATIONS.md#rel-23).


<a id="op-173"></a>

## OP-173. Falling-factorial residue projector

**Kind:** linear.

```math
Q_r^{(m)}=\Phi P_r^{(m)}\Phi^{-1}
```

**Scope.** $m\ge1$ and $0\le r<m$. The map $P_r^{(m)}$ selects monomial degrees modulo $m$ and $\Phi(z^k)=x^{\underline{k}}$. Finite polynomial coefficients over a commutative ring suffice.

**Keep in view.** Its labels are falling-factorial degrees, not ordinary powers of x. It survives even where a particular spectral interpolation formula fails.

**Source relationship.** Explicit source construction.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Finite checks linked:** [R08](CHECKS.md#r08), [R09](CHECKS.md#r09), [R10](CHECKS.md#r10), [R18](CHECKS.md#r18).

**Related entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-026](B_CYCLIC.md#op-026) · [OP-033](B_CYCLIC.md#op-033) · [OP-041](C_COORDINATES.md#op-041) · [OP-042](C_COORDINATES.md#op-042) · [OP-047](C_COORDINATES.md#op-047) · [OP-048](C_COORDINATES.md#op-048) · [OP-174](C_COORDINATES.md#op-174) · [OP-176](C_COORDINATES.md#op-176).

**Composition laws:** [Transported differentiation](RELATIONS.md#rel-05) · [Degree realization](RELATIONS.md#rel-18).


<a id="op-174"></a>

## OP-174. Transported polynomial product

**Kind:** bilinear.

```math
f\star g=\Phi\bigl((\Phi^{-1}f)(\Phi^{-1}g)\bigr)
```

**Scope.** Polynomial ring and invertible linear basis map $\Phi$. Multiplication is performed before transport.

**Keep in view.** For the falling-factorial map, $x\star x=x(x-1)$. The operator $\Delta$ is a derivation for $\star$, not for ordinary multiplication.

**Source relationship.** Explicit source construction.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Finite checks linked:** [R11](CHECKS.md#r11), [R12](CHECKS.md#r12), [R13](CHECKS.md#r13).

**Related entries:** [OP-030](B_CYCLIC.md#op-030) · [OP-041](C_COORDINATES.md#op-041) · [OP-047](C_COORDINATES.md#op-047) · [OP-173](C_COORDINATES.md#op-173) · [OP-175](C_COORDINATES.md#op-175).

**Composition laws:** [Transported product](RELATIONS.md#rel-06).


<a id="op-175"></a>

## OP-175. Falling-factorial raising operator

**Kind:** linear.

```math
(R f)(x)=x f(x-1),\qquad R=\Phi M_z\Phi^{-1}
```

**Scope.** Polynomial ring over a commutative coefficient ring. The map $R$ raises the degree bound by one. For the degree-$d$ square truncation in the falling-factorial basis, $[\Delta_d,R_d]=I-(d+1)E_d$, where $E_d$ projects onto the top basis vector.

**Keep in view.** $R x^{\underline{k}}=x^{\underline{k+1}}$ and $[\Delta,R]=I$ on the polynomial ring. This is not multiplication by $x$ alone. The finite boundary term vanishes when the coefficient ring kills $d+1$, including in characteristic dividing $d+1$.

**Source relationship.** Explicit consequence of the source basis and transported-product laws.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R14](CHECKS.md#r14), [R15](CHECKS.md#r15), [R16](CHECKS.md#r16).

**Related entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-047](C_COORDINATES.md#op-047) · [OP-059](C_COORDINATES.md#op-059) · [OP-174](C_COORDINATES.md#op-174) · [OP-176](C_COORDINATES.md#op-176).

**Composition laws:** [Raising and lowering](RELATIONS.md#rel-17).


<a id="op-176"></a>

## OP-176. Falling-factorial degree operator

**Kind:** linear.

```math
\mathcal N=x\nabla=\Phi(zD_z)\Phi^{-1},\quad\nabla f(x)=f(x)-f(x-1)
```

**Scope.** Polynomial ring with declared coefficient characteristic. It has eigenvalue $k$ on $x^{\underline{k}}$.

**Keep in view.** Spectral interpolation through degree d needs the differences $k-j$ to be units. In characteristic p, degree labels can collide while coefficient projectors remain distinct.

**Source relationship.** Explicit source construction.

**Sources:** [RU: Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

**Finite checks linked:** [R17](CHECKS.md#r17), [R18](CHECKS.md#r18).

**Related entries:** [OP-029](B_CYCLIC.md#op-029) · [OP-041](C_COORDINATES.md#op-041) · [OP-047](C_COORDINATES.md#op-047) · [OP-173](C_COORDINATES.md#op-173) · [OP-175](C_COORDINATES.md#op-175).

**Composition laws:** [Degree realization](RELATIONS.md#rel-18).


<a id="op-177"></a>

## OP-177. Formal compositional inversion

**Kind:** nonlinear partial operation.

```math
\phi\longmapsto\psi,\qquad\phi(\psi(z))=\psi(\phi(z))=z
```

**Scope.** $\phi(0)=0$ and the coefficient of z is a unit. Finite jets use equality modulo $z^{N+1}$.

**Keep in view.** This is inversion under substitution, not reciprocal multiplication. A vanishing linear coefficient must not be accepted as an invertible chart.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Finite checks linked:** [R19](CHECKS.md#r19), [R20](CHECKS.md#r20).

**Related entries:** [OP-060](C_COORDINATES.md#op-060) · [OP-065](C_COORDINATES.md#op-065) · [OP-203](C_COORDINATES.md#op-203).

**Composition laws:** [Compositional inversion](RELATIONS.md#rel-19).


<a id="op-178"></a>

## OP-178. Recurrence reconstruction

**Kind:** linear in initial data and defects.

```math
a_{n+d}=\sum_{j=0}^{d-1}c_j a_{n+j}+\delta_n
```

**Scope.** Fixed order $d\ge1$, finite horizon and recurrence coefficients. The input contains all d initial values and every required defect.

**Keep in view.** With the defects retained this reconstructs arbitrary finite sequences. Dropping them changes the problem to a homogeneous recurrence.

**Source relationship.** Explicit source construction.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [CC: Companion coordinate examples](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/COMPANION_COORDINATE_CALCULUS.md).

**Finite checks linked:** [R26](CHECKS.md#r26), [R27](CHECKS.md#r27), [R28](CHECKS.md#r28).

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-064](C_COORDINATES.md#op-064) · [OP-179](G_DYNAMICS.md#op-179) · [OP-180](G_DYNAMICS.md#op-180) · [OP-205](E_SIGNAL.md#op-205).

**Composition laws:** [Recurrence coordinates](RELATIONS.md#rel-21).


<a id="op-203"></a>

## OP-203. Formal exponential

**Kind:** nonlinear.

```math
\operatorname{Exp}(u)=\sum_{k\ge0}\frac{u^k}{k!}
```

**Scope.** Commutative $\mathbb Q$-algebra and $u(0)=0$, or an explicitly finite nilpotent/truncated setting with all required factorials invertible.

**Keep in view.** The exponential and formal logarithm are inverse on the stated classes. Formal coefficient identities do not require numerical convergence.

**Source relationship.** Documented formal operation; standard coefficient definition supplied explicitly.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [R21](CHECKS.md#r21), [R22](CHECKS.md#r22), [R23](CHECKS.md#r23).

**Related entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-065](C_COORDINATES.md#op-065) · [OP-066](C_COORDINATES.md#op-066) · [OP-177](C_COORDINATES.md#op-177).

**Composition laws:** [Exponential and logarithm](RELATIONS.md#rel-20).


<a id="op-204"></a>

## OP-204. Normalized coefficient multiplication

**Kind:** bilinear.

```math
(a\star_\gamma b)_n=\sum_{k=0}^{n}\frac{\gamma_n}{\gamma_k\gamma_{n-k}}a_kb_{n-k}
```

**Scope.** Basis $e_n=z^n/\gamma_n$ over a ring where the indicated normalizers are units. Integral structure constants may alternatively define a divided-power algebra.

**Keep in view.** Hurwitz multiplication is the factorial case. An integral divided-power product need not imply an invertible normalization to ordinary power-series coordinates.

**Source relationship.** Explicit source construction.

**Sources:** [G: Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md).

**Finite checks linked:** [R22](CHECKS.md#r22), [R24](CHECKS.md#r24), [R25](CHECKS.md#r25).

**Related entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-052](C_COORDINATES.md#op-052) · [OP-067](C_COORDINATES.md#op-067).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
