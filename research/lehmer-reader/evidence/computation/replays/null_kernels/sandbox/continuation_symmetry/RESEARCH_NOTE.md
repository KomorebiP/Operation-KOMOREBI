# Sum-preserving packet corrections for the Lehmer attempt

Research continuation, 26 September 2026

## Status and scope

This block does not prove that Ramanujan's tau function is nonzero at every prime. It constructs explicit polynomial corrections whose weighted five-core shell sums vanish for **every** coefficient index. Such corrections can turn a signed packet sum into a one-sign sum without changing its value. The block includes a complete six-packet elimination at index 7, fourteen rationally verified strict sign certificates, an exact obstruction to a specified seven-correction search space at index 31, and a certificate overcoming that obstruction using higher-degree corrections.

The universal null identities below follow from harmonic theta modularity and the level-one valence formula, together with exact symbolic calculations. They do not follow merely from the finite shell tests. No Lean compilation or historical-priority claim is made.

## 1. Classical packet formula and conventions

Set

\[
\mathcal V_n=\{v\in\mathbb Z^5:v_i\equiv i\pmod5,
\ \sum_i v_i=0,\ \sum_i v_i^2=10n\},
\]

\[
D(v)=\prod_{0\le i<j\le4}(v_i-v_j),\qquad W(v)=D(v)/288.
\]

The specialization of Han's V-coding identities and the Nekrasov–Okounkov identity gives

\[
\tau(n)=\sum_{v\in\mathcal V_n}W(v).
\]

Here 288 is \(1!2!3!4!\). Every packet weight is integral. One way to see integrality is the determinant of the five binomial polynomials \(\binom{v_i}{j}\). Its Vandermonde sign agrees with our convention because there are ten pairs. The cited identity and its normalization were checked against Theorems 1.1 and 1.2 on page 3 of Han's arXiv version [H].

Write \(s_m(v)=\sum_i v_i^m\). In particular \(s_1=0\) and \(s_2=10n\) on a shell.

The involution

\[
J(v)_i=-v_{(-i\bmod5)}
\]

preserves the shell and preserves \(W\). It changes the sign of every odd power sum. The associated permutation is \((1\ 4)(2\ 3)\), which is even, and \(D\) has even degree ten. Therefore

\[
\sum_{v\in\mathcal V_n}W(v)s_3(v)=0.
\]

## 2. A precise low-degree limitation

Every alternating polynomial in five variables is divisible by the Vandermonde polynomial \(D\). If its total degree is at most 13, the symmetric quotient has degree at most three. On the hyperplane \(s_1=0\), it is a linear combination of \(1,s_2,s_3\).

Consequently its shell sum is a scalar of the form \(a+10bn\), multiplied by \(\tau(n)\), up to the harmless normalization by 288. The \(s_3\) component vanishes under \(J\).

This is a limitation only for alternating polynomial refinements of total degree at most 13. It is not an impossibility theorem about all packet operations. At total degree 14 the additional symmetric invariant \(s_4\) appears.

## 3. Why the harmonic shell theta series has level one

We give the specialization of the general harmonic theta theorem [IW] rather than assuming it.

Let \(A_4=\{a\in\mathbb Z^5:\sum a_i=0\}\), with the ordinary Euclidean metric, and let \(L=\sqrt5 A_4\). The finite quadratic module is

\[
L^*/L\cong A_4^*/5A_4,
\qquad |L^*/L|=5^5.
\]

A dual vector can be written \(u_i=a_i+t/5\), with \(a_i\in\mathbb Z\), \(\sum a_i=-t\), and \(0\le t<5\).

Suppose two residues \(a_i,a_j\pmod5\) coincide. The transposition exchanging these coordinates fixes the discriminant coset. Its action on any alternating harmonic polynomial is minus one. Thus the corresponding theta component vanishes.

If all five residues are distinct, they are exactly the residues 0 through 4. Their sum is zero modulo 5. The equation \(\sum a_i=-t\) forces \(t=0\). The regular cosets are therefore precisely one free \(S_5\)-orbit of size 120. The sign-isotypic subspace of the discriminant group ring has dimension one.

