# ABC research checkpoint RR2

The full ABC conjecture remains unproved. This checkpoint extends the latest
square-kernel archive rather than replacing the target with a density claim.

The strongest pointwise progress is in the common-power family
`a=A^n, b=B^n, c=A^n+B^n`, for coprime integers A>B>=1. Its output powerful
part satisfies exactly

    U(c)=B_2(n) W_n G_n,     G_n|n,     B_2(n)<=A.

Here W_n records exceptional repeated-prime contributions at first occurrence.
The entire ordinary odd-prime contribution divides n. If all exceptional
output primes are at most n^(1/2-delta), with fixed 0<delta<1/2, then for
each epsilon>0 and all sufficiently large n, uniformly in A,B,
`c<=rad(abc)^(1+epsilon)`. Prime and binary exponent identities isolate an
even sharper primitive-prime obstruction. See [the proof](routes/global/PROOF_NOTE.md).

The remaining issue on this route is a weighted bound for large exceptional
prime contacts. The route also needs new input to cover arbitrary exponent
vectors or unrestricted multipliers. Its representation with n=1 does not
make its large-n estimate a theorem about every primitive triple.

Full-radical counting improves the prior restricted exception exponent and
gives a global sparse-count theorem. Neither counting statement implies
finitely many exceptions. An exact arithmetic-derivative image formula
identifies an integral lift cost that ordinary projection cannot bound.

The inherited fixed-offset statement needs explicit multiplier coprimality.
The corrected standalone statement is in [ERRATA.md](ERRATA.md).

All five finite contracts ran successfully with exact arithmetic. Their
version 2 evidence records validate. Proof reviews are separate from these
computations. No Lean compilation or historical novelty claim is made.

Read [the claim ledger](CLAIM_LEDGER_RR2.md) for scope and review records,
and [the handoff](HANDOFF.md) for the next exact obligations.
