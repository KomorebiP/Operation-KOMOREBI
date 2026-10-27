# Independent mathematical review

Checkpoint SF-DISCOVERY-001. Reviewed on 2026-10-08 UTC. This reviewer first derived the requested claims from their definitions, then read the completed raw proofs. An additional isolated agent received only the asymmetric/tap-bank definitions and independently derived their entire extension and growth order. Agreement between reviewers is not the proof: the decisive arguments are recorded below.

**Primary verdict: proved as written for the audited mathematical claims under their stated domains.** No failed implication was found. The one-dilation definition and its general scalar-nonlinearity construction are established in Méndez's 2024 paper; their definition must not be called new. Historical priority of the analytic results and of the asymmetric extension remains unresolved.

## Exact audit targets and revisions

All paths below are relative to `output/special_function_discovery_v0.1`.

| Raw artifact | SHA-256 at final review |
|---|---|
| `routes/nonlinear_dilation.md` | `2e9c83a7d5ecb46861b83ea1e46c231def02aec74a787344af4adc6d1593c9af` |
| `routes/asymmetric_dilation.md` | `5956a622393e36f646a15c4a1c439c1a2682c53eb52e198a1f4463e190925911` |
| `routes/complex_depth.md` | `eca782880926cd3089eb83628b8b4746a8206f0d9c048dbe892deb192a4e0cc3` |
| `routes/arithmetic_polynomials.md` | `69fa99ae14c672973565449bd0f50bae9794da1ddf1305cf33c5b857db75be78` |
| `routes/orbit_zeta.md` | `8b7bba5ec2805db7c322fc56a200cb9859beb5e412c4b16185299a665903bfe1` |

