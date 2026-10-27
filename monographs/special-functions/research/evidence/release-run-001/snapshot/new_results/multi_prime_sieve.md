# Finite-prime sieve families and explicit detection of signed atoms

Checkpoint SF-DISCOVERY-100. This extends the one-prime route to a genuine finite-prime parameter family. The results below are local mathematical derivations. They do not assert historical priority. Classical orthogonal-polynomial mechanisms are identified as such.

## Definition and exact coordinates

Let \(F\) be a finite set of distinct primes, let \(\boldsymbol\lambda=(\lambda_p)_{p\in F}\), and put

\[
x_n=(1-n^{-2})^2,\qquad
\kappa_F(n;\boldsymbol\lambda)=\prod_{p\in F}(1+\lambda_p\mathbf1_{p\mid n}),
\]
\[
\nu_{F,\boldsymbol\lambda}
=\sum_{n\ge1}\mu(n)^2n^{-4}\kappa_F(n;\boldsymbol\lambda)\delta_{x_n}.
\]

The mass at \(x_1=0\) is exactly 1. A strength \(\lambda_p=-1\) deletes every squarefree atom divisible by \(p\). Several deletions commute. The depth-\(k\) family uses \(x^k\,d\nu\), for integers \(k\ge0\).

Write \(D(s)=\zeta(s)/\zeta(2s)\). For arbitrary finite complex strengths and \(\Re s>1\), absolute convergence permits expansion of the finite prime product. The local squarefree Euler factors give

\[
Z_F(s;\boldsymbol\lambda)
=\sum_{n\ge1}\mu(n)^2n^{-s}\kappa_F(n;\boldsymbol\lambda)
=D(s)\prod_{p\in F}\left(1+\frac{\lambda_p}{p^s+1}\right).
\]

Equivalently, expansion in subsets \(S\subseteq F\) gives the coefficient
\(D(s)/\prod_{p\in S}(p^s+1)\) for \(\prod_{p\in S}\lambda_p\). This is an independently useful coordinate formula for prime overlap.

Consequently

\[
M_j(\boldsymbol\lambda)=\int x^j\,d\nu_{F,\boldsymbol\lambda}
=\sum_{r=0}^{2j}(-1)^r\binom{2j}{r}
 D(4+2r)\prod_{p\in F}
 \left(1+\frac{\lambda_p}{p^{4+2r}+1}\right).
\tag{1}
\]

Depth-\(k\) moments are \(M_{k+j}\). With \(v=\pi^{-2}\), the even-zeta formula makes every \(D(4+2r)\) a rational multiple of \(v^{r+2}\). Thus the moments belong to
\(\mathbb Q[v,\lambda_p:p\in F]\), and monic orthogonal-polynomial coefficients belong to
\(\mathbb Q(v,\lambda_p:p\in F)\). This is an exact field statement, with no decimal recognition step.

For two primes the interaction term is explicit:

\[
M_j(\lambda_p,\lambda_q)=M_j(0,0)+\lambda_p U_{p,j}
+\lambda_q U_{q,j}+\lambda_p\lambda_q U_{pq,j},
\]

where \(U_{pq,j}=\sum_{pq\mid n}\mu(n)^2n^{-4}x_n^j>0\). More generally, with all other strengths at least \(-1\), every mixed moment derivative in a set of distinct primes is strictly positive. It is the integral over atoms divisible by those primes, with the remaining nonnegative prime factors. Infinitely many such atoms remain after any finite collection of deletions. Pure second derivatives in any one strength vanish because the moments are separately affine.

## The exact positivity domain

**Theorem 1.** For real strengths, \(\nu_{F,\boldsymbol\lambda}\) is a positive measure if and only if \(\lambda_p\ge-1\) for every \(p\in F\). On this closed orthant, every finite Hankel matrix of every nonnegative integer depth is strictly positive definite.

**Proof.** The stated inequalities make each atom weight nonnegative. The primes outside \(F\) supply infinitely many positive atoms, even when all strengths are deletion endpoints. A nonzero polynomial cannot vanish on infinitely many distinct nodes; therefore its squared norm is strictly positive. Conversely, if \(\lambda_p<-1\), the squarefree atom \(n=p\) has mass \((1+\lambda_p)p^{-4}<0\): no other strength appears at that atom. The same argument works after every depth tilt because \(x_p>0\). \(\square\)

The positive monic families \(P_m^{(k;F,\boldsymbol\lambda)}\) consequently exist at all degrees throughout the closed orthant. Their Hankel determinants never vanish there, including at simultaneous deletion endpoints. Each finite-degree coefficient is analytic in a neighborhood of every point of that orthant. This neighborhood is a finite-degree statement; the next theorem explains why no common enlargement of the positivity domain works at all degrees.

