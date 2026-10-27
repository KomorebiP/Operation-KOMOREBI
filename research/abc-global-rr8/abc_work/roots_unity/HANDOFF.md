# Continuation after the roots-of-unity test

Checkpoint ABC-20261025-RR3 extends the RR2 archive pinned in LATEST.md.
The full target is unchanged: every-epsilon primitive integer ABC, including
arbitrary triples. There is no Git revision or executable .mathbox ledger in
the supplied inputs. Content hashes and versioned claim ledgers record ancestry.

The next exact inequality must retain the input radical. In the common-power
family c=A^n+B^n, put D=rad(AB). RR2 gives U(c)=B_2 W_n G_n, G_n|n. For
gamma=epsilon/(1+epsilon), a quality exception is exactly

    log W_n > gamma log c + log D - log B_2 - log G_n.

The cyclotomic degree theorem controls the left side when exceptional birth
orders occupy a small total degree. It does not prove that this happens in
the remaining high-degree packets. Nor does a large-n theorem cover arbitrary
inputs by setting n=1.

Its divisor-count corollary improves the sufficient exceptional-prime cutoff
to n^(1-delta) for every fixed 0<delta<1. Thus the next moving-prime test can
focus above that nearly linear threshold in this restricted family. The
corollary imposes no automatic exclusion of those larger exceptional primes.

The primary next task is to state and test a quantitative comparison for a
specified simultaneous contact packet at moving primes. A candidate must
include dependence on bases, prime support, torsion orders, depth, and radical.
It must survive primitive Hensel contacts, the birth-depth plateau, synchronized
exponent filters, and the bounded-n output-only counterexamples.

| Route | Executed outcome | Deferred continuation and resumption condition |
| --- | --- | --- |
| Conductor/character filters | Exact depth and lcm-correlation laws; naive extra-depth rarity refuted | Resume when a proposed arithmetic bound on the principal birth coefficient is supplied. A new orthogonality identity alone is not such a bound |
| Cyclotomic resolvents | Pole preservation and resultant divisibility/height budget | Resume with an adaptive filter family whose moving resultant height is independently bounded and whose observable remains nonzero |
| p-adic torsion split | Exact depth equality and explicit height-paying arbitrary contacts | Resume with a bound on unusually small rational representatives of simultaneous moving torsion contacts, retaining input radical |
| General torsion-distance transfer | Source contracts verified; the local constant is precisely the unknown depth | Resume with a theorem giving the missing quantitative uniform dependence, or another valid dictionary preserving fixed variety and torsion hypotheses |
| Auxiliary polynomial | Modular shortness can lie in the exact-zero lattice | Resume after defining the admissible space and proving nonvanishing with a height bound. Requiring merely a nonzero coefficient vector is insufficient |
| Cyclotomic order budget | Restricted pointwise criterion established | Resume on the remaining high-degree exceptional packets; do not assume the degree condition holds automatically |

Known controls to retain:

* A=2,B=1,p=1093: order 364, birth depth 2, contact at n=182 and 546.
* A=7,B=1,n=2,p=5: output 50 has depth 2 with unit derivative and discriminant.
* Binary n, P(T)=T-2, A=2: the moving resultant is 2^n+1 and the filtered
  observable vanishes. Small coefficient norm does not imply small resultant.
* At n=1, A=p^e-1,B=1: log(W)/log(c) tends to 1. Any unrestricted claim must
  retain the input radical or separately handle this boundary.

All current route proofs and reviews are linked in CLAIM_LEDGER_RR3.md.
Finite computations are separate evidence with exact stated domains. No
external article text was copied into this checkpoint, and no novelty claim
or Lean compilation is included. The generalized roots-of-unity route remains
open. The specific shortcut mechanisms above were tested and their failures
recorded without asserting impossibility of the broader approach.
