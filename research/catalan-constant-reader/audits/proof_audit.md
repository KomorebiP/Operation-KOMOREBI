# Catalan Series 08: critical proof audit

Audit checkpoint dated 9 October 2026. Reviewer: `catalan_audit_finish`. Primary verdict for the proposed conclusion **G is irrational**: **incomplete, with the smallest missing implication a strict uniform decay estimate for nonzero integer forms after clearing and content reduction**. The publication does not assert that this implication has been proved.

This is a critical self-review of the assembled program, not an independent referee certificate or proof assistant check. The raw historical script, the current source contracts and the recorded exact computation assertions were read. The source-dependent leaves use the separately authenticated literature record. Final manuscript coverage is recorded separately after its text is saved. No new eight million pair scan was run in this audit.

## Definitions and dependency graph

The coefficient field of the recurrence is Q. Its initial pairs are (u0,u1)=(1,7/4), (v0,v1)=(0,13/8). For n>=1, A_n=(2n+1)^2(2n+2)^2p(n), C_n=(2n-1)^2(2n)^2p(n+1), p(n)=20n^2-8n+1, and q(n) is the polynomial in the historical script. The shared equation is A_n w_(n+1)=q(n)w_n+C_nw_(n-1). Forward iteration starts at n=1, not n=0.

The root conclusion would require:

1. Exact recurrence and coefficient normalization [external LC01].
2. Exact integer packet inputs T_n=16^n u_n [external half-binomial formula LC05 plus internal integer-series argument].
3. Universal clearing for v_n [external LC05 and its explicit normalization bridge].
4. Filter identity [finite binomial theorem, corrected integral identity LC03, source filter LC06].
5. Nonvanishing on a selected infinite family [internal positivity for even m].
6. A strict decay margin after clearing and content reduction [not proved for this program].
7. The elementary rationality lattice contradiction [internal proof].

The large valuation scan, the five gcd pairs and the finite sign diagnostics support implementation claims at finite indices. They do not supply leaf 6. Neither recent preprint claim nor its criticism is a leaf proving the root conclusion.

## Claim cards and decisive evidence

### PA01. Universal Wronskian

Claim: for every integer n>=0,

W_n=u_(n+1)v_n-u_nv_(n+1)=(-1)^(n+1)p(n+1)/[2(2n+1)^2(2n+2)^2].

Verdict: **proved as written** for the defined recurrence, with no limiting or irrationality input. Substitution cancels q(n) and gives W_n=-(C_n/A_n)W_(n-1) for n>=1. The proposed closed form obeys this relation, and W0=-13/8. The denominator is nonzero and p(t)=20(t-1/5)^2+1/5>0. Thus W_n is nonzero at every allowed index. A separate symbolic simplification in this audit returned zero for the induction residual and -13/8 for the base case. The recorded Fraction run checks n=0,...,200. A nonzero Wronskian proves adjacent coefficient pairs differ. It does not by itself prove an arbitrary filtered error is nonzero.

### PA02. Positivity and exact packet integrality

Claim: u_n>0 and T_n=16^n u_n belongs to Z for every integer n>=0.

Verdict: **proved as written, using the exact external formula LC05**. Positivity follows from the initial values and positive recurrence coefficients. In particular q(n)>0 for n>=1: its n^4,n^3,n^2 terms have sum at least 1524n^4, and the remaining terms are positive. A_n and C_n are positive.

For integrality, LC05 identifies

u_n=sum_(j=0)^n binom(n,j)binom(n-1/2,j)binom(n+j-1/2,j).

For integers h,j>=0, 4^j binom(h-1/2,j) is the z^j coefficient of (1+4z)^h(1+4z)^(-1/2). Both factors have integer coefficients because the second has coefficients (-1)^j binom(2j,j). Multiplying a summand by 16^n leaves the integer factor 16^(n-j) times two such integer coefficients and binom(n,j). This includes n=j=0. The finite half-binomial audit checks all 1326 summands for 0<=n<=50. The recurrence division check through n=10000 is separate finite evidence, not the universal proof.

### PA03. Clearing the second coefficient

Claim: 8*16^n*L_(2n)^2*v_n is integral for every integer n>=0, with L_0=1.

Verdict: **externally proved in the exact required form after the LC05 notation bridge**. The stronger source statement gives 4*16^n*L_(2n)^2*v_n in Z. The formal coefficient bridge is b_n=-4v_n and does not assume linear independence of 1 and G. The zero-index claim is direct because v0=0. This is stronger than the finite check through n=500 and must not be attributed solely to the asymptotic 2002 denominator statement LC04.

