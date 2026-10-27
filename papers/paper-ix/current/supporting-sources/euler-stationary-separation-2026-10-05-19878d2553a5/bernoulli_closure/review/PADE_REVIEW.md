# Independent audit of the Bernoulli Padé separation route

Reviewer: arithmetic_structure, 2026-10-05. The final mathematical notes have
been read; final execution provenance pins are recorded below. No author files
were edited by this reviewer.

## Normalized claim and verdict

Let T be an ordinary nonnegative integer for which
r=(17659+2^18 T)2^640-161 has true terminal161, and put m=r+161.
The coefficient domain is Q embedded in Q_2, with B_1=-1/2. On the inherited
chart x=10202+2^15 Z, K_r=2^-178 G_r has a unique critical point c in Z_2.
The reviewed route constructs rational approximants to the actual Bernoulli
kernel and then compares their *source-transformed* stationary values.

**Primary verdict: conditional on the named inherited packet-normalization
and quadratic-chart inputs.** The new coefficient, Hankel, convergence,
error, and center-motion arguments pass independent reconstruction under
those inputs. The finite strict-transfer certificates pass at exactly the
two stated indices. They do not prove universal critical nonvanishing.
This review does not re-audit the ancestor proof establishing the actual
chart for every admitted T; the current checker reconstructs and checks the
chart at its two fixed inputs.

The all-rank algebraic part must distinguish two ranges. With
h_q=a_(m+q)/a_m, the d-by-d Hankel matrix is nonsingular with determinant
valuation d-1, and its [d-1/d] Padé denominator is integral with last
coefficient valuation1, for 1<=d<=2^639. The first omitted coefficient has
valuation1 for 1<=d<2^639. Its proof uses h_(2d), so the endpoint is strict.
Indeed at d=2^639, write m=B2^640. Since B=3 mod8, addition of1 removes
two trailing binary ones, and v2(h_(2^640))=s2(B+1)-s2(B)=-1. The model
coefficient is integral, so the first error there has valuation-1, not1.
The explicit source error and center-motion table is the separate small-rank
claim, 1<=d<=10; its closest-factor calculation must not be extrapolated
to the full Hankel rank range.

## Dependency graph and obligations

1. Actual Bernoulli valuation and the ordinary carry reset give
   v2(h_q)=s2(q) for 1<=q<2^640.
2. Two binary Hankel determinant identities give the actual Hankel valuation,
   integral Padé denominator, and the first omitted coefficient.
3. Integral model moments plus the factor8^q give a convergent source model;
   true-terminal integrality controls the remote actual tail.
4. Exact local falling-factor geometry gives the source error and its
   derivative, including the contribution from moving the stationary point.
5. Unequal model-critical and exact-error valuations transfer nonvanishing
   at a specified input. The two tested cases use model valuation below error.

| Obligation | Status | Decisive reconstruction |
|---|---|---|
| Continued-fraction coefficient match and first error | Passed | Factorial Padé identity and its first coefficient have the stated sign and odd denominator. |
| Simple denominator roots | Passed with scope clarification | D_N has simple roots; g_N has simple poles there, whereas f_N=g_N-2w g_N' has double poles. |
| Height versus error | Passed | Adjacent-continuant coprimality survives at w=2^(2a); the denominator grows faster than the certified linear precision. |
| Shifted rank1 divergence | Passed | At x=-22566 and q=2^k, k>=15, the binomial factor is odd and every selected packet has valuation-25. |
| Shifted rank2 convergence and discrepancy | Passed | The denominator coefficients have valuation1; the stated recurrence bound gives convergence and the three leading packets sum to2^10 modulo2^11. |
| Actual carry-reset Hankel range | Passed | The maximum moment used is below2^640 in the stated ranges. |
| Padé denominator integrality | Passed | Dividing all nonfirst Hankel rows by2 leaves an invertible integral matrix; the right-hand side is even. |
| First omitted moment | Passed | The Schur-complement quotient H_(d+1)/H_d has valuation1. |
| Infinite source convergence | Passed | Model coefficients are integral; gamma contributes8^t. Remote actual packets use true-terminal integrality and local falling-factor content. |
| Error derivative | Passed with explicit local/global distinction | Near-tail x derivatives gain15 bits after localization; remote tails have a much stronger local bound than mere divisibility by8. |
| Critical-center motion | Passed | The half-derivative is an isometry; its perturbation has valuation E_d+7. |
| Strict finite separation | Passed | Rank3/T0: 0<7. Rank6/T718787533: 30<31. |
| Uniform nonvanishing in T | Not established | No argument guarantees that some model has critical valuation below its certified error for every T. |

## Independent all-rank Hankel reconstruction

The exact coefficient valuation is

    v2(a_n)=s2(n)-1.