Together, Theorems 1 and 2 also prove the exact equivalence: every finite Hankel matrix is positive semidefinite if and only if every strength is at least \(-1\). Thus this is a complete positivity-domain result, not only a sufficient condition.

## An explicit polynomial detector for every bad strength

For an integer \(a\ge2\), define

\[
L_a(x)=\prod_{n=1}^{a-1}\frac{x-x_n}{x_a-x_n},\qquad
C_a=L_a(1)=\prod_{n=1}^{a-1}\frac{1-x_n}{x_a-x_n}>0,
\]
\[
r_a=\frac{1-x_{a+1}}{1-x_a}
=\frac{a^4\bigl(2(a+1)^2-1\bigr)}{(a+1)^4(2a^2-1)}\in(0,1),
\]
\[
f_{a,m}(x)=L_a(x)\left(\frac{1-x}{1-x_a}\right)^m,
\qquad m=0,1,2,\ldots.
\tag{2}
\]

The degree is \(a-1+m\); all lower nodes are killed exactly; \(f_{a,m}(x_a)=1\). At every higher node,
\(|f_{a,m}(x_n)|\le C_a r_a^m\), because each factor of \(L_a\) increases on \([x_a,1]\) and \(1-x_n\le1-x_{a+1}\).

Set
\(C_F=\prod_{q\in F}\max(1,|1+\lambda_q|)\).
Then \(|\kappa_F(n)|\le C_F\), and the elementary decreasing-series bound gives

\[
\sum_{n>a}|\mu(n)^2n^{-4}\kappa_F(n)|
\le\frac{C_F}{3a^3}.
\tag{3}
\]

**Theorem 2.** If \(\lambda_p<-1\), then

\[
\int f_{p,m}(x)^2\,d\nu_{F,\boldsymbol\lambda}(x)
\le\frac{1+\lambda_p}{p^4}
+\frac{C_F C_p^2}{3p^3}r_p^{2m}.
\tag{4}
\]

Hence the Hankel matrix of order \(p+m\) is not positive semidefinite whenever

\[
\boxed{\frac{p C_F C_p^2}{3}r_p^{2m}<-(1+\lambda_p).}
\tag{5}
\]

All quantities in (5) are rational when the strengths are rational. It provides an exact finite certificate without calculating Hankel eigenvalues or relying on floating-point root finding. A suitable finite \(m\) exists because \(r_p<1\).

**Proof.** The polynomial kills all atoms below \(p\), equals 1 at the negative atom \(p\), and has the stated uniform bound above \(p\). Replacing all higher signed contributions by their absolute values and applying (3) proves (4). The coefficients of \(f_{p,m}\) then supply a negative quadratic form for \([M_{i+j}]_{i,j<p+m}\) when (5) holds. \(\square\)

For depth \(k\), the same polynomial satisfies

\[
\int x^k f_{p,m}(x)^2\,d\nu
\le\frac{(1+\lambda_p)x_p^k}{p^4}
+\frac{C_F C_p^2}{3p^3}r_p^{2m}.
\]

Replace the right side of (5) by \(-(1+\lambda_p)x_p^k\) to obtain an explicit depth-\(k\) detector. This proof extends to any finite signed atomic measure with these nodes and the same summable weight envelope. Its mechanism is an isolating polynomial followed by exponential suppression of the higher nodes.

## Conditional prime fibers and all-prime margin bounds

Fix \(p\in F\), with all other strengths at least \(-1\), and write
\(\kappa(n)=\prod_{q\in F\setminus\{p\}}(1+\lambda_q\mathbf1_{q\mid n})\).
Separate the positive measure into its \(p\)-free and \(p\)-divisible parts:

\[
A_m=[\sum_{p\nmid n}\mu(n)^2n^{-4}\kappa(n)x_n^{i+j}]_{i,j<m},
\quad
B_m=[\sum_{p\mid n}\mu(n)^2n^{-4}\kappa(n)x_n^{i+j}]_{i,j<m}.
\]

Both matrices are positive definite. For \(A_m\), use infinitely many primes outside \(F\); for \(B_m\), use infinitely many squarefree integers \(p\ell\), with primes \(\ell\) outside \(F\). This remains true at every deletion endpoint of the other strengths.

**Theorem 3.** The one-variable fiber

\[
\tau_m(\lambda_p)=\det\bigl(A_m+(1+\lambda_p)B_m\bigr)
\]

has exact degree \(m\), and all its roots, with multiplicity, are real and strictly less than \(-1\). The root nearest the positivity boundary is \(-1-\delta_m\), with

\[
\delta_m=\min_{0\ne f\in\mathbb R[x],\ \deg f<m}
\frac{\int f^2\,d\nu_{p\text{-free}}}{\int f^2\,d\nu_{p\text{-divisible}}}>0.
\tag{6}
\]