### PA04. Corrected integral normalization

Claim: J_n=8(-1)^n(u_nG-v_n) for n>=0, with the exact double integral of LC03.

Verdict: **proved as written using the authenticated Whipple transform and formal coefficient identification recorded in LC03**. The internal beta expansion is valid by Tonelli. Its resulting 3F2 has excess n+1/2>0. The Whipple hypothesis also becomes n+1/2>0. The gamma prefactors cancel with no factor 2. The current written derivation therefore gives the factor 8, and the independent n=0 computation J0=8G agrees.

The printed source factor 1/4 is incompatible with the stated initial values. Its exact discrepancy and the all-index corrective derivation are preserved in `audits/integral_normalization_derivation.md`. An n=0 check alone would not prove the corrected all-index identity. The proof is source-dependent. This review checks the beta expansion, parameter hypothesis and gamma cancellation, and uses the exact external identities authenticated by the separate literature audit. It does not certify a first-principles derivation of Whipple's general transformation. No erratum is claimed.

### PA05. Filter, signs and even-family nonvanishing

Claim: for integers n,m>=0,

Jtilde_(n,m)=sum_i(-16)^i binom(m,i)J_(n+i)
=integral psi(x,y)^n(1-16psi(x,y))^m dmu,

where psi=xy(1-x)(1-y)/(1-xy) and dmu=dxdy/[sqrt(x(1-y))*(1-xy)]. Moreover Jtilde_(n,m)>0 when m is even.

Verdict: **proved as written using PA04 and the source filter dictionary LC06**. A finite binomial expansion produces the integral identity. Its measure is positive and integrable in the required weighted integral. For even m, the integrand is nonnegative. It is positive on an interior open set where 0<psi<1/16, which has positive measure. Hence the integral is strictly positive. This includes m=0 and n=0. No arbitrary odd-m sign claim follows.

The signed audit form F_(n,m)=8(-1)^n sum_i binom(m,i)16^(n+i)(u_(n+i)G-v_(n+i)) equals 16^n Jtilde_(n,m). The signs of its finite diagnostic grid may therefore be compared with even-filter positivity. The exploratory assertion sign(F)=(-1)^m is **refuted**, already at (n,m)=(1,1), where F=173056/9-20992G>0. The recorded rational interval certifies that sign. Its 138 mismatches among 860 pairs do not refute the source filter or the even-family proof.

### PA06. Maximum of the integral kernel

Claim: max_[0,1]^2 psi=phi^(-5), where phi=(1+sqrt(5))/2.

Verdict: **proved as written**, with continuous boundary extension of psi at (1,1). Fix z=sqrt(xy). Since x+y>=2sqrt(xy), psi<=z^2(1-z)/(1+z), with equality at x=y=z. The derivative of this one-variable function is -2z(z^2+z-1)/(1+z)^2. Its maximum on [0,1] is attained at z=phi^(-1) and equals phi^(-5)=(5sqrt(5)-11)/2. In particular phi^(-5)>1/16, so the filtered kernel can change sign when m is odd. The derivative and maximum were symbolically simplified in this audit. This calculation does not replace a proof of an all-index decay equality for the integrated filter.

### PA07. Pascal update and finite valuation scan

Claim: S_(n,m)=sum_i binom(m,i)T_(n+i) obeys S_(n,m+1)=S_(n,m)+S_(n+1,m) for n,m>=0. On the actual finite domain 1<=n<=2000, 0<=m<=4n, the largest observed v2 is 31 and every observed valuation is exact.

Verdicts: **proved as written** for the universal Pascal identity; **computationally verified only in the stated range** for the maximum. The pair count is sum_(n=1)^N(4n+1)=2N^2+3N=8006000. A nonzero residue modulo 2^128 determines the exact valuation below 128. A zero residue would give only a lower bound, and is tracked. No zero residues occurred. The in-place update runs in increasing n, leaving each right neighbor on the old row. The T input extends to 5N, enough for all n+m<=5N.

The smaller direct-sum run checks all 20300 pairs for n<=100. A low-precision branch test finds eight unresolved zero residues and correctly refuses exactness. The first reported large maximizer (1466,2113) is first in loop order, not asserted unique. None of these facts proves a uniform o(n+m) valuation estimate.

### PA08. Minimal clearance and gcd decomposition