For a regular representative \(u\), \(\sum u_i^2\) is divisible by 5, and also by 2 because \(\sum u_i=0\). Hence its quadratic form \(\sum u_i^2/10\) is integral. The Weil operator \(T\) is the identity on the sign line. The Weil representation descends to \(SL_2(\mathbb Z)\) since the lattice rank is even. Its restriction to that one-dimensional line has \(T=1\); the relation \((ST)^3=S^2\) then gives \(S=1\).

For any alternating homogeneous harmonic polynomial \(h\) of degree \(\nu\), the vector-valued harmonic theta theorem gives weight \(\nu+2\). The sign-line argument makes the component on our regular coset a scalar modular form for the full modular group. Its constant term is zero, so it is a cusp form. Scaling arguments of \(h\) between \(u\) and \(u/\sqrt5\) changes only an overall constant.

In particular, if \(Q\) is symmetric homogeneous of degree \(d\) and \(DQ\) is harmonic on \(\sum v_i=0\), then

\[
\Theta_Q(q)=\sum_{n\ge1}\left(\sum_{v\in\mathcal V_n}W(v)Q(v)\right)q^n
\in S_{12+d}(SL_2(\mathbb Z)).
\]

## 4. Exact symbolic harmonic construction

The Vandermonde polynomial is harmonic: its Laplacian is alternating of degree eight and so must vanish. For a symmetric polynomial \(f\), define the operator \(\mathcal L\) by

\[
\Delta_{A_4}(Df)=D\mathcal L f.
\]

Using \(s_0=5,s_1=0\),

\[
\mathcal L s_m=m\sum_{a=0}^{m-2}s_as_{m-2-a}
-\frac{m(m-1)}5s_{m-2},
\]

and

\[
\nabla s_m\cdot\nabla s_n
=mn\left(s_{m+n-2}-\frac{s_{m-1}s_{n-1}}5\right).
\]

The product rule supplies \(\mathcal L f\) for arbitrary \(f(s_2,s_3,s_4,s_5)\). Higher power sums are reduced by Newton's identities. This is implemented over exact rational polynomials in `kernel_lp.py`; despite that file's name, the symbolic operator does not use optimization or floating-point arithmetic.

For a homogeneous invariant degree \(d\), solve the rational linear equations consisting of:

1. \(\mathcal L Q=0\);
2. the first \(\lfloor(12+d)/12\rfloor\) shell coefficients of \(\Theta_Q\) vanish.

The level-one valence formula [S] implies that the resulting cusp form is identically zero. The second step is therefore a finite certificate with a universal mathematical justification, not extrapolation from a sample.

## 5. The first two universal zero-sum corrections

The construction gives

\[
Q_8=6273s_2^4-33750s_2^2s_4-56800s_2s_3^2
+69600s_3s_5+45000s_4^2
\]

and

\[
\begin{aligned}
Q_{10}={}&2091s_2^5-11250s_2^3s_4-145800s_2^2s_3^2
+409600s_2s_3s_5\\
&+15000s_2s_4^2-30000s_3^2s_4-264000s_5^2.
\end{aligned}
\]

Both \(DQ_8\) and \(DQ_{10}\) are harmonic. On the first shell there is the vector \((0,1,2,-2,-1)\), with \(s_2=10,s_3=0,s_4=34,s_5=0\), and both corrections vanish there. The corresponding theta series have weights 20 and 22. Each cusp space has dimension one and a normalized generator beginning with \(q\): \(\Delta E_4^2\) and \(\Delta E_4E_6\). Their first coefficients being zero, both theta series vanish identically.

Thus, for every positive integer \(n\),

\[
\boxed{\sum_{v\in\mathcal V_n}W(v)Q_8(v)=
\sum_{v\in\mathcal V_n}W(v)Q_{10}(v)=0.}
\]

Fourteen such corrections are retained in `KERNELS_EXTENDED.json`, with counts by invariant degree

\[
8:1,\quad10:1,\quad12:1,\quad14:2,\quad16:2,\quad18:3,\quad20:4.
\]

An invariant degree \(d\) means a total degree \(10+d\) for \(DQ\), and a theta weight \(12+d\). These are different degree conventions.

## 6. Sum-preserving sign certificates

Given any finite list of the proved null corrections, put

\[
F(v)=1+\sum_j a_j Q_j(v),\qquad a_j\in\mathbb Q.
\]

Then

