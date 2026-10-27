# ABC polyphase and tap checkpoint RR4

The tested polyphase refinements and taps are useful for exact localization
and for constructing nonzero auxiliary integers. They have not improved RR3's
near-linear exceptional-prime cutoff or closed the remaining high-order ABC
obstruction. The full conjecture remains unproved.

Parent checkpoint: RR3 archive SHA-256
`557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302`.

For coprime A>B>=1, write s_n=A^n+B^n. The constructive two-tap identity is

    s_(n+h)-B^h s_n=A^n(A^h-B^h).

Extended Euclid gives a genuinely nonzero certificate

    u s_n+v s_(n+h)=G_(n,h)=gcd(s_n,A^h-B^h)>0.

It is the smallest positive integer obtainable by unrestricted integer taps
at that stride. When h is small relative to n, G_(n,h)<A^h is a smaller
height certificate retaining the appropriate first-contact factors. For example,

    -511*(8^3+1)+8*(8^5+1)=9.

At the unresolved primitive stride h=2n, however, G_(n,2n)=s_n. Aligned taps
give zero or an integer at least as large as the original output. Half-order
sum-sequence shifts lose the odd contact instead. Vanishing moments multiply
both the contact depth and its degree-height cost by the same factor.

Polyphase refinement retains the same obstacle. With n=Mt and blocked bases
A^M,B^M, the local order and first-contact depth become

    d'_p=d_p/gcd(d_p,M),    e'_p=e_p+v_p(M).

The output's total birth/lifting product is unchanged. The exact old occupied
cyclotomic product divides the blocked product, and D_n<=M D'_t. A smaller
degree after decimation is paid for by the larger base height.

For a reconstruction bank, the preserved integral quantity is the minimum
channel valuation. A deep individual sum can move into cancellation between
unit channels. Concentrating depth in all channels charges it to a determinant
or denominator. Real energy preservation alone is not a p-adic bound.

The live continuation is an adaptive construction of a controlled nonzero
integer that preserves the required exceptional factors while genuinely
lowering the height budget. Its nonvanishing, tap cost, evaluated degree,
determinant and denominators all need proof. The tested identities do not
supply that construction.

See [the ledger](CLAIM_LEDGER_RR4.md), [the handoff](HANDOFF.md), and
[the source dictionary](SOURCES.md). The three exact finite contracts passed.
Separate proof reviews are included. No Lean compilation or historical
originality claim is made.