Claim: if U is an integer, V=N/D in lowest terms with D>0, and D divides positive Q, then

gcd(QU,QV)=(Q/D)gcd(DU,N)=(Q/D)gcd(U,N).

Verdict: **proved as written**. Factoring Q/D from both integral entries gives the first equality. The second uses gcd(D,N)=1. A common global sign has no effect. This is an exact algebraic statement, not an asymptotic content law. The five historical rows verify the application. Their minimally cleared pair gcds are 8,4,8,64,8. The much larger cleared gcds include Q/D and cannot be interpreted as wholly intrinsic cancellation.

### PA09. Filter asymptotic input and direction of inequality

Claim: for integer m=m(n)>=0 with m/n->alpha>=0, LC07 supplies the stated coefficient growth limit and limsup |Jtilde_(n,m)|^(1/n)<=M(alpha).

Verdict: **externally proved in the exact required upper-bound form, as a versioned preprint input**. The project must retain the <= direction. Neither the maximum of the pointwise kernel nor this limsup bound implies equality for the signed integral. Rounded exponent 0.62 is below the irrationality threshold and does not prove irrationality. A positive exponent for an available cleared-error upper bound shows that the estimate fails to force decay. It does not prove the actual cleared forms diverge.

### PA10. Strict sufficient decay margin

Claim: along an infinite family with n->infinity, suppose the raw error has limsup log|F_n|/n<=-delta, the positive clearing scale has limsup log Q_n/n<=c, and the positive content satisfies liminf log d_n/n>=h. If delta+h>c, the reduced integer errors Q_nF_n/d_n tend to zero.

Verdict: **proved as written as a conditional theorem**. Choose epsilon>0 with c-delta-h+3epsilon<0. Each of the three definitions supplies its respective eventual bound. Combining them makes the reduced error at most exp((c-delta-h+3epsilon)n). This supplies only sufficiency. Equality of rates needs finer estimates, and failure of the sufficient inequality is not a proof of divergence. For the actual filtered integral with PA09, one sufficient condition is h>log(16)+4(1+alpha)+log M(alpha), under the matching LCM asymptotic input and even m. No such content lower bound is proved by five rows.

### PA11. Elementary irrationality criterion

Claim: if integer pairs (A_k,B_k) give 0<|A_kG-B_k|->0 along an infinite sequence, then G is irrational.

Verdict: **proved as written**. If G=a/b with b>0, then b(A_kG-B_k)=aA_k-bB_k is a nonzero integer and has absolute value at least 1. This contradicts vanishing. Integrality, nonvanishing and vanishing are distinct obligations. The current program proves useful parts of the first two, but not the actual unconditional third obligation.

### PA12. Strict rational brackets from the recurrence alone

Claim: r_n=v_n/u_n has a limit L, strict alternating brackets r_(2k)<L<r_(2k+1), and d_n-d_(n+1)<|L-r_n|<d_n, with sign(L-r_n)=(-1)^n and d_n=|W_n|/(u_nu_(n+1)).

Verdict: **proved as written** in the current Chapter 4. The shifted polynomial q(n)-A_n at t=n-1 has the displayed positive coefficients, checked by exact symbolic subtraction with residual zero. Thus u_(n+1)>u_n>=1. The Wronskian gives the exact alternating quotient increment. Moreover d_n/d_(n-1)=(C_n/A_n)u_(n-1)/u_(n+1)<1 directly from the positive recurrence. The explicit |W_n| bound and u_n>=1 force d_n to zero. The alternating series converges. Positive paired tails give the strict lower bound, and positive tails of the opposite parity give the strict upper bound. Identifying L with G is separately LC01, not a consequence of finite decimal agreement. The four printed initial quotients were checked from the raw recurrence.

### PA13. The LCM asymptotic and its index translation

Claim: log L_N/N tends to 1 as integer N tends to infinity. Consequently log(8L_(2(n+m))^2)/n tends to 4(1+alpha) when m/n tends to finite alpha>=0.

Verdict: **externally proved in the exact required form plus a proved elementary translation**, using LC10. The primary source supplies theta(x)/x tending to 1 and theta(x)=O(x). Prime factorization gives log L_N=sum_(a>=1)theta(N^(1/a)). At most log_2(N) terms are nonzero, and every a>=2 term is O(sqrt(N)). The total higher-power contribution is therefore O(sqrt(N)log N)=o(N). Substituting N=2(n+m) and retaining both the squared LCM and the doubled index proves the factor 4. The additive log 8 disappears after division by n. A finite plot of log L_t does not prove this theorem.

