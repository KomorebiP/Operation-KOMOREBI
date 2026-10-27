# Komorebi Quadratic-Form Engine v1.1 verification

## Newly executed production/general tests

- general central engine: 7/7 PASS
- noncentral positive engine: 4/4 PASS
- approximate polyphase light cone: 5/5 PASS
- budget scheduler: 4/4 PASS
- spectral/tail bridge: 5/5 PASS
- residual trace/moment certificates: 5/5 PASS
- residual exact completion: 3/3 PASS

Total re-executed at this checkpoint:

\[
7+4+5+4+5+5+3 = 33
\]

**33/33 PASS.**

## Noncentral exact controls

Three isotropic families were tested:

- df=8, noncentrality=3.5, scale=0.08;
- df=20, noncentrality=15, scale=0.03;
- df=50, noncentrality=80, scale=0.01.

Tail probabilities from 1e-4 through 1e-40 were compared to SciPy's exact
noncentral-chi-square survival function.

Maximum absolute discrepancy:

9.258e-15 decades.

All tested analytic truncation certificates passed.

## Deep-tail reference convergence

The central deep-tail hardening audit remains part of v1.1.  A nominal fixed
reference grid moved materially as K increased from 4096 to 16384 and only
agreed with the stable adaptive certified answer at the 1e-8-decade scale by
K=32768.

Therefore a fixed "large" grid is not treated as authoritative without an
independent refinement check.

## Arithmetic hardening

The packet approximation error is accumulated with log-sum-exp arithmetic and
compared to the requested tolerance in log space.  This removes the known
transient exponential/sum overflow path in rejected deep-tail candidates.

## Evidence boundary

This is finite software verification plus the proved operator identities in the
manuscript.  It is not a directed-rounding proof of every float64 operation.
Signed/indefinite forms are not yet part of the minimal v1.1 production API.