The sequence \(\delta_m\) is nonincreasing, and, with
\(C_\kappa=\prod_{q\ne p}\max(1,1+\lambda_q)\),

\[
\boxed{\delta_{p+m}\le\frac{p C_\kappa C_p^2}{3}r_p^{2m}.}
\tag{7}
\]

**Proof.** The definite pencil is congruent to
\(I+(1+\lambda_p)A_m^{-1/2}B_mA_m^{-1/2}\), whose eigenvalues have positive slopes. Its roots are \(-1-1/\eta_i\), with \(\eta_i>0\). This proves the degree and root statements, and the reciprocal largest eigenvalue is exactly (6). Polynomial-space inclusion proves monotonicity. Test (6) at order \(p+m\) with (2). The denominator includes the atom \(p\), of mass \(p^{-4}\), because \(\kappa(p)=1\). The numerator kills every lower atom, has no atom at \(p\), and its higher tail is bounded by \(C_\kappa C_p^2r_p^{2m}/(3p^3)\). This proves (7) and therefore \(\delta_m\to0\). \(\square\)

A sharper arithmetic bound uses the exact remaining tail mass

\[
A_{\rm tail}=D(4)\frac{p^4}{p^4+1}
\prod_{q\ne p}\left(1+\frac{\lambda_q}{q^4+1}\right)
-\sum_{1\le n<p}\mu(n)^2n^{-4}\kappa(n)>0,
\]

and replaces (7) by
\(\delta_{p+m}\le p^4 C_p^2 A_{\rm tail}r_p^{2m}\).
Every finite-degree coefficient can have poles only at the fiber's Hankel roots; numerator cancellations can remove a possible pole. The theorem does not assert simple roots or global multivariate real stability.

At depth zero, the initial margin is exactly \(\delta_1=p^4\), independently of all other safe strengths: the total \(p\)-free and \(p\)-divisible masses have ratio \(p^4\), since all the other Euler factors cancel. The higher-order margins contain the arithmetic overlap information.

The same argument applies to every nonnegative depth, replacing each integral by its \(x^k\) tilt. The denominator's explicit atom contribution becomes \(p^{-4}x_p^k\), and (7) acquires the factor \(x_p^{-k}\).

## Resolution, nonconvex finite tests, and a different additive family

For \(F=\{2,3\}\), the order-one Hankel matrix is the scalar

\[
M_0(\lambda_2,\lambda_3)=105\pi^{-4}
\left(1+\frac{\lambda_2}{17}\right)
\left(1+\frac{\lambda_3}{82}\right).
\]

Thus \((0,0)\) and \((-34,-164)\) have the same positive order-one Hankel matrix. Their midpoint \((-17,-82)\) has zero total mass. The unrestricted real parameter set passing the order-one positive-definiteness test is therefore nonconvex. This is a concrete warning about a finite test, while the true positivity domain in Theorem 1 is a convex closed orthant.

The positive-semidefinite feasible set is nonconvex as well: the points \((0,0)\) and \((-34,-246)\) have positive mass factors 1 and 2, while their convex combination with weights \(3/5\) and \(2/5\), namely \((-68/5,-492/5)\), has mass factor \(-1/25\).

An additive prime family is a different deformation:

\[
\widetilde\nu_{F,\boldsymbol\gamma}
=\sum_{n\ge1}\mu(n)^2n^{-4}
\left(1+\sum_{p\in F}\gamma_p\mathbf1_{p\mid n}\right)\delta_{x_n}.
\]

Its exact positivity domain is the polyhedron

\[
1+\sum_{p\in S}\gamma_p\ge0\quad(S\subseteq F),
\quad\text{equivalently}\quad
1+\sum_{\gamma_p<0}\gamma_p\ge0.
\]

Necessity uses the squarefree integer \(n=\prod_{p\in S}p\); sufficiency checks every atom's prime subset. Its finite Hankel matrices are affine functions of the strengths, so their positive-semidefinite feasible sets are convex spectrahedra. In contrast, the multiplicative family includes the arithmetic prime-overlap terms and has polynomial parameter dependence. For example, additive strengths \(\gamma_2=\gamma_3=-3/4\) leave both individual prime weights positive but make the \(n=6\) weight negative; multiplicative strengths \(\lambda_2=\lambda_3=-3/4\) remain safely positive.

## A limited nonreduction statement