### PA14. The explicit M bound and its cleared-rate limitation

Claim: for alpha_n=m(n)/n, |Jtilde_(n,m(n))|<=8G M(alpha_n)^n. Thus its limsup nth root is at most M(alpha) when alpha_n tends to alpha. For every alpha>=0 the available unreduced cleared upper-bound exponent kappa(alpha)+log M(alpha) is positive.

Verdict: **proved as written** in current Chapter 9, using the already sourced corrected integral and kernel range. On s in [0,1/16], the maximum of s(1-16s)^alpha is at s=1/[16(1+alpha)] when alpha>0. The other branch s(16s-1)^alpha increases on [1/16,t] and has maximum t(16t-1)^alpha. At alpha=0 the maxima have the stated continuous extensions. Bounding a positive finite measure integral by its absolute integrand maximum proves the upper bound. Continuity yields the limsup statement. This is not an equality for the actual integral. The proof that the cleared upper-bound exponent is positive uses t>5/64, hence 16t>5/4 and 16t-1>1/4. The displayed rational square check establishing sqrt(5)>357/160 is valid. The result is a limitation of the available estimate, not a proof that actual errors diverge.

### PA15. Certified Euler enclosure

Claim: the rational Euler sums E_N satisfy E_N<G<E_N+2^(-N-1), with the exact positive integral remainder displayed in current Chapter 1, for every integer N>=0.

Verdict: **proved as written**. The positive-difference convention Delta a_k=a_k-a_(k+1) matches the finite sum and the integral of (1-x^2)^j(-log x). Nonnegative terms justify monotone interchange. The finite geometric identity gives the exact remainder. Since 0<G<1, its upper bound 2^(-N-1)G is strictly smaller than 2^(-N-1). The finite run at N=1000 computes one exact rational interval of width 2^(-1001); it does not prove the universal tail formula. The printed small differences, E0,E1,E2, and upper endpoint 1709/1800 are consistent.

### PA16. Pigeonhole converse and reduced denominator criterion

Claim: every irrational real alpha has a nonzero integer form with 1<=Q<=H and |Q alpha-P|<1/H at every integer H>=1. Conversely, nonzero forms tending to zero imply irrationality.

Verdict: **proved as written** in Chapter 2. Place the H+1 fractional parts in H half-open intervals. Two points in the same interval have distance strictly below 1/H, including at H=1. Taking the difference of their indices gives a positive Q after ordering the indices. Irrationality supplies nonvanishing. Positive Q cannot stay bounded while their distances to integers tend to zero, since a finite set of irrational multiples has a positive minimum distance to integers. This converse assumes irrationality and is not used to prove the target without that assumption. The reduced rational criterion follows from the exact multiplication |Q alpha-P|=Q|alpha-P/Q| with positive Q.

### PA17. Root-rate clearing criterion

Claim: rational forms are eventually nonzero, a positive integer D_j clears both coefficients, and their two nth-root limsup bounds have finite product strictly below 1. Then alpha is irrational.

Verdict: **proved as written** in Chapter 2. The clearing rate bound is at least one because D_j>=1. The strict product margin admits larger positive rates lambda',delta' whose product is still below one, also when the original error rate lambda is zero. Eventual limsup bounds then make each nonzero cleared integer form at most (lambda'delta')^j. The rationality gap gives the contradiction. The rational exponential example has product exactly one and constant cleared error -1, correctly refuting replacement of the strict inequality by a weak inequality. The logarithmic and content variants use eventual bounds and the same strict margin; their finite initial indices should be discarded before a gcd logarithm is defined.

### PA18. Transfer matrices and continuants

Claim: for every rational initial pair and integer n>=2, the recurrence solution is w_n=K_(1,n-1)w1+beta1*K_(2,n-1)w0, where each continuant has upper adjacent entries -beta_(r+1),...,-beta_s, lower adjacent entries 1, diagonal alpha_r,...,alpha_s, and the empty determinant K_(r,r-1)=1.