\[
\boxed{\sum_{v\in\mathcal V_n}W(v)F(v)=\tau(n).}
\]

If all \(W(v)F(v)\) have one weak sign and at least one is nonzero, this certifies \(\tau(n)\ne0\). No interpolation in the coefficient index is assumed.

### Complete elimination at n=7

Choose

\[
a=\frac{383}{1411344000000},\qquad
b=\frac{139}{61158240000000},\qquad F=1+aQ_8+bQ_{10}.
\]

The shell has three pairs under \(J\). Representatives give

| Representative | W | Q8 | Q10 | F |
|---|---:|---:|---:|---:|
| (-5,-4,2,3,4) | 1176 | 712800000 | -525096000000 | 0 |
| (-5,6,2,-2,-1) | -8624 | -3790800000 | 12636000000 | 0 |
| (0,-4,7,-2,-1) | -924 | 36288000000 | -786240000000 | 299/33 |

Each conjugate has the same entries. Therefore four of six packets disappear and the remaining two are negative:

\[
\boxed{\tau(7)=2(-924)\frac{299}{33}=-16744.}
\]

Equivalently, multiply the entire identity by 183474720000000. The integer correction is

\[
183474720000000+49790Q_8+417Q_{10},
\]

with surviving value 1662392160000000. This certificate is independent of a preassigned tau(7) value; the defining-series computation is an orthogonal verification.

## 7. Exact obstruction and its removal at n=31

The seven retained corrections through invariant degree 16 do not suffice for a nontrivial one-sign certificate at 31.

Let the sixteen distinct packet signatures be represented by \(v_i\), set \(\epsilon_i=\operatorname{sgn}W(v_i)\), and take the strictly positive rational numbers \(y_i\) recorded in `DUAL_31.json`. The exact checks are

\[
\sum_i y_i=1,\qquad
\sum_i y_i\epsilon_i=0,\qquad
\sum_i y_i\epsilon_i Q_j(v_i)=0\quad(j=1,\ldots,7).
\]

For every choice of correction coefficients,

\[
\sum_i y_i\epsilon_i\left(1+\sum_j a_jQ_j(v_i)\right)=0.
\]

A strictly positive weighted average cannot be zero when all entries have one weak sign and one is nonzero. This proves impossibility **in this seven-dimensional correction span**, for either target sign. It is not a blanket impossibility theorem about degree-bounded packet methods or about all null polynomials.

After adding the retained corrections at degrees 18 and 20, an exact strictly negative certificate exists at 31. The proposed coefficients were obtained from a numerical linear program, converted to rationals, and verified on every packet using exact arithmetic. The positive dual from the smaller span does not annihilate the enlarged span.

Strict rational certificates are recorded for fourteen primes:

| p | Invariant degree used | Sign |
|---:|---:|---:|
| 2 | 8 | - |
| 3 | 8 | + |
| 5 | 8 | + |
| 7 | 10 | - |
| 11 | 8 | + |
| 13 | 12 | - |
| 17 | 8 | - |
| 19 | 14 | + |
| 23 | 14 | + |
| 29 | 16 | + |
| 31 | 20 | - |
| 37 | 20 | - |
| 47 | 14 | + |
| 59 | 20 | - |

“Degree used” does not assert optimality. In particular, no exact degree-18 impossibility certificate is claimed at 31. Unsuccessful LP proposals at other tested primes are inconclusive, not proofs of infeasibility.

## 8. An additional moment identity and the limit of extraction alone

The harmonic polynomial \(D(130s_4-47s_2^2)\) gives a weight-16 cusp form. Its first coefficient is -280, so if \(E_4\Delta=\sum a_{16}(n)q^n\), then

\[
130R_4(n)-4700n^2\tau(n)=-280a_{16}(n),
\]

or

\[
\boxed{13R_4(n)=470n^2\tau(n)-28a_{16}(n),\qquad
R_4(n)=\sum W(v)s_4(v).}
\]

Here the Eisenstein series are normalized with constant coefficient one, unlike Stein's normalization in parts of [S].

Likewise, with \(E_6\Delta=\sum a_{18}(n)q^n\), harmonicity of \(D(90s_2s_4-27s_2^3-320s_3^2)\) gives

\[
900nR_4(n)-27000n^3\tau(n)-320\sum W(v)s_3(v)^2=3600a_{18}(n).
\]

