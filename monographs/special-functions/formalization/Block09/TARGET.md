# SF-LEAN-B09 target contract

Base: `b672123ad852de103130420565a6c1e9645b63f5` (SF-LEAN-B08).
Source: the explicit lower comparison in Theorem F.2,
`monograph/sections_v11/coupled_growth_full.tex`.

For 0<q,r,a,b<1, use Q=maxScale, m=minScale, B=1+2/m,
C=Q/(1-Q), rho=the positive characteristic exponent, and w=its
max-normalized positive right vector. Prove c_minus=log(2)/(B+C)^rho>0
and both inequalities log(F_i(R))>=c_minus*w_i*(R+C)^rho for every R>=2,
with the actual canonical real functions and real powers. Also extract a
uniform positive lower bound on log(F_i(R))/R^rho for R>=2.
Do not identify a real liminf/type without checking its boundedness needs;
the upper bound and full asymptotic/type conclusions remain later work.

Primary route: exact shift geometry and the seed interval [2,B], followed
by simultaneous induction on the closed caps [2,B+n*d],
d=(1-Q)*B+Q>0. Every child lies in [2,R-d], so an Archimedean covering
gives the global result. First discriminator: a general real-radius
fixed-descent induction lemma, with endpoints and positivity explicit.

Alternative: a first-failure/infimum argument using continuity (uncertainty:
closed failure set and boundary handling). Another alternative: a finite
branching tree of contracted child radii and characteristic weights
(uncertainty: termination and leaf-weight bookkeeping). Revisit these if
the closed-cap route stalls; they are not assumed failed or exhausted.

Controls distinguish a strictly positive descent from zero, the shift sign,
the seed/child thresholds, and real-power monotonicity when 0<rho<1.
Tests are exact controls, not a numerical growth experiment. Update source,
claim maps, hashed I/O, catalogue and continuation files; preserve earlier
proof blocks and manuscript sources.
