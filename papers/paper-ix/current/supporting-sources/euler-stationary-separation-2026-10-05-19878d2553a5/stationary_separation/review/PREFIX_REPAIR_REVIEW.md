# Independent review of finite prefix repair

**Verdict: proved as written.** For each fixed admitted ordinary r and m>=1,
the repair restores the first N=2m actual moments, retains the all-q h_m
error and unit property, and has constant-recurrence rank at most mk+N.
Its complete-source correction and the stated cleared differential-order
bound are valid. It supplies no stationary-discriminant bound.

Reviewed proof: `stationary_separation/root/PREFIX_REPAIR_AND_HEIGHT_SCOPE.md`.
SHA256: `4ebbd56352acd0794aea9f3b5fdc5b5c55045a66a3eb50ae91db1409f6731e12`.
Reviewer: `/root/cross_cartier_review`. Read-only mathematical review;
no checker replay, new numerical range, model-rank search, or Lean run.

- **Moment and error scope:** The repaired prefix uses exact rational actual
  moments, which are units. Outside that prefix the previous model moments
  remain units. Errors are zero for q<N and retain valuation at least h_m
  for q>=N. The equality at q=0 makes its correction vanish.
- **Recurrence rank:** The old moment sequence has rank at most mk. Any
  sequence supported at indices 0,...,N-1 has an N-dimensional nilpotent
  shift realization. Their direct sum gives the stated bound, without
  pretending the new zero eigenvalue fits the nonzero-mode dictionary.
- **Complete source and degrees:** For 1<=q<N, exact source cancellation
  leaves P_(q-1)(x)(9^(x-q+1)-1)/8. Since P_(q-1) has degree 2q-2, the
  correction has degree at most 2N-4 at each of bases 1 and 9. Multiplying
  by D_r, of degree 2r+2, gives degree at most 2r+2N-2. The two fixed-base
  annihilator contributions therefore total 4r+4N-2. Adding the existing
  safe Jordan contribution 8mk proves the claimed order bound, including
  possible coincident bases.
- **Actual function and stationarity:** The unchanged integral packet
  factors transfer all-q error with precisely the old normalization loss
  178. For L=h_m-178>=9, the inherited actual quadratic chart persists.
  Half differentiation loses one bit, giving center error at least L-1;
  stationarity makes its contribution to value error at least 2L-2, hence
  the full stationary-value error is at least L.
- **Height conclusion:** N>=2 ensures packet 1 is replaced by the fixed
  exact a_1. Thus the previously proved growth of the particular e_1^[k]
  representation cannot obstruct every finite actual model. No bound on
  the repair coefficients, the other moments, or the final discriminant
  follows. The note correctly retains these limitations.

The repaired *cleared* expression is a finite exponential polynomial. The
unchanged caveat about zeros of D_r still applies to any contact argument;
the review does not infer global contact equivalence after clearing.
The smallest missing implication remains a strict model critical-value
valuation below h_m-178, or another arithmetic nonvanishing certificate.

Conservative proofreading found no correction needed. This review makes
no new theorem claim beyond the stated repair and its exact scope.