If at least two strengths in a positive multiplicative family are nonzero, its entire depth-zero monic polynomial sequence cannot equal any one-prime sequence on the same variable and node system. A direct proof avoids importing a determinacy theorem. Write \(P_m=x^m+\sum_{j<m}c_{mj}x^j\). The equations \(\int P_m\,d\nu=0\) recursively determine every normalized moment from the monic sequence. Equal sequences therefore give equal normalized Stieltjes series for \(|z|>1\). Analytic continuation on the connected complement of the common closed node set makes their Stieltjes functions equal, and residues at each isolated node give equal normalized atom weights. The mass 1 at zero fixes the normalization constant. Finally, the atom at each prime \(p\) reads off \(1+\lambda_p\), whereas a one-prime deformation changes at most one such atom. This is a precise separator from the existing one-prime family, not a global novelty certificate. It does not address arbitrary affine variable changes.

The multi-prime Stieltjes kernel also retains infinitely many isolated poles at primes outside \(F\), so the preceding one-prime proof of non-D-finiteness applies unchanged. Orthogonal-polynomial existence, definite-pencil spectral theory, and compact moment determinacy are classical mechanisms. The specific arithmetic coordinates, parameter geometry, and explicit finite-resolution detector are the objects developed here.

## Worked arithmetic examples

For \(F=\{2,3\}\), the following coefficients are rounded high-precision evaluations of (1) and the Hankel formulas. They are not exact decimal constants.

| \((\lambda_2,\lambda_3)\) | \(P_1(x)\) | \(P_2(x)\) |
|---|---|---|
| \((-1,-1)\) | \(x-0.00200014863265043361\) | \(x^2-0.933902261393426053x+0.000000921271332319859170\) |
| \((-1/2,1)\) | \(x-0.0377167661732468061\) | \(x^2-0.725293001442481628x+0.000932648146085806112\) |
| \((1,1)\) | \(x-0.0822907496962840844\) | \(x^2-0.655873200757636623x+0.00211153000026086129\) |

Simultaneously deleting \(2,3,5\) gives
\(P_1(x)=x-0.000528721422047782375\) and
\(P_2(x)=x^2-0.966491641778821472x+0.0000000795531413796910514\),
again rounded. This removes the low prime shelves while retaining the fixed mass at zero and an infinite tail.

For the variable strength at \(p=2\), the nearest conditional margins are:

| Hankel order | Other strength \(\lambda_3=-1\) | Other strength \(\lambda_3=3\) |
|---|---:|---:|
| 1 | \(16\), exact | \(16\), exact |
| 2 | \(0.0939109919936561\) | \(1.43829172807931\) |
| 3 | \(0.000302450514004102\) | \(0.0346655628067259\) |
| 4 | \(0.000000528145808944195\) | \(0.000223749375519984\) |

The noninteger entries are approximate symmetric-pencil calculations. They show an actual prime-overlap effect beyond the mass test. In these calculations the defect \(\lambda_2=-1.001\) is visible at order 3 when the 3-shelf is deleted, but only at order 4 when that shelf is strengthened to 3. This comparison is a numerical example, not a universal monotonicity theorem.

The separate rational certificates (5) do not depend on those approximate roots. The script constructs negative detectors for primes \(2,3,5,7\), at Hankel orders \(8,11,19,40\), respectively. These sufficient orders are not asserted to be minimal. In the \(p=7\) example, the other strengths are \(\lambda_2=1/2,\lambda_3=-1,\lambda_5=2\), and \(\lambda_7=-1.0001\); the exact rational upper bound on the detector norm is approximately \(-9.74271\times10^{-9}\).

## Computation contract

`checks/multi_prime_sieve.py` uses exact rational arithmetic for Euler-factor versus subset-expansion comparisons, Bernoulli-based even-zeta coordinates, isolating-polynomial values, and the rational detection criterion (5). It separately evaluates the infinite moments at high precision, tests positive orthogonality grids, compares them with a direct finite squarefree sum plus a proved tail envelope, calculates conditional definite-pencil roots, and evaluates signed detector norms. These decimal checks are not interval certificates. Universal positivity and negativity conclusions follow from the displayed proofs and exact rational bounds.

The passing run records 1,019 exact rational assertions, 102 positive parameter/depth cases, 1,395 lower-monomial orthogonality conditions, 381 recurrence identities, 40 conditional-pencil cases, and four exact negative-atom certificates. Working precision is 320 decimal digits. Maximum absolute orthogonality residual was approximately \(6.33\times10^{-322}\), maximum recurrence residual \(2.23\times10^{-303}\), and maximum scale-normalized pencil determinant residual \(5.06\times10^{-321}\). These are finite numerical consistency results, not interval certificates. No execution failure occurred in this route's run.

The script records actual versions, source hash, parameter bounds, finite counts, precision, residuals, examples, and any failed criteria in `evidence/multi_prime_sieve_checks.json`. It accepts an optional output path so a parent bounded runner can place the result inside a fresh evidence directory. No broad priority search was performed for this specific extension; historical novelty remains unresolved.
