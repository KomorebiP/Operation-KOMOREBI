# Continuation from ABC-20261025-RR2

## Exact target and done condition

For every epsilon>0, prove finiteness of primitive positive a+b=c with
c>rad(abc)^(1+epsilon), or disprove that assertion with a verified infinite
fixed-epsilon family. A fixed exponent, an ordinary-hit family, or an
exceptional-set bound is partial progress only.

Parent archive hash:
`f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.
There is no executable .mathbox ledger in the inputs. The versioned claim
ledger and hashed route files supply the checkpoint ancestry. No earlier
progress history was rewritten.

## Primary next obligation

In the common-power family let d_p=ord_p(A/B) and
e_p=v_p(A^d_p-B^d_p). At odd p|A^n+B^n, e_p=1 is ordinary.
All ordinary powerful-part mass divides n. The remaining weight is

    W_n=product_(odd p|A^n+B^n) p^(e_p-1).

The next worthwhile estimate must control this weight at large exceptional
primes, with quantified dependence on A,B,n. For odd prime n=ell, remove
U(A+B) and the optional ell factor first. The only new weight then comes
from exceptional primes of order 2ell, hence p>=2ell+1. For binary exponents
n>=2, the entire output powerful part is exceptional and primitive.

A candidate uniform bound must be tested first at base 2, p=1093,n=182,
where the exceptional factor cannot be omitted. It must also be checked
with varying bases. A proof merely bounding ordinary lifting or small
exceptional primes repeats an already resolved sub-obligation.

No estimate controlling all large exceptional weights was established here.
This route remains open. Extending the half-order calculation to arbitrary
1+hq^n also requires a new mechanism because -h^(-1) need not have order two.

## Other routes and resumption conditions

| Route | Executed outcome | Open next step and resumption condition |
| --- | --- | --- |
| Full-radical counting | Improved sparse counts using positive divisor/Euler series | State an additive arithmetic saving that forces eventual emptiness; resume when an actual proposed estimate has been formulated. Current growing count bounds cannot provide this |
| Global allocation count | Full primitive family has a sublinear fixed-excess count | Retain a+b=c beyond its coprimality and coarse size consequences; no such saving was proved |
| Quadratic reverse realization | Complete-radical budget retained; perfect-power branch bounded | Use multiplier primality or squarefreeness together with the radical restriction. Pure congruence-based escape is refuted by the fixed-Q family |
| Counterexample search | Two infinite ordinary-hit families established | Determine a fixed-positive-excess radical estimate. The families do not provide ABC counterexamples; no missing radical lower bound may be assumed |
| Arithmetic derivatives | Exact Wronskian image and integer quotient J identified | Bound integral nondegenerate coordinate norm relative to J. Image existence and rational projection do not pay the integral lift cost |

The derivative sufficient condition must retain every positive exponent:
for each delta>0, seek a nondegenerate integral lift with H/J bounded by
C_delta c^delta on the proposed domain. An explicit exception family must
be settled independently. The customary source exception consists of
unordered entries {1,N,q} with q prime; its radical bound is immediate.
This small-lift statement is a sufficient condition, not a proved equivalence.
One unspecified small-derivative exponent below 1 only gives a fixed-exponent
ABC estimate by Pasten's stated dependencies.

## Review and verification boundaries

Reviews are linked in `CLAIM_LEDGER_RR2.md`. The global original review pins
a pre-supplement snapshot, and its supplement pins the current proof.
The complete five-route finite reproduction is `python3 abc_work/reproduce.py`
from the extracted package's top directory. Manifest validation is described
in the outer README. No Lean code was produced or run in this checkpoint.

The fixed-offset correction in `ERRATA.md` must be retained on continuation.
Do not treat an omitted gcd(h,Q)=1 as harmless if its formula is stated alone.

The available mechanisms were advanced to their current exact bottlenecks.
The unresolved continuations are deferred, not claimed exhausted or impossible.
The next research cycle should supply and attack one explicit candidate large
exceptional-weight or integral-lift estimate, with a falsifying control, rather
than extending finite searches without a discriminating mathematical question.
