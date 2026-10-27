# Complex-depth squarefree packet functions

Checkpoint: SF-DISCOVERY-001. This route extends the established Paper II arithmetic energy to a genuine complex variable. It does not rename the classical Riesz or Báez-Duarte signed sequence, and it does not establish historical priority for the resulting function.

## Definition and endpoint convention

Fix real `a > 1/2`, real `beta > 0`, and a positive integer `q`. Define

\[
 A_{a,\beta,q}(s)=\sum_{\substack{n\ge2\\(n,q)=1}}
 \frac{\mu(n)^2}{n^{2a}}\exp\!\bigl(2s\log(1-n^{-\beta})\bigr),\qquad s\in\mathbb C,
\]

where the logarithm is the real logarithm of a positive number. Write

\[
 w_n=\mu(n)^2n^{-2a},\qquad
 \lambda_n=-2\log(1-n^{-\beta})>0,
 \qquad A(s)=\sum w_n e^{-\lambda_n s}.
\]

The support consists of squarefree integers coprime to `q`. The atom at `n=1` is deliberately absent: its positive integer-depth energy is zero but it has no complex-depth logarithm. Thus `A(k)=E(k)` for every positive integer `k`, while `A(0)=E(0)-1`. This is an actual endpoint change, not an unstated convention for `0^0`.

Define, for real `v>1`,

\[
 Z_q(v)=\sum_{(n,q)=1}\mu(n)^2n^{-v}
 =\frac{\zeta(v)}{\zeta(2v)}
   \prod_{p\mid q}(1+p^{-v})^{-1}.
\]

Only `rad(q)` affects this family. Let `m` be the least prime not dividing `q`, equivalently the smallest integer in its support. Set

\[
 M=Z_q(2a)-1,\qquad \tau=-2\log(1-m^{-\beta}).
\]

## 1. Entire extension with exact growth scale

**Theorem.** The series converges locally uniformly on the whole complex plane, and

\[
 |A(s)|\le M\exp\!\bigl(\tau\max\{-\Re s,0\}\bigr).
\]

Consequently it is entire of order one and exponential type exactly `tau`. More precisely, if `ell` is the next support integer after `m`, then

\[
 A(-t)=m^{-2a}e^{\tau t}
       +O\bigl(e^{\lambda_\ell t}\bigr),\qquad t\to+\infty,
\]

with absolute error at most `(M-m^{-2a}) exp(lambda_ell t)` for every `t>=0`.

**Proof.** The frequencies lie in `(0,tau]` and the weights have finite total mass `M`. The bound gives uniform convergence on compact sets and also bounds every termwise derivative by `M tau^j exp(tau max(-Re s,0))`. Isolating the first support atom gives the displayed remainder. This lower growth bound and the global upper bound identify the exact exponential type and order. The least support integer is prime because an admissible composite would have a smaller admissible prime factor.

For `beta=2`, the types for `q=1,2,6,30` are respectively `2 log(4/3)`, `2 log(9/8)`, `2 log(25/24)`, and `2 log(49/48)`. The negative depth direction therefore sees which initial primes the modulus excludes.

## 2. A closed transfer law in depth and weight

Let `S` shift the weight parameter by `beta/2`: `(SA)_a=A_{a+beta/2}`. Then

\[
 \boxed{A_{a,\beta,q}(s+1)
 =A_{a,\beta,q}(s)-2A_{a+\beta/2,\beta,q}(s)
     +A_{a+\beta,\beta,q}(s).}
\]

In particular, `A(s+1)=(I-S)^2A(s)`. This is a relation across two parameters, not a finite order differential equation in `s` alone.

The stronger fractional transfer law is

\[
 A_{a,\beta,q}(s+t)=
 \sum_{j=0}^{\infty}(-1)^j\binom{2t}{j}
       A_{a+j\beta/2,\beta,q}(s),\qquad s,t\in\mathbb C.
\]

Both laws follow by expanding `(1-n^{-beta})^2` or its complex power. The infinite expansion is locally uniformly absolutely convergent in `(s,t)` because the largest `n^{-beta}` on the support is `m^{-beta}<1`; its binomial coefficients grow at most polynomially on compact parameter sets, while the shifted arithmetic sums decay geometrically in `j`.

Setting `s=0` gives a numerically useful exact Newton expansion:

\[
 \boxed{A_{a,\beta,q}(t)=
 \sum_{j=0}^{\infty}(-1)^j\binom{2t}{j}
       \bigl[Z_q(2a+j\beta)-1\bigr].}
\]

