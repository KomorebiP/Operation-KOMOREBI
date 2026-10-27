# Komorebi Positive Quadratic-Form Engine v1.0 verification

## Newly executed general-engine tests

- representation equivalence: factor / PSD / spectrum — PASS
- streamed block-factor spectrum equivalence — PASS
- general Gaussian quadratic constructor — PASS
- exact scaled chi-square control — PASS
- threshold/log-tail round trip — PASS
- deep-tail hardened arithmetic emits no overflow warning — PASS
- deep-tail adaptive result agrees with a converged exact-spectrum grid — PASS

General API: **7/7 PASS**.

## Re-executed generic structural tests

- approximate polyphase light cone: 5/5 PASS
- budget scheduler: 4/4 PASS
- spectral/tail bridge: 5/5 PASS
- residual trace/cap algebra + MGF envelope smoke subset: 3/3 PASS
- residual exact completion: 3/3 PASS

Total tests executed in this generalized checkpoint: **27/27 PASS**.

The two most expensive pre-existing residual-tail regression cases were not
rerun in this checkpoint after one exceeded the bounded execution window; those
cases remain previously verified in the v0.9 lineage.  This checkpoint does
not use that prior result to inflate the 27/27 count above.

## Reference-convergence audit

A first comparison at rank 350 appeared to disagree with a nominal
"high-resolution" exact-spectrum grid by about 0.00396 decades.  Refining the
reference grid showed:

- K=4,096: difference about 1.88e-2 decades
- K=8,192: difference about 2.6e-3 to 4.0e-3 decades depending on support
- K=16,384: difference about 1.39e-4 decades
- K=32,768: difference about 2.60e-8 decades

The adaptive certified answer was stable.  The initial discrepancy was an
under-resolved reference, not evidence against the hardened solver.

## Arithmetic hardening

The packet approximation error

\[
\frac{2}{U}\sum_k |I_k|\,[\exp(\epsilon_k)-1]
\]

is now accumulated as a log-sum-exp.  Packet-bound comparisons against the
requested tolerance are also performed in log space.

This removes the known transient `expm1`/sum overflow pathway without changing
the accepted mathematical bound.

## Evidence boundary

This is finite software verification plus previously proved matrix identities.
It is not a directed-rounding proof of every float64 operation.
