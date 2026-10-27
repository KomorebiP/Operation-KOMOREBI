# Global ABC progress and source calibration

Checked 2026-10-25. Base RR4 archive SHA-256:
`689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae`.
Read input hashes are in `INPUTS.json`. Existing checkpoints were not edited.

## Exact target and current outcome

For every fixed epsilon>0, full ABC asks for only finitely many primitive
positive triples a+b=c with c>rad(abc)^(1+epsilon). Write
lambda=1/(1+epsilon), so 0<lambda<1. These exceptions are exactly the
triples with rad(abc)<c^lambda.

RR2 proves an unconditional global count

    E_epsilon(X) <= C(3,eta/3) X^(lambda+eta)

for every fixed eta>0, where the count is ordered and c<=X. Its elementary
Euler product proof has a separate audit. This is a valid global statement,
but it is weaker than the standard elementary count below and is not a
global improvement on the literature.

RR3 supplies stronger pointwise criteria in the restricted common-power
family A^n+B^n, including the cyclotomic degree budget and a near-linear
exceptional-prime cutoff. RR4 establishes exact tap and refinement identities
and obstructions; it does not improve that pointwise cutoff. These are useful
structural progress, not a bound on arbitrary primitive triples. Taking n=1
does not extend large-n estimates to arbitrary triples.

## An immediate strengthening of our own count

This is a short independent derivation of the standard elementary exponent,
using the already proved RR2 Euler product. It is not a novelty claim.

Let B(X,Y) count ordered primitive positive triples a+b=c<=X with
R=rad(abc)<=Y, where X>=2 and Y>=1. For delta>0, RR2 establishes

    sum_(m<=Z,rad(m)<=T) k^omega(m)
       <= C(k,delta) T Z^delta,
    C(k,delta)=product_p (1+k/[p(p^delta-1)])<infinity.

Since a,b,c are pairwise coprime, put r_a=rad(a), r_b=rad(b), r_c=rad(c).
The product of the three pair products r_a r_b, r_a r_c, r_b r_c is R^2.
At least one of these pair products is at most R^(2/3)<=Y^(2/3).

For each of the three possible pair types, let m be its ordinary integer
product. Then m<=X^2 and rad(m)<=Y^(2/3). There are exactly 2^omega(m)
ordered coprime factorizations of m into that pair, since each full prime
power is assigned to one of two factors. Each specified pair determines the
remaining member of a+b=c uniquely. Some assignments produce no positive
triple, which only makes this an overcount. Taking the union of the three
pair types and applying the Euler bound gives

    B(X,Y) <= 3 C(2,delta) Y^(2/3) X^(2 delta).

Substituting Y=X^lambda and delta=eta/2 proves

    E_epsilon(X)
       <= 3 C(2,eta/2) X^[2/(3(1+epsilon))+eta].

This improves the internal RR2 exponent lambda+eta to 2lambda/3+eta.
No new external theorem or finite computation is needed. The universal
proof is the displayed factor-allocation argument. It recovers the
established elementary bound, and still allows infinitely many exceptions.

## Current primary-source comparison

Source authentication and theorem extraction were performed on the arXiv
abstract/version pages and the indicated PDF text. This is a comparison of
theorems as stated in those primary sources, not an independent audit of
their entire proofs or computational appendices. No full external source
text was copied into this package.

1. Christian Bernert, *The exceptional set in the abc conjecture*,
   arXiv:2506.13364v1, submitted 16 June 2025, PDF internal date 17 June 2025.
   Primary locator: <https://arxiv.org/pdf/2506.13364v1>.
   Its N_lambda(X) uses the same positive primitive triples and strict
   radical cutoff. Theorem 1 states exponent (23lambda+3)/40+eta for
   lambda in (0,2), every eta>0. The concluding improvement to 8/13 at
   lambda=1 is presented as a sketch. No sketch is used in our argument.

2. Christian Bernert, Tim Browning, Jared Duker Lichtman and Joni Teravainen,
   *Bounds on the exceptional set in the abc conjecture*,
   arXiv:2410.12234v2, submitted 9 May 2026. Primary locator:
   <https://arxiv.org/pdf/2410.12234v2>.
   Proposition 1.1 states exponent 2lambda/3+eta for lambda>0.
   Theorem 1.2 states exponent (23lambda+3)/40+eta for lambda in (0,2].
   Theorem 1.3 states N_lambda(X) <<_(eta,lambda) X^(0.6+eta) for each
   lambda in (0,1), every eta>0. Thus the current paper is stronger than
   our global count in the near-critical range. For all lambda in (0,1)
   one can retain the best of these bounds, not just the uniform 0.6 bound.
   The version page and PDF header identify v2. The PDF internal date is
   12 May 2026, whereas the HTML view displays 24 August 2026. Pin the
   arXiv version ID rather than identifying the version by its internal date.

Our dictionary is lambda=1/(1+epsilon). The papers' small exponent slack
is denoted eta here, so it cannot be confused with our ABC quality excess.
Their gcd(a,b,c)=1 condition is equivalent to gcd(a,b)=1 under a+b=c.
Their box [1,X]^3 is equivalent to c<=X for positive additive triples.

The internal strengthening is **known after translation of notation**:
it recovers Proposition 1.1 with an explicit Euler-product constant.
The original RR2 count is a weaker consequence, not a new global record.

## Why global finiteness remains open in this program

All displayed counting exponents remain positive. A count bounded by
X^alpha for alpha>0 is compatible with infinitely many very sparse heights.
Even an X^o(1) upper count alone would not force finiteness. Counting a
small number of exceptional allocations therefore differs from excluding
every sufficiently high exceptional allocation.

The elementary argument exploits the additive equation only to obtain
pairwise coprimality and recover one entry from a pair. It has no mechanism
that bounds the final exceptional height. The present task does not supply
such a mechanism or an IUT repair. The unrestricted global target remains
open. An IUT comparison estimate would require its own independently
verified hypotheses, normalization and height-error budget before being
combined with these results.