The subtraction of one is essential. At integer positive depth the finite stencil cancels that one automatically. At general complex depth one should use the subtracted form to preserve exponential convergence and the endpoint convention.

## 3. A strict positive complex kernel

For any distinct complex points `s_1,...,s_d`, the matrix

\[
 K_{ij}=A(s_i+\overline{s_j})
\]

is strictly positive definite. Indeed its quadratic form is a positive sum of squares of finite exponential sums in the real frequencies. If that form were zero, such an exponential sum would vanish at every support frequency. These frequencies accumulate at zero, so the identity theorem makes the exponential sum identically zero. Its first `d` derivatives at zero give an invertible Vandermonde system on the distinct points `s_i`, forcing every coefficient to vanish.

For real `s`, all alternating derivatives are strictly positive:

\[
 (-1)^j A^{(j)}(s)=\sum w_n\lambda_n^j e^{-\lambda_n s}>0,
 \qquad j=0,1,2,\ldots.
\]

The real-depth restriction is therefore completely monotone, and the complex kernel has arbitrarily large finite rank. Strict positivity is a proof from the support, not an inference from sampled eigenvalues.

## 4. A rigorous boundary against the finite hypergeometric zoo

**Theorem.** For every parameter triple in the stated domain, `s -> A_{a,beta,q}(s)` is not D-finite: it satisfies no nonzero linear differential equation with polynomial coefficients in `s`.

**Proof by peeling the support.** Suppose

\[
 \sum_{j=0}^{r}P_j(s)A^{(j)}(s)=0
\]

with polynomial `P_j`. At `s=-t`, the first support atom is dominant. On dividing by its exponential, the equation gives

\[
 Q_m(-t)=O\bigl((1+t)^D e^{-(\lambda_m-\lambda_\ell)t}\bigr),
 \qquad Q_n(s)=\sum_{j=0}^{r}P_j(s)(-\lambda_n)^j,
\]

where `D=max deg P_j` and the tail bound follows from finite mass and bounded frequencies. A polynomial which tends to zero exponentially along the negative real axis is identically zero. Thus `Q_m=0`, so the first atom makes no contribution to the supposed differential equation at any `s`. Apply the same argument to the remaining atoms, successively, to obtain `Q_n=0` at every support frequency. For any fixed `s`, the polynomial `sum_j P_j(s)(-lambda)^j` consequently has infinitely many distinct roots; it must be zero. Every `P_j` is therefore zero, a contradiction.

This rules out equality, as a function of the depth variable itself, with an ordinary finite-parameter generalized hypergeometric or Meijer G function, or any finite D-finite expression assembled through the usual D-finite closure operations. It does **not** rule out nonalgebraic changes of variable, representations by non-D-finite classical arithmetic functions, or identification with a previously named arithmetic Laplace transform. Non-D-finiteness is a structural distinction, not a historical novelty certificate. The argument applies to a broad discrete bounded-frequency class, not exclusively to this arithmetic choice.

An independent check uses derivatives at zero: `b_j=A^(j)(0)=sum w_n(-lambda_n)^j`. Their ordinary generating function is `sum w_n/(1+z lambda_n)` and has infinitely many isolated poles at `-1/lambda_n`, with no finite accumulation. Standard D-finite/P-recursive equivalences lead to the same contradiction. The elementary proof above does not require that equivalence.

## 5. Complex-sector arithmetic asymptotics

The real integer-depth power law already appears in Paper II. Here the same argument extends to complex depth uniformly in every closed sector `|arg s| <= pi/2-epsilon`. Put

\[
 \alpha=(2a-1)/\beta,\qquad
 \delta_q=\frac1{\zeta(2)}\prod_{p\mid q}\frac{p}{p+1}.
\]

Then, as `|s| -> infinity` in such a sector,

\[
 A_{a,\beta,q}(s)=\frac{\delta_q}{\beta}
 B(\alpha,2s+1)
 +O_{a,\beta,q,\epsilon}\bigl(|s|^{-(2a-1/2)/\beta}\bigr),
\]

and hence

\[
 A_{a,\beta,q}(s)\sim
 \frac{\delta_q\Gamma(\alpha)}{\beta}(2s)^{-\alpha}.
\]

The power uses the principal branch in the right half-plane. The beta term is a continuous density model, not the exact arithmetic function.