Because m is divisible by2^640 and q<2^640, addition has no carry into m;
therefore v2(h_q)=s2(q). In particular h_0=1, every positive-index h_q is
even, and h_q/2 reduces to1 precisely when q is a power of2.

Put b_j=1 when j+1 is a power of2 and0 otherwise, and define over F_2

    B_n=det[b_(i+j)]_(0<=i,j<n),
    C_n=det[b_(i+j+1)]_(0<=i,j<n).

The identities b_(2j)=delta_(j0) and b_(2j+1)=b_j give, by grouping even
and odd rows and columns,

    B_(2k)=B_k^2,       B_(2k+1)=C_k^2,
    C_(2k)=B_k C_k,     C_(2k+1)=B_(k+1) C_k.

For the odd B matrix, its even-even block has only the top-left entry1;
expanding there leaves two transposed shifted Hankel blocks. This verifies
the otherwise delicate index shift. The base cases B_0=C_0=B_1=C_1=1
therefore prove that both determinant families are1 at every size.

Divide rows1,...,d-1 of H_d=[h_(i+j)] by2. Its reduction has first row
(1,0,...,0); the remaining principal block has determinant C_(d-1)=1.
Thus v2(det H_d)=d-1. This row factorization also gives
H_d^-1 in (1/2)M_d(Z_2). The Padé right-hand side consists of even moments,
so every denominator coefficient is integral. The last coefficient is,
up to sign, det[h_(i+j+1)]/det H_d. Dividing every row of its numerator by2
leaves B_d, so its valuation is exactly d-(d-1)=1.

Finally the first unmatched moment is, up to sign convention, the Schur
complement det H_(d+1)/det H_d. Its valuation is1 when2d<2^640. These
arguments use actual coefficients; no asymptotic replacement of h_q is made.

## Error, derivative, and moving center

For the small ranks set q_0=161+2d. The first coefficient error in the reset
moment sequence has valuation1. All later errors before the next carry
remain even: both the actual moments and the model moment coefficients
are even away from index0. After removing the first erroneous packet, the
remaining near tail is divisible by8 as a restricted x-series.

On x=10202+2^15 Z, the unique closest integer factor of P_(q_0)(x) is x-90,
with valuation7. For d<=10 all other integer factors have smaller valuations.
Consequently

    v2(P_(q_0)(x))=7+v2(90!)+v2((70+2d)!)
                       =93+v2((70+2d)!),
    E_d=6d+v2((70+2d)!)-84.

The resulting table is

    d:    1,  2, 3,  4,  5,  6,  7,  8,  9, 10
    E_d: -8, -1, 7, 14, 24, 31, 39, 46, 55, 62.

