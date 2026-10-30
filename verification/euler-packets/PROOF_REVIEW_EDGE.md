# Exact tail continuation: focused self-review

EULER-CASE-007 · 29 October 2026 · same-assistant review. Verdict: **proved as
written**, using the explicitly checked restricted-series preparation theorem
as a source input. No independent review or new Lean execution.

| ID | Claim and audit | Result |
|---|---|---|
| C53 | Finite tail factorization | Passed. r is first omitted index, not retained depth. N=r+x and 0<=q<=x. Factorial cancellation gives 4^q times the falling 2x-factorial, which contributes another 2^q and exactly P_q. H_r(0)=1 retains the sharp first-row error. No analytic convergence is needed at natural rows. |
| C54 | Binary weights and finite carry minimum | Passed. v_2 beta_m=s_2(m)-1 follows by subtracting 2m+v_2((2m)!) from 4m-1. Thus coefficient ratios have exact lambda weights. The bound lambda>=3q+1-s_2(r) proves every minimizer lies inside the displayed cutoff; q=0 gives mu<=0. Representative tables were recomputed. |
| C55 | Sparse-binary all-row valuation | Passed. For s_2(r)<=3 every positive q contribution is even, since P_q and A(x-q) are integral and A(x) is a unit. H is odd, so the valuation equality follows. First omitted indices 1..14 all satisfy the hypothesis. The binomial coefficients binom(2N,2r) and binom(N,r) have equal valuations, not equal values. |
| C56 | Cancellation witness and unchanged uniform optimality | Passed. r=15,N=16 has two omitted terms of weight 63. The exact H numerator is 32 times an odd number with odd denominator, so its valuation is five, giving 59+4+5=68. At N=15 the error is kappa_15 of valuation 59, so no uniform improvement follows. |
| C57 | Finite polynomial boundary and open scope | Passed with checked source input. H uses the source's restricted extension for noninteger arguments. G has integral restricted coefficients and exact Gauss normalization. The monic preparation polynomial is not its mod-two reduction or a finite Taylor truncation. The source's preparation proof uses successive division by the monic reduction and convergent corrections. Universal root simplicity remains explicitly open and distinct from the closed uniform theorem. |

Primary run-007 covers 93 exact tail rows: r=1..8,x=0..8 and
r=15,31,63,x=0..6. It checks direct Euler reconstruction, partial sums,
factorization and valuations, including the cancellation witness. For all
r=1..255 the proved carry cutoff is compared with q=0..256. The universal
cutoff and sparse family are justified by the written inequalities, not finite
extrapolation. Cross-check-007 adds 234 pinned API comparisons: 46 partials,
46 errors, 132 omitted weights and 10 kernel values. The larger row range in
the primary run is not misreported as cross-checked in full.

An initial command preflight rejected runner-owned stdout/stderr paths in the
result list before mathematical execution. The result list was restricted to
JSON/CSV outputs. The accepted primary and cross runs then completed; no failed
mathematical run is inferred from that setup rejection.

Proofreading checked error-versus-partial-sum notation, r=L+1, full Euler degree
2N, factorial scaling, binary normalization sign, integer versus 2-adic domain,
exact valuation of zero, all displayed rational arithmetic and open boundaries.
Earlier claims retain their reviews. No unresolved obligation remains for the
new statements within their declared hypotheses.
