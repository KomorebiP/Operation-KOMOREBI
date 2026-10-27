# Euler threshold-free program, 2026-10-06

Base: Nishibuchi_Conjecture_Completion.pdf, extension v0.11.0,
and the visible threshold-free conjecture proposed in this conversation.

Exact original goal:

    v_2(Delta_u^k C_(4,j)(n))>=k

for all j=0,1,2,3 and all natural n,k,u, including k>n.

C_(N,j) is defined by the actual reciprocal

    sum C_(N,j)(n) t^(Nn)/(Nn)!
      = [j! sum t^(Nn)/(Nn+j)!]^(-1).

Proof means a universal argument from that exact definition. Exact-rational
or modular tests corroborate it; no finite success count proves the theorem.

The original generalized Euler normalization is E_(Nn)^(N,j)=j! C_(N,j)(n).
The old completed estimate was min(k,n), not the present global k estimate.

This program is distinct from the open Euler-tail universal simplicity
and stationary-discriminant nonvanishing problem. A congruence improvement
does not discharge those arithmetic root obligations.

Parallel work has disjoint scopes: combinatorial/, measure/, computation/,
sharp_periods/, review/. There is no executable .mathbox ledger or external
Git repository here. Final proof/evidence hashes will pin this checkpoint.