The remote tail must be handled locally. A quotient of falling products with
s additional factors has local Gauss valuation at least floor(s/2), because
the affine chart has even x. This statement is not a global Gauss estimate
in the variable x. After the fixed first-coefficient loss6d+1, remote terms
at t>=2^640 still have valuation far above18. Their Z derivatives preserve
this large bound. Near-tail x derivatives acquire the factor2^15; thus the
logarithmic derivative of the removed tail unit cannot compete with the
unique contribution2^15/(x-90), whose valuation is8. It follows that

    v2(error(Z))=E_d,
    v2(error'(Z))=E_d+8

at every Z in the chart, with the corresponding coefficientwise bounds.
A statement only of the form tail-unit in1+8 Z_2<Z> would be insufficient
for the derivative claim; the stronger split above is essential.

For d>=2 the perturbed half-derivative remains an isometry. If c_d is its
zero, evaluating it at the actual c gives

    v2(c_d-c)=E_d+7.

The quadratic stationary-distance law makes the value change from moving
c to c_d have valuation2E_d+14, strictly greater than E_d. Hence

    v2(Phi_(r,d)-Phi_r)=E_d,  2<=d<=10.

This is a uniform comparison in admitted T. It is not a uniform bound on
Phi_r or on Phi_(r,d). Rank3 is valid despite E_3=7 being below the older
Section3 sufficient bound L>=9: it uses this carry-specific derivative
improvement, not that older generic estimate.

## Finite computation and precision

The author checker reconstructs actual Bernoulli moments and local
polynomials at exactly T=0 and T=718787533, ranks1,...,10. A separate review
session replayed the initial version; this reviewer also replayed both final
frozen executables. The final carry records agree in every field apart from
runtime, and the final initial-Padé records agree in every field. The implemented
strict comparisons are:

| T | Rank | Model critical valuation | Error valuation | Center distance valuation |
|---|---:|---:|---:|---:|
| 0 | 3 | 0 | 7 | 14 |
| 718787533 | 6 | 30 | 31 | 38 |

In particular the second comparison has only one bit of strict margin, but
that bit is justified. Lower ranks3,4,5 at the second T have model critical
valuation equal to the error bound and do not transfer nonvanishing.

The moments use384 bits and the source computation uses256. Exact Cramer
determinants lose only d-1<=9 bits. Once numerator divisibility is known,
perturbing both determinants by2^384 changes their integral quotient by a
multiple of2^(384-(d-1)); it does not require twice the loss. Thus denominator
coefficients are correct beyond the256 bits used by the recurrence.

The model tail is integral and acquires at least3t bits from8^t. The actual
cutoff inequality is checked from the exact digit formula. Local degree18
and higher vanish modulo2^256 because localization multiplies degree j by
2^(15j). The source truncation uses [X^j]A in2^j Z_2 and remains valid under
integral translation and multiplication by the normalized local polynomial.

After division by2^178, K is known to78 bits. Its half-derivative determines
the critical center to77 bits. Stationarity makes the center-substitution
error at least154 normalized bits, so the displayed valuations through62
are exact, not precision lower bounds. The largest displayed center
difference69 is also resolved below the77-bit center precision.

For an orthogonal finite check, `check_pade_review.py` constructs the reset
moments directly from

    [sum_(q>=0) 4^q w^q/(2q+1)!]^-1,

without a Bernoulli routine, and uses Fraction Gaussian elimination rather
than Bareiss/Cramer. It verifies Hankel valuations through rank11,
denominator coefficient valuations and first errors through rank10, and
both binary Hankel recursions through dimension128. It also explicitly
asserts the two strict-transfer inequalities against the saved source
records. The universal parity proof above does not depend on this finite
check.

## Remaining gap and strongest safe conclusion

The route now supplies convergent actual-coefficient rational models and a
proved stationary-value error budget. For a rank with the proved *exact*
critical-error law, its remaining implication is:
for every admitted ordinary T, some usable rank must satisfy

    v2(Phi_(r,d)) != exact error valuation.

If the model valuation is below the error, the actual valuation equals the
model's. If it is above the error, the actual valuation equals the error.
For a merely one-sided error bound, only the first implication is available.
The nonsingular moment matrix does not establish the required inequality.
Nor do simple kernel poles, source convergence, or a nonzero finite-rank
critical value suffice without comparison with the error. The two fixed
indices pass; a finite scan cannot establish the quantified statement.
No new multiplier digits or Lean compilation were used.

There is an existing actual limitation to the displayed rank window. The
separate frozen certificate
`bernoulli_closure/recurrence/frozen_run/results.json` gives valuation91 at
T=22831001499602523078606181325. Since every E_d for2<=d<=10 is at most62,
the proved exact-error law forces v2(Phi_(r,d))=E_d at every one of those
ranks. Rank1 has no stationary point. Thus none of these ten models supplies
a non-equality certificate at that already fixed input. This is a deduction
from the uniform theorem and the earlier actual certificate, not an additional
Padé computation or a newly searched multiplier.

## Frozen provenance and corrections

`PADE_REVIEW_PINS.json` records all reviewed proof, code, data, result, and
manifest SHA256 values, together with the two exact replay commands and
comparison results. The principal source pins are:

- `separation/STRUCTURED_BERNOULLI_PADE.md`:
  `6f24391cf311dc3ba291dd0050f3ed4fc5ffe5c9c20ead395857dcb320f57394`.
- `separation/carry_adapted/CARRY_ADAPTED_SEPARATION.md`:
  `d18c3b64b54ea55c3139e1b9ee39c23bfcd6bbaea1827c5d69ea2224bb404e6e`.
- `separation/carry_adapted/check_carry_adapted.py`:
  `9cbc368f0f0833d705d43eeba1f4eff8298286e5db75b58a56ccd7f07986195d`.

Both author manifests were independently validated against their own source
roots: `separation/certified_run_final/manifest.json` and
`separation/carry_adapted/certified_run/manifest.json`. The older
`separation/certified_run` is superseded after the source corrections.

The independent reciprocal-sinh and Gaussian run is recorded in
`review/pade_orthogonal_run/manifest.json`, SHA256
`86d6c92c6433c37ccea2354be96b109dfe9e7bacc1d5f6042d64a87330f99ce6`.
It was validated against the workspace root. Its preserved source-results
snapshot agrees with every original scientific field of the final author run;
the final run adds one moment, next-Hankel/first-error checks, derivative-error
assertions, and the two named strict-transfer assertions. The independent
checker uses no author Bernoulli or determinant implementation.

During review, the author clarified that the simple poles belong to g_N,
not f_N, and retained the nonzero constant factor in the factorization of D_N.
The carry note now explicitly states the coefficientwise derivative bound
needed for the isometry argument and the sharp first-error endpoint. A review
draft's phrase "model recurrence coefficients are even" was corrected to
"model moment coefficients are even": denominator coefficients may be units.
The final proof and final replays have no unresolved discrepancy within the
stated scope. The universal nonvanishing implication remains open.
