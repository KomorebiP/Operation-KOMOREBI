# SF-LEAN-B08 target contract

Base: `13e65505a1ce2de3ece418b22b93b38811573207` (SF-LEAN-B07).
Source: the positivity and final-unit-interval comparisons in Theorem F.2,
`monograph/sections_v11/coupled_growth_full.tex`.

For labeled real scales 0<q,r,a,b<1, identify the canonical complex pair on
the real axis with actual convergent real series. Establish nonnegativity
and U_real(R),V_real(R)>=R for R>=0, the real derivative equations, and
monotonicity on the nonnegative axis. Prove the maximum-modulus identities
on each nonnegative radius. Then prove the lower product recurrences
U_real(R)>=U_real(q(R-1))V_real(r(R-1)) and the second row for R>=1,
their logarithmic form for R>1, and that all child radii are >=2 when
R>=B=1+2/min(q,r,a,b). These are prerequisites for the explicit lower
type bound, not a proof of all of F.2.

Primary route: map the actual complex HasSum representations to real series,
restrict the complex derivatives to the real axis, and use a mean-value
derivative comparison on the final unit interval. First discriminators:
HasSum real-part/ofReal transport and HasDerivAt.real_of_complex.
Alternative: the interval-integral/FTC argument (first uncertainty: the
ordered integral comparison interface). Another alternative: compare the
ordinary positive coefficients by a binomial bound on the unit shift
(first uncertainty: the exact all-degree power inequality and derivative
series transport). Keep these alternatives available if the primary stalls.

Boundary controls distinguish nonnegative real radii, real values versus
complex norms, R>=1 for the unit shift, and R>=B for child radii >=2.
No numerical approximation or graph certifies the universal inequalities.
Update actual source files, hashed input/output records, status, catalogue
and continuation guidance; preserve earlier blocks and manuscript files.
