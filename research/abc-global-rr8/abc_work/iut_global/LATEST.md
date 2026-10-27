# ABC global and IUT checkpoint RR5

Original target: for every epsilon>0, only finitely many primitive positive
triples a+b=c satisfy c>rad(abc)^(1+epsilon). **Not achieved.** No IUT
repair or new unrestricted pointwise ABC inequality is established here.

RR5 descends from the exact RR4 archive, SHA-256
689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae.
Earlier live views and claim ledgers are retained unchanged.

## What changed

The global count was strengthened internally to

    E_epsilon(X) <= 3 C(2,eta/2) X^[2/(3(1+epsilon))+eta],

for every epsilon,eta>0, with the Euler-product constant defined in the
global-audit note. This recovers a standard elementary bound; it is not
a new literature record. The current arXiv:2410.12234v2, Theorem 1.3,
states N_lambda(X) <<_(eta,lambda) X^(0.6+eta) for fixed 0<lambda<1.
Here lambda=1/(1+epsilon). Its statement and version were checked, not
its entire proof or computational appendix. Neither positive-power count
establishes finiteness.

The IUT source pass located the numerical step in the May 2020 author
version of IUT III, Corollary 3.12, proof Step (xi-e) to (xi-f). It also
checked Mochizuki's September 2018 response, October 2025 report, April
2026 formalization report, and the July 2026 Project LANA interim report.
The last gives a more precise compatibility target: find suitable admissible
S with eta^q=eta^anab_S, retaining the quantitative hull/volume estimate.
LANA reports no proof of this compatibility and withholds a final verdict.
This checkpoint does not independently settle the full IUT argument.

The exact elementary numerical repair criterion is upper cofinality of
actual admissible output log-volumes V at the input value q0. An explicit
additive loss E is allowed. A separate uniform-error lemma records what
would suffice to obtain every-epsilon ABC if the arithmetic comparison
were independently supplied. Neither lemma constructs the required IUT data.

A specific local repair by roots of unity or GL_k(O) changes was tested.
For L_theta=direct_sum pi^(s_j m)O and L_q=direct_sum pi^m O, any lattice
containing L_q after such a change requires normalized enlargement cost
at least (average s_j-1)m log q. The exact lower bound is attained. This
rules out a sublinear-cost repair in this defined lattice class. No
identification of this class with the full IUT hull or indeterminacies is
claimed.

## Evidence and next action

The three elementary proof notes received a focused independent audit:
[review](reviews/elementary_claims.md). All passed as written at their exact
scopes. No new load-bearing finite computation or Lean run was performed.
Source attribution and theorem extraction are separate from proof validation.

See [claim ledger](CLAIM_LEDGER_RR5.md), [sources](SOURCES.md), and
[continuation handoff](HANDOFF.md). The unrestricted ABC goal and the
actual IUT compatibility route remain open.
