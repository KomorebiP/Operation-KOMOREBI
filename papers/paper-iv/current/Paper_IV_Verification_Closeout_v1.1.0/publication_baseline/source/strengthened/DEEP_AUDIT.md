# Deep Mathematical Audit

## 1. Audit decision

The article was not advanced to Paper V during this pass. Paper IV was expanded and reviewed again from its definitions through its final analytic consequences.

The main theorem chain survived the audit. No central theorem was removed. Several statements needed stronger hypotheses or more exact wording. Those corrections were made before the final build.

The final chain is

\[
\text{cyclic projection}
\longrightarrow
\text{finite differential basis}
\longrightarrow
\text{reciprocal powers}
\longrightarrow
\text{zero geometry}
\longrightarrow
\text{Hadamard data}
\longrightarrow
\text{zero zeta}.
\]

## 2. Corrections made during the audit

### 2.1 Root filter domain

The earlier wording allowed an arbitrary rotation invariant domain while also using one Taylor series throughout that domain. The final article works on a disk centered at the origin, with the whole plane allowed. This makes the Taylor and root filter statements global on the declared domain.

### 2.2 Complex congruential powers

A zero free condition on the reciprocal function alone did not exclude its poles. The final statement requires a simply connected region avoiding the zeros of the normalized section. On that region the reciprocal is holomorphic and nonvanishing, so one logarithm can be fixed.

### 2.3 Euler polynomial normalization

The former sentence identified the secant Appell system directly with the classical Euler polynomials. The correct relation includes a scaling and translation:

\[
E_m^{(2,0,1)}(x)
=
2^m E_m\left(\frac{x+1}{2}\right).
\]

The source and verification suite now use this exact formula.

### 2.4 Literature positioning

The earlier phrase described the zero result as sharper than the general exponential sum theory. That comparison was too broad. The final introduction says that the regular exponent polygon and conjugation symmetry permit an explicit specialization. It does not assign priority beyond the verified classical sources.

## 3. Formal algebra audit

The root filters were checked as orthogonal idempotents and as exact coefficient selectors. The cyclic product law follows from residue addition modulo \(N\).

The finite algebras

\[
\mathbb C[\xi]/(\xi^N-1)
\quad\text{and}\quad
\mathbb C[\xi]/(\xi^N+1)
\]

were checked against the transfer and signed differential systems. The signed companion matrix satisfies \(J_N^N=-I\). The final article now gives every entry of \(e^{zJ_N}\), not only its first column.

Risk level: low after symbolic verification.

## 4. Reciprocal coefficient audit

The Bell polynomial formula, denominator recurrence, logarithmic Newton recurrence, lower Hessenberg determinant, exact degree, leading coefficient, and parameter semigroup were checked independently from truncated formal series.

The first three parameter polynomials were derived both from the Bell formula and from direct expansion. The normalized sequence was checked to satisfy the ordinary binomial type law.

Risk level: low after exact symbolic verification.

## 5. Appell and theta audit

The normalized section, triangular inverse, complex order polynomiality, Appell derivative law, translation law, two parameter convolution, and differential operator form were checked by coefficient extraction.

The theta reconstruction and theta Newton recurrence were checked independently. The factors at \(u=0\) and, for even \(N\), at \(u=-1\), follow directly from the defining generating function.

Risk level: low after exact symbolic verification.

## 6. Large zero audit

This is the highest risk part of the article.

The proof was reviewed in the following order:

1. The indicator is the support function of the regular exponent polygon.
2. Away from tie directions one exponential dominates uniformly.
3. Near a tie direction two adjacent exponentials dominate.
4. A direct modulus comparison confines large zeros to a fixed strip.
5. The normalized zero equation is a small perturbation of \(1+e^{2is_Nz}=0\).
6. The inverse function estimate localizes every large zero near one model point.
7. Rouché's theorem gives exactly one zero in each small disk, counted with multiplicity.
8. Conjugation symmetry makes that unique zero real.
9. Rotation produces all remaining large zeros.
10. Differentiation gives the derivative asymptotic and sign.
11. A second expansion gives the first exponentially small displacement.

The strengthened numerical suite checks the zero strings, correction term, derivative sign, derivative magnitude, and rotational copies for \(N=3\) through \(N=10\) at high precision.

The argument is internally coherent. Independent review by a specialist in exponential polynomials remains important because this is the deepest proof in the paper.

Risk level: moderate to high until independent specialist review.

## 7. Product and trace audit

The change of variable \(w=z^N\) gives an entire function of order \(1/N\). For \(N\geq2\), this order is below one. The genus zero product therefore has no nonconstant exponential factor.

The exact zero count implies

\[
\sum_{\lambda\in\Lambda_N}|\lambda|^{-1}<\infty.
\]

This makes the diagonal zero operator trace class. Its Fredholm determinant is the reduced denominator, and the traces of its powers equal the logarithmic coefficients.

The same order argument was checked for every normalized section.

Risk level: moderate. The proof uses standard entire function and trace class determinant facts that are cited rather than reproved.

## 8. Coefficient asymptotic audit

The nearest circle theorem is stated only for positive integral reciprocal order. This ensures that the reciprocal is meromorphic and that every nearest simple zero produces a finite principal part.

After subtracting all principal parts on the first zero circle, the remainder is holomorphic up to every radius below the second zero circle. Cauchy estimates then give the error term.

The orbit reduction uses the exact identities

\[
\rho^{-Nn}=\tau^{-Nn}
\]

and

\[
-\rho D_N'(\rho)=-\tau D_N'(\tau).
\]

Risk level: moderate.

## 9. Zero zeta audit

The exact zero count gives the sharp half planes of absolute convergence. The exponentially accurate zero locations give an exponentially summable difference from a Hurwitz zeta model on every compact set of the complex \(s\) plane.

The pole and residue follow from composition with \(Ns\). The exact cases \(N=2\) and \(N=4\) were added as a separate corollary. In those cases the entire correction vanishes.

The derivative weighted zeta is entire for \(N\geq3\) because the derivative at the large zeros grows exponentially while the complex power factor has at most polynomial growth on compact sets of \(s\).

Risk level: moderate to high until the zero theorem is independently reviewed.

## 10. Scope boundary

The audit does not establish historical priority. General zero strip and asymptotic distribution theory for exponential sums is classical. The article cites Pólya, Langer, Moreno, and Levin and claims only the explicit deductions proved for this symmetric family.

The audit also does not settle the finite exceptional zeros. The paper proves eventual simplicity and eventual positivity of the reduced zeros. It does not prove that every zero has those properties.

## 11. Final audit conclusion

No unresolved theorem target remains in the manuscript. Every theorem, proposition, lemma, and corollary has a proof. All internal references and citations resolve. The formal and finite computational checks pass. The PDF passes clean build and visual inspection.

The appropriate remaining action is independent specialist review, especially of the large zero theorem and the zeta continuation that depends on it.
