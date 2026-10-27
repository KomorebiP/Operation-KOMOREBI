# Stochastic Polyphase Refinement Theorem v0.1.0

This block extends the checked stochastic covariance-residual theorem with exact multiscale/polyphase refinement.

Let the actual covariance tangent be

`L(A0+RA,P,Q0+RQ) = (A0+RA)P + P(A0+RA)^T + (Q0+RQ)`

and suppose `A0`, `P`, and `Q0` respect a coarse packet decomposition. For distinct coarse packets `a != b`, Lean proves that the baseline contributes exactly zero and

`B_a^c L(A0+RA,P,Q0+RQ) B_b^c`

is exactly the coarse block of the named residual forcing

`F = RA*P + P*RA^T + RQ`.

If a fine packet system refines the coarse one by `rho`, Lean then proves

`B_a^c F B_b^c = sum_{rho(c)=a, rho(d)=b} B_c^f F B_d^f`.

More strongly, because coordinate fine blocks have disjoint support,

`B_a^c F B_b^c = 0`

iff every descendant block `B_c^f F B_d^f` is zero. Therefore

`B_a^c F B_b^c != 0`

iff at least one descendant is nonzero. This gives a rigorous adaptive refinement trigger: a coarse leakage channel is present exactly when some finer leakage channel is present.

The same statements are checked for literal residue/polyphase lanes. A fine phase modulo `m*k` coarsens by reduction modulo `m`; the theorem is specialized further to every dyadic depth `m*2^r`.

## Stochastic specialization

For distinct coarse packets, Lean proves

`packetBlock coarse a b (covarianceRHS (A0+RA) P (Q0+RQ))`

equals the sum of fine descendant blocks of

`covarianceRHS RA P RQ`.

Thus all instantaneous cross-packet covariance creation is attributed to named fine residual channels, while the exactly packet-preserving baseline disappears identically.

## Verification and limitations

The full source passes the preserved Lean 4.34.0-rc2 / pinned-mathlib checker. Representative central theorems depend only on `propext`, `Classical.choice`, and `Quot.sound`.

The no-cancellation result uses coordinate packet blocks with disjoint support. A general arbitrary-projector analogue would require additional orthogonality/direct-sum hypotheses and is a separate theorem target.