These are exact identities, but they introduce additional cusp coefficients. They do not alone force the original one to be nonzero.

## 9. Other candidate routes tested

### Root-location proposal fails

For an individual auxiliary packet polynomial \(\prod_{i<j}[(i-j)+T(c_i-c_j)]\), every finite root is rational and lies in [-4,4]. This follows from \(|i-j|\le4\) and a nonzero integer denominator \(c_i-c_j\).

The aggregate signed sum does not preserve that property. At 31, the aggregate polynomial satisfies exactly

\[
P_{31}(10)=-56767541184<0,\qquad
P_{31}(11)=4645170845280>0.
\]

It therefore has a root between 10 and 11. This is an exact counterexample to the proposed inherited root bound.

### Irreducibility evidence remains finite

The auxiliary polynomial was factored over the rationals for all 303 primes through 2000. Each of the 300 polynomials at primes at least 7 was irreducible in this range. This is not a universal irreducibility theorem. It was not used to establish any universal null identity or any sign certificate.

## 10. Audit and reproducibility

Run from the extracted `lehmer_residual_audit` directory:

```sh
python continuation_symmetry/verify_all.py
```

The verifier does not call the numerical optimizer. It verifies stored rational proposals with exact arithmetic, and checks the defining symbolic identities and finite coefficient conditions independently of the search decisions.

The retained final run reports:

- 14 exact symbolic harmonic identities;
- 26 initial zero Fourier coefficients, with the universal implication supplied by the valence proof;
- 130 shell checks: n=1,...,128 plus 2411 and 16249;
- 1,796 correction-shell identities;
- 24,509 packet involution checks;
- 130 checks of each of the weight-16 and weight-18 moment identities;
- 14 strict rational sign certificates, with all 300 packet margins checked exactly;
- the sixteen strictly positive dual weights and all eight zero relations at 31;
- the explicit six-packet elimination at 7;
- all 3,125 discriminant cosets, including exactly 120 regular ones;
- independent product versus Jacobi recurrence checks through 128;
- exact refactorization of the 303 stored auxiliary polynomials.

The mathematical proof does not rest on the number of tests. The tests authenticate implementation and certificates. Input and output hashes appear in `AUDIT_RECORD.json`; it is a plain audit record, not a schema-validated Mathbox manifest.

### Failures and limitations

The inherited aggregate root bound failed mathematically. The seven-correction approach through invariant degree16 at 31 failed mathematically, as certified by the exact dual; the extended degree20 construction overcame that specific obstruction. Failed floating-point LP proposals without an exact dual are inconclusive. No current-turn arithmetic assertion failure is reported.

## 11. The unresolved uniform step

A sufficient next theorem would guarantee, for every prime p, some finite rational combination of universally null corrections such that the corrected packets have one sign and do not all vanish. The current results do not prove that such a certificate exists for every prime, nor give a uniform bound on the necessary degree.

Allowing coefficients to depend on p makes each finite search flexible, but does not itself establish a uniform theorem. Unrestricted reweighting that merely preserves a known sum would be circular; the useful restriction here is that the available Q-polynomials are fixed, universally null, and certified without assuming the value of tau(p).

The constructive advance is an exact family of permissible corrections, not a resolution of Lehmer's conjecture.

## References

[H] Guo-Niu Han, *The Nekrasov–Okounkov hook length formula: refinement, elementary proof, extension and applications*, arXiv:0805.1398v1, 9 May 2008, Theorems 1.1 and 1.2, page 3. Published in Annales de l'Institut Fourier 60 (2010), DOI 10.5802/aif.2515.

[IW] Tomoyoshi Ibukiyama and Brandon Williams, *Hermitian modular forms and algebraic modular forms on SO(6)*, arXiv:2505.23497v1 (PDF displays 29 May 2025 and internal date June 12, 2025), section 3.4, pages 18–19. Only the established harmonic theta modularity statement in section 3.4 is used; none of that paper's proposed correspondences is assumed.

[S] William Stein, *Modular Forms: A Computational Approach*, online chapter *Modular Forms of Level 1*, Theorem 2.11 (valence), Theorem 2.14, Corollaries 2.15–2.16 (structure and dimensions), Theorem 2.17 (Eisenstein basis). Normalizations are translated as described in section 8.
