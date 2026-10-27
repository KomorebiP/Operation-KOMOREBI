# B64.5. Arithmetic consequences and exact quantifiers

All conclusions retain TARGET_CONTRACT.md. Define

    U={97,197,293,491,587,883,1373,1471,1567,1667},
    V64=U union{43,113,127,337,463,547,617,953}.

The six primes U\{197,883,1373,1667} are already excluded from beta ramification
at every depth by the retained natural-period condition. Combining that fact
with B64.3 yields

    n=1 => beta ramifies at a prime outside V64.

The new outside-support theorem is not an exclusion of every conductor,
or of any individual prime in V64 when other ramification is present.

Under COMPLETE H(C) subset U, the inherited result still gives n=1. A required
supporting prime outside V64 therefore has h=v7(q^f_q-1)=1 and
v7(v_q(C))=0. It must satisfy the inherited phi and75A seventh-power residue
conditions. Arbitrary such outside low-congruence support is not bounded.
The entire H(C) subset U class remains open.

For the full geometrically eligible divisor set

    E(C)={q|C: q outside2,3,5,7, q^f_q=1 mod7,
                  phi a seventh-power residue at its K-place},

there is the enlarged all-depth exclusion

    COMPLETE E(C) subset V64 => no retained reducible representation.

Proof. A nontrivial highest eta layer is geometrically eligible and has h>=2.
All the eight added primes outside U have h=1, so the highest layer would be
supported above U, contrary to Block58. Hence eta is fully trivial. At n>=2,
actual beta support has h>=floor(n/2)+1>=2, so the added low-h primes cannot
support beta. The six geometrically excluded U primes leave S={197,883,1373,1667},
which the retained full-eta higher-depth argument excludes. At n=1 use B64.3.
These arguments allow extra divisors failing eligibility, but do NOT bound E(C)
for arbitrary triples. No size-based contradiction from a product of primes
is claimed. The separately forced2549 need not ramify in eta or beta.

The nonzero unit coefficient and13|C remain preserved at every depth. The
whole reducible branch, unrestricted depth1 and depth2, higher support,
CM nonboundary points, higher Hilbert levels, full signature and full Beal
remain separate unresolved obligations.