| Normalized claim | Domain and conventions | Verdict |
|---|---|---|
| Unique entire odd solution of $f_q'=1+f_q(qz)^2$, $f_q(0)=0$; order $\log2/\log(1/q)$ and finite upper type | Real $0<q<1$; $q=0$ separately gives $z$ | Proved as written |
| $f_{1/2}(z)=\sqrt2\sinh(z/\sqrt2)$ | Same normalization | Proved as written |
| Unique entire asymmetric solution; order given by $q^\rho+r^\rho=1$ | Real $0<q,r<1$ | Proved as written |
| Positive finite tap-bank order $\max_j\rho_j$, finite upper type, and off-diagonal nonrescaling against $f_s$ | Finitely many $h_j>0$, $\sum h_j=1$; contractions in $(0,1)$; comparison $0<s<1$ | Proved as written |
| Entire arithmetic depth function of order one, exact type $-2\log(1-p_*^{-\beta})$, and non-D-finiteness | Real $a>1/2$, $\beta>0$, positive integer modulus; $n=1$ absent | Proved as written |
| Orbit-zero zeta holomorphic on $\Re s>1/N$, with positive integer arguments given by $[w^k](-wd_N'/d_N)$ | Integer $N\ge2$; fixed principal powers; zeros counted with multiplicity | Proved as written with the verified Hadamard input |
| Nearest arithmetic sieve Hankel margin $\delta_m\downarrow0$ and the explicit prime-2 bound | Prime $p$, positive base weights; explicit bound for $m\ge2$ | Proved as written |
| Arithmetic sieve resolvent not D-finite | Fixed $\lambda\ge-1$, including deletion; germ based at $z=2$ | Proved as written |

## Dependency graph and obligation matrix

The dilation conclusions use coefficient uniqueness and a tangent majorant to obtain a germ, dilation of disks to obtain an entire function, coefficient positivity to identify maximum modulus on the positive axis, and two integral inequalities to identify order. The asymmetric separator additionally uses the first three coefficients and strict Jensen inequalities. These are internal proofs.

The arithmetic depth conclusions use summable positive weights, bounded frequencies with an isolated largest frequency, and infinitely many distinct support frequencies. Its non-D-finiteness proof requires no named theorem about moment generating functions.

The orbit conclusion uses its elementary exponential growth bound, the checked finite-order factorization theorem, and locally uniform differentiation of a genus-zero product. The sieve boundary uses definite matrix pencils and uniform polynomial approximation of a continuous isolated-node bump; its resolvent obstruction uses genuine isolated poles.

| Obligation | Result |
|---|---|
| Definitions, parameter domains, normalizations and endpoints | Passed; essential restrictions listed below |
| Entire existence and uniqueness | Passed for both dilation constructions and the depth function |
| Both directions of the order claims | Passed; lower arguments do not assume regular growth or positive type |
| Exact finite upper type | Passed for the one-delay and finite-bank proofs |
| Positivity and infinite support | Passed; no numerical positivity is used as a universal proof |
| Multiplicity, branch and convergence conventions | Passed for orbit zeta |
| Actual polynomial-coefficient ODE obstruction | Passed for depth function and sieve resolvent |
| Smallest exact cases and independent construction | Passed in the finite ranges recorded below |
| Hadamard hypothesis translation | Passed against the complete primary notes |
| Historical novelty and global continuation of zero zeta | Out of scope; no affirmative claim is warranted |

## Decisive analytic evidence

### One-dilation solution

For $f_q=\sum_{n\ge0}c_nz^{2n+1}$, coefficient matching gives

$$
c_0=1,\qquad (2n+1)c_n=q^{2n}\sum_{i=0}^{n-1}c_ic_{n-1-i}\quad(n\ge1).
$$

The general Taylor recurrence uniquely determines all coefficients; even coefficients vanish. Comparison with the same recurrence at $q=1$ gives the convergent tangent majorant. If the solution exists on $|z|<R$, the primitive of $1+f_q(qz)^2$ extends it to $|z|<R/q$ and satisfies the same equation there, because its values agree with the old solution at every contracted argument. Thus the bootstrap proves entire existence, rather than merely formal convergence.

Positivity gives $M(R)=f_q(R)$. Independently derived bounds are

$$
M(R)\le R(1+M(qR)^2),\qquad
M(R)\ge(1-\alpha)R M(\alpha qR)^2\quad(0<\alpha<1).
$$

The author's logarithmic upper iteration is correctly indexed and yields $\log M(R)=O(R^\rho)$ at $\rho=\log2/\log(1/q)$. The lower inequality propagates a positive seed on $R_0(\alpha q)^{-k}$; taking $\alpha\uparrow1$ supplies the matching lower order. The argument proves finite upper type, not a strictly positive type.

For $q=1/2$, direct substitution reduces the equation to $1+2\sinh^2(u/2)=\cosh u$. Both the derivative and the zero normalization match, so uniqueness proves the classical reduction at the function level.

### Asymmetric solution and finite feedback banks

Independent coefficient reconstruction gives

$$
c_1=\frac{qr}{3},\qquad c_2=\frac{q^2r^2(q^2+r^2)}{15},\qquad
c_3=\frac{q^3r^3(q^2+r^2)(q^4+r^4)}{105}+\frac{q^5r^5}{63}.
$$

The disk bootstrap uses $\max(q,r)$, and the characteristic root is unique because $q^t+r^t$ strictly decreases from $2$ to $0$. In a finite positive bank, set $\rho=\max_j\rho_j$. The raw upper proof defines $H(t)=\log M(e^t)$ and then $G(t)=H(t)+t+B$. Its choice $B\ge\max_j(a_j+b_j)+\log2$ correctly removes the additive term and gives

$$
G(t)\le\max_j\{G(t-a_j)+G(t-b_j)\}.
$$

The seed interval and induction length $\min_j(a_j,b_j)$ cover every predecessor. Since $q_j^\rho+r_j^\rho\le1$, this proves finite upper type at $\rho$. A channel attaining the maximum supplies the lower inequality. After contraction by an auxiliary $\alpha<1$, its logarithmic recurrence propagates a positive seed at the corresponding characteristic exponent; that exponent increases to $\rho$ as $\alpha\uparrow1$. Strict positivity and finiteness of the active channels are used. An averaged characteristic equation involving $h_j$ would be incorrect; the raw file correctly takes the maximum.

The off-diagonal separator also passes. Put $p=qr$, $u=q^2+r^2$. Equality with $B^{-1}f_s(Bz)$ forces $B^2s^2=p$, $2s^2=u$ and equal orders. Strict Jensen excludes $q\ne r$ unless $\rho=2$. In that exceptional case $u=1$, and the $z^7$ coefficient difference is

$$
\frac{p^3(1-4p^2)}{1260},
$$

which vanishes only at $p=1/2$, forcing $q=r$. As an additional independent algebra check, the general coefficient difference after matching $c_1,c_2$ factors as

$$
c_3(T_{q,r})-c_3(B^{-1}f_s(Bz))
=\frac{p^3(6u-5)(u^2-4p^2)}{1260}.
$$

Thus some off-diagonal points with $u=5/6$ can match the first three coefficients; the order argument is substantive and must not be replaced by a blanket coefficient-only assertion. Parameter identifiability from $p,u$, the address-weighted tree formula and the stated scaled-sinh exclusion also check.

### Arithmetic depth family

Use the raw file's positive-frequency convention $A(s)=\sum w_ne^{-\lambda_ns}$, with $\lambda_n=-2\log(1-n^{-\beta})$. Its total mass is finite, its frequencies lie in $(0,\tau]$, and the largest frequency is attained only at the least admissible prime $p_*$. Local uniform convergence, termwise differentiation and the bound

$$
|A(s)|\le M e^{\tau\max(-\Re s,0)}
$$

follow directly. Along $s=-t$, the first atom dominates with an exponentially smaller tail, proving exact type $\tau>0$ and order one.

The raw non-D-finiteness proof by successively peeling the largest remaining atom is valid: after division by its exponential, the corresponding polynomial coefficient tends to zero exponentially, hence is identically zero. Each finite peeling step leaves summable weights and a strictly smaller next frequency. Infinitely many distinct frequencies then force every polynomial in the supposed ODE to vanish.

An independent proof uses the Laplace transform

$$
\mathcal B(z)=\int_0^\infty e^{-zt}A(t)\,dt
=\sum_n\frac{w_n}{z+\lambda_n},\qquad \Re z>0.
$$

This has genuine isolated poles at every $-\lambda_n$, with nonzero residues; these poles accumulate only at $0$. A polynomial-coefficient ODE for $A$ transforms, by integration by parts, into a nonzero polynomial-coefficient inhomogeneous ODE for $\mathcal B$, with polynomial right side. Nonzeroness follows from the invertible Weyl-algebra substitutions $t\mapsto-\partial_z$, $\partial_t\mapsto z$. At any pole where the highest derivative coefficient is nonzero, its highest Laurent pole order cannot cancel with the lower derivatives or a polynomial right side. Only finitely many poles could be exceptional zeros of that coefficient, a contradiction.

The transfer laws, strict complex-kernel argument and sector asymptotic error calculation were also inspected. The latter's two error integrals have beta exponents $\gamma=(2a-1/2)/\beta$ and $\gamma+1$; $|s|/\Re s$ is bounded on the stated closed sectors. No extra RH or signed-cancellation input is hidden there.

### Orbit-zero zeta

The bound $|d_N(w)|\le e^{|w|^{1/N}}$ proves order at most $1/N<1$. The verified Hadamard theorem then gives genus zero, a constant exponential factor and the stated zero count. Since $d_N(0)=1$, the product has exactly the normalization used in the raw file. It also has infinitely many zeros: a finite product would make the nonpolynomial $d_N$ a polynomial.

For every $\sigma>1/N$, the zero count gives $\sum|w_j|^{-\sigma}<\infty$. Principal powers satisfy

$$
|e^{-s\operatorname{Log}w_j}|\le |w_j|^{-\Re s}e^{\pi|\Im s|},
$$

so convergence is locally uniform in the strict half-plane. Multiplicities are retained throughout. In fact there are no zeros on the negative real axis, since $d_N(-x)=\sum x^n/(Nn)!>0$ for $x\ge0$; the branch convention is therefore compatible with the usual principal logarithm.

Near zero, absolute convergence of $\sum|w_j|^{-1}$ justifies both logarithmic differentiation and the geometric-series interchange. This yields the stated coefficient dictionary for every integer $k\ge1$. No simple-zero assumption or global meromorphic continuation is needed. The $N=2$ and $N=4$ Hurwitz reductions and the orbit multiplicity count check.

### Sieve Hankel boundary and resolvent

For $A_m,B_m$ defined from the non-$p$ and $p$ submeasures, both are positive definite. The closest determinant root is $-1-\delta_m$, with

$$
\delta_m=\min_{\deg f<m,\,f\ne0}
\frac{\int |f|^2\,d\nu_{\mathrm{non}p}}{\int |f|^2\,d\nu_p}.
$$

Nested polynomial spaces give monotonicity. A continuous bump supported around the isolated node $x_p$ and equal to one there has zero non-$p$ norm and positive $p$ norm. Uniform polynomial approximation on $[0,1]$ therefore proves $\delta_m\to0$ for the exact infinite measure.

For $p=2$, the proposed test polynomial $x(1-x)^{m-2}$ has degree $m-1$, kills the zero atom, and exploits the gaps $x_2=9/16$, $x_3=64/81$. The displayed constants and exponent in the bound

$$
\delta_m\le\frac{4096}{81}\left(\frac{16M_0}{17}-1\right)
\left(\frac{272}{567}\right)^{2(m-2)}
$$

are correct. The infinitely many isolated resolvent poles persist even at $\lambda=-1$. A rational-coefficient ODE has only finitely many exceptional finite points; the same highest-Laurent-order argument excludes it. The route appropriately allows cancellation of determinant roots in individual polynomial coefficients.

## Independent finite checks and reproduction

Independent calculations used Python 3.12.14, SymPy 1.14.0, mpmath 1.3.0 and standard-library `fractions.Fraction`. The dependency path was supplied through `PYTHONPATH=/workspace/scratch/de82c13900d1/special_work/verification_dependencies`. No randomness was used. Exact calculations concern rational or symbolic coefficients; the one scalar matrix-pencil decimal check used 80-digit arithmetic and is not an interval certificate.

| Independent calculation | Tested range | Result |
|---|---|---|
| Truncated integral fixed-point construction $F\leftarrow z+\int F(qt)^2dt$ | Symbolic coefficients through $z^9$, five iterations | $1,q^2/3,2q^6/15,q^{10}(12q^2+5)/315,2q^{16}(12q^4+5q^2+14)/2835$ |
| Scaled-sinh benchmark | Same five coefficients at $q=1/2$; symbolic functional residual | All match $1/(2^n(2n+1)!)$; residual is exactly zero |
| Asymmetric integral fixed-point construction | Symbolic coefficients through $z^7$, four iterations | Matches the three nontrivial coefficients above and swapping invariance |
| Direct formal expansion of $-wd_N'/d_N$ | $N=2,3,4,5$; $k=1,2,3,4$ | Exact values in the table below |
| Finite arithmetic depth shift | Squarefree $2\le n\le60$, coprime to $6$; $a=1,\beta=2$; depths $-1,0,1,2$ | All four exact depth/weight shift identities pass |
| Finite arithmetic Gram determinant | Same support, points $0,1,2$ | Exact $3\times3$ determinant strictly positive |
| Prime-2 order-two pencil | Direct moment sums, scalar quadratic formula, 80 digits | Nearest root matches the author's decimal; explicit upper bound passes |

| $N$ | $\mathcal Z_N(1)$ | $\mathcal Z_N(2)$ | $\mathcal Z_N(3)$ | $\mathcal Z_N(4)$ |
|---|---|---|---|---|
| 2 | $1/2$ | $1/6$ | $1/15$ | $17/630$ |
| 3 | $1/6$ | $1/40$ | $53/13440$ | $307/492800$ |
| 4 | $1/24$ | $17/10080$ | $691/9979200$ | $929569/326918592000$ |
| 5 | $1/120$ | $5/72576$ | $997/1743565824$ | $4618777/973160803270656$ |

The $N=2,4$ rows separately agree with their Hurwitz formulas. The exact smallest sieve check is particularly useful:

$$
\tau_1^{p}(\lambda)=D(4)\left(1+\frac\lambda{p^4+1}\right),
\qquad\delta_1=p^4.
$$

Thus the prime-2 first root is exactly $-17$. Independent order-two evaluation gives

$$
\lambda_2=-1.46510834637297761595236065537251557392744845383848\ldots,
$$

while its proved upper bound is $\delta_2\le0.73427623058403925229721455363727\ldots$. Neither decimal is promoted to certified interval arithmetic.

The final author code was also reproduced without file writes, by importing each module, redirecting its stdout into memory and calling `main()`. Both exit successfully: `nonlinear_dilation` reports **1,218** exact assertions, $n\le30$, degree 61 and symbolic $n\le12$; `asymmetric_dilation` reports **1,811** exact assertions, $n\le30$, degree 61, bivariate $n\le8$, seven rational pairs and two two-channel banks. Reproduction command:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/workspace/scratch/de82c13900d1/output/special_function_discovery_v0.1/checks \
python - <<'PY'
import contextlib, importlib, io, json
for name in ['nonlinear_dilation', 'asymmetric_dilation']:
    module = importlib.import_module(name)
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        module.main()
    result = json.loads(capture.getvalue())
    print(name, {k: result[k] for k in ['status', 'exact_assertions', 'bounds']})
PY
```

The reproduced code hashes were `5c33ba1e57f3ea00173c6c9743201c5b240ed0e9b24c659582c1773dc791b509` for `checks/nonlinear_dilation.py` and `e50f6e095de2f90340fe057938165351288d4fe22253f75bcc1380fddf78533d` for `checks/asymmetric_dilation.py`. This review's bounded runs do not prove entire extension, growth order, non-D-finiteness, or historical novelty; those conclusions depend on the arguments above. No additional standalone run-manifest file was created because the review's write scope was restricted to this evidence document.

## Primary-source authentication and scope

1. M. A. Méndez, *Combinatorial differential operators in: Faà di Bruno formula, enumeration of ballot paths, enriched rooted trees and increasing rooted trees*, Australasian Journal of Combinatorics 89(3) (2024), 350–384: [official complete PDF](https://ajc.maths.uq.edu.au/pdf/89/ajc_v89_p350.pdf). Independently opened and read Theorem 2.1, printed page 354, and Example 2.4, printed page 356. The notation translation is $f_q(z)=P_\beta(z,q)$ and $c_n=p^\beta_{2n+1}/(2n+1)!$. This authenticates the exact prior definition and general scalar nonlinearity. It supplies no priority determination for the analytic growth theorem.
2. Noam Elkies, *Functions of finite order: product formula and logarithmic derivative*, Math 259 notes: [complete PDF](https://people.math.harvard.edu/~elkies/M259.02/prod.pdf). Independently read the first theorem and its proof. It includes zeros with multiplicity, genus $\lfloor\alpha\rfloor$, polynomial exponential factor of degree at most that genus, locally uniform product convergence and $O_\epsilon(R^{\alpha+\epsilon})$ zero counts. With order at most $1/N<1$ and nonzero value at zero, the project's genus-zero implication is valid.
3. NIST DLMF version 1.2.8, released 2026-09-15: [10.46.3](https://dlmf.nist.gov/10.46) verifies $d_N(w)=E_{N,1}(-w)$; [16.8.3](https://dlmf.nist.gov/16.8) and [16.21.1](https://dlmf.nist.gov/16.21) verify the polynomial differential equations behind the restricted hypergeometric/Meijer-G separator. These were independently opened in full. No global classification of special functions follows.

No copies of these primary sources were written by this reviewer. The novelty search itself was not independently repeated comprehensively. Unavailable adjacent papers and global citation chains remain outside this review.

## Essential boundaries and remaining gaps

There is no remaining gap in the audited mathematical implications. The following boundaries are essential, not optional caveats:

- The exact positive-order formulas exclude zero contractions. At $q=1$ the symmetric germ is tangent and is not entire.
- The depth family requires $a>1/2$, $\beta>0$ and a positive integer modulus. The deleted $n=1$ atom changes the depth-zero endpoint by one; it cannot be silently restored for complex depth.
- Zero powers require a fixed logarithm, multiplicities and the strict initial half-plane. Global continuation and residue-weighted sums were not established.
- Sieve positivity is for $\lambda\ge-1$; low-degree positive matrices beyond this endpoint do not certify positivity of the infinite signed measure. Numerical Hankel roots are examples, not interval-certified roots.
- The nonrescaling theorem compares the stated real positive one-delay domain only; it does not exclude every named function, nonlinear substitution or unspecified complex parameter family.

A minor notation convention remains outside the headline claims: if the Uvarov formula is intended at polynomial degree zero, specify $K_{-1}=0$, or state the formula for $m\ge1$. This does not affect the sieve-boundary or resolvent proofs.

Final self-review covered this evidence file's displayed equations, signs, ranges, notation and source locators. No substantive changes to the author proofs were made. The cheapest next research check concerns historical overlap of the asymmetric construction with multitype increasing-tree and left/right path-length generating functions; more numerical successes do not settle that question.