Verdict: **proved as written** in Chapter 3. Last-row expansion gives the plus-sign recurrence K_(r,s)=alpha_s*K_(r,s-1)+beta_s*K_(r,s-2). The n=2 boundary requires precisely the defined empty K_(2,1). Direct iteration checks n=3, after which both coefficient sequences satisfy the same recurrence. The matrix inverse [[0,1],[1/beta,-alpha/beta]] and ordered transfer product are correct for n>=1. The rational solution basis uses the invertible initial pair matrix and does not assume anything about G. The exact 60-instance check at n=2,...,13 for five rational initial families supports the implementation only. Its separately recorded, validated v2 manifest is `evidence/computation/continuant_final/manifest.json`. The universal result rests on the written induction.

## Obligation matrix

| Obligation | Status | Evidence and limit |
|---|---|---|
| Recurrence domain, initial values, signs | passed | Raw script plus LC01 |
| Wronskian base case and induction | passed | Written algebra, symbolic residual 0, separate finite n<=200 run |
| Universal T integrality | passed | Exact LC05 formula plus integer coefficient argument |
| Universal v clearing | passed through external input | LC05 notation bridge, including direct n=0 |
| All-index corrected integral factor | passed using named external identities | LC03, current derivation, independent J0 check |
| Kernel measure and maximum | passed | Correct denominator placement and one-variable maximum |
| Even m positivity | passed | Positive measure on an interior open set |
| Arbitrary odd m sign law | failed | Exact counterexample (1,1) |
| Finite modular exhaustive coverage | passed in stated range | 8006000 pairs, no unresolved residue |
| Uniform valuation/content asymptotic | not addressed by finite scans | Exact missing global input |
| Preprint rate direction | passed as upper bound | LC07 gives limsup <= M, not equality |
| Unconditional irrationality conclusion | incomplete | Strict reduced-error decay not proved |

## Cheapest next check and strongest safe statement

The next useful research step is a proved denominator or content bound in a fixed normalization, restricted to a nonzero family such as even m and sufficient to cross the strict exponent threshold. A larger scan may identify a candidate bound but cannot replace it. The strongest safe release statement is that universal recurrence and packet identities, an even-filter nonvanishing argument, authenticated source inputs and finite exact arithmetic audits have been assembled. Catalan's irrationality is not proved by this release.

## Audit provenance

The raw source, literature ledger and current computational report are pinned in `proof_audit.json`. This audit made no mathematical changes to the manuscript. Source revisions after a pin require a further review. The diagnostic `ls catalan_set/paper` exited 2 because manuscript authors had not yet saved that directory. It did not affect a scientific computation. Final source coverage and hashes will be appended when the book is frozen.

The first figure-data checkpoint assumed a row field named `gcd`, but the actual diagnostic field is `cleared_gcd`. It raised a KeyError before writing a report. Inspecting the schema and rerunning with the actual field succeeded. No data file or scientific run was changed. This failed command is recorded in both audit JSON records.

## Manuscript review finding and its resolution

Chapter 2's content-rate proposition assumes nonvanishing only eventually. Its gcd is therefore positive only for sufficiently large indices. The author was asked to discard the finite initial segment or restrict the gcd definition to sufficiently large indices before taking its logarithm. The final text explicitly discards the finite initial set and defines the gcd on the remaining sufficiently large indices. This resolves the domain issue without changing the asymptotic argument or adding a hypothesis to the final content criterion.

The appendix's compact source table now includes LC09. The book denotes clearing cost by kappa0, and its combined available bound by E=kappa0+log M. The guide explicitly defines its kappa as the combined bound. Each definition is unambiguous. The table and notation changes preserve the mathematics.

## Final source self-review

All ten numbered chapters, both appendices, opening, main file, bibliography, both shared preambles and the complete visual guide have been read. Claims, signs, ranges, finite evidence and source attribution were checked in context. No further mathematical or meaning-changing issue was found. This reviewer made no manuscript edits. The only mathematical clarification requested in the manuscript was the eventual gcd domain described above, performed by the author. Ordinary layout formatting was reviewed without changing factors. All 31 figure formulas and their data sources are pinned separately in `figure_data_review.json`.

The final source hashes and LaTeX reference/environment checks are in `evidence/proofreading/final_source_self_review.json`. Page appearance is a separate review and is not certified by this source self-review. These records apply to their exact pinned files. A later content change needs renewed review.

Final layout revisions were reviewed conservatively. TOC spacing, a diagram notation bridge, consistent LCM notation, scan-count prose and figure label sizes changed. The continuant formula and all figure formulas/data are unchanged. The superseded successful continuant run is preserved. Its caption context pin became stale, so a fresh 60-instance final run was recorded and validated against current bytes. No large scan was repeated.