**Counting and error argument.** Squarefree inclusion and exclusion gives
`Q_q(x)=sum_(n<=x,(n,q)=1) mu(n)^2=delta_q x+O_q(sqrt(x))`.
Specifically, expand `mu(n)^2=sum_(d^2|n) mu(d)`; for `(d,q)=1`, the inner coprime count is `(phi(q)/q)x/d^2+O(2^omega(q))`. Summing the errors and bounding the omitted convergent `d^-2` tail proves the estimate and its stated density. Integrate against
`g_s(x)=x^-2a(1-x^-beta)^(2s)` for `x>=1`. Its endpoint values are zero when `Re s>0`. The density contribution is `delta_q/beta B(alpha,2s+1)` by substitution `y=x^-beta`. The counting error is bounded by `C_q integral_1^infinity sqrt(x)|g_s'(x)| dx`. Its two derivative terms are beta integrals with exponents `(2a-1/2)/beta` and `1+(2a-1/2)/beta`. On the specified sector `|s|/Re s` is bounded, giving the displayed error. Standard beta asymptotics give the leading term. No signed cancellation or RH hypothesis enters.

## 6. Mixed character extension

For Dirichlet characters `chi,psi` modulo the same actual modulus `q`, define

\[
 A_{\chi,\psi}(s)=\sum_{n\ge2}
 \mu(n)^2\chi(n)\overline{\psi(n)}n^{-2a}e^{-\lambda_n s}.
\]

The matrix kernel with entries `A_(chi,psi)(s+bar t)` is positive semidefinite on pairs `(s,chi)` by the same feature-space formula. A single off-diagonal entry can be complex or signed and is not asserted completely monotone. Its Newton coefficients are
`L(2a+j beta,eta)/L(4a+2j beta,eta^2)-1`, where `eta=chi bar(psi)`. This follows from the Euler product `prod_p(1+eta(p)p^-v)`. The diagonal reduces to the principal family above. Fixed-modulus character cancellation gives the inherited real-depth decoherence estimate; no character-uniform or GRH claim is made here.

## 7. Bounded comparison and status

Sources checked on 2026-10-08 UTC:

1. Mark W. Coffey, *On the coefficients of the Báez-Duarte criterion for the Riemann hypothesis and their extensions*, arXiv:math-ph/0608050v2, 7 September 2006, https://arxiv.org/pdf/math-ph/0608050. Formula (10) is the signed sequence `sum mu(n)n^-2(1-n^-2)^k`; formulas (19)-(20) treat parameterized binomial coefficients built from reciprocal Hurwitz-zeta values. Its signed measure differs from the positive `mu(n)^2` family and has different analytic conclusions. Nonetheless its kernel and Newton-series mechanisms are close prior machinery. Classification: partial or adjacent result only for the present entire positive family; known machinery for the transform mechanism. The PDF was read through the primary arXiv source; no local copy was created.
2. NIST DLMF, https://dlmf.nist.gov/16.8, equation 16.8.3, and https://dlmf.nist.gov/16.21, equation 16.21.1. These exhibit polynomial-coefficient differential equations for generalized hypergeometric and Meijer G functions with fixed finite parameter lists. This supports the limited non-reduction statement after the proved non-D-finiteness result.
3. Current project guide, Paper II lessons 05-12 and Paper III lesson 01. The integer-depth energy, positive measure, finite zeta stencil, real asymptotic, Gamma limit, and real character decoherence are inherited project results. They should not be advertised again as discoveries of this checkpoint.

Discovery queries used both routine and stronger web search: `Baez Duarte Riesz criterion coefficients binomial zeta k squarefree generating entire function`; `squarefree Dirichlet series complex Baez Duarte`; `D-finite exponential infinitely Dirichlet`; `DLMF Meijer G differential equation hypergeometric differential equation`. The Coffey source was checked in its primary full version. An attempted EMIS URL for the original Báez-Duarte PDF returned an internal retrieval error; the original paper was not authenticated from that URL, and no conclusion rests on it. This is a bounded comparison through these sources, not an exhaustive priority search. No apparently-new classification is claimed.

**Research judgment.** This is a substantive complex-depth arithmetic function family with a closed transfer calculus and a proven obstruction to finite hypergeometric reduction. Its base sequence and Laplace-transform architecture have established antecedents. The next meaningful novelty question is whether the particular coupled shift structure, sharp complex-depth asymptotics, and arithmetic spectral identification have already been developed together, rather than whether writing a new sum automatically invents a new special function.

## Computation contract

`checks/complex_depth.py` performs exact finite-sum checks of the depth/weight shift over integer and negative integer depths, verifies exact principal endpoint and radical invariance, and computes exact positive Gram determinants. High precision examples independently compare direct complex sums with the subtracted zeta Newton series and bound the direct omitted tail. These are implementation checks and examples. Entire continuation, sector asymptotics, strict kernel positivity in all finite dimensions, and non-D-finiteness are justified by the proofs above, not by finite computation.
