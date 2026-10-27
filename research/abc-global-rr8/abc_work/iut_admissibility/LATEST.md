# IUT admissibility and hull checkpoint RR6

The original target is every-epsilon ABC finiteness for all primitive positive
triples a+b=c. It remains open. This pass supplies no new global ABC exponent,
no verified IUT repair, and no disproof of the full IUT construction.

Base: the exact RR5 archive, SHA-256
79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01.
All earlier phase records and live views are preserved unchanged.

## What changed

The definition-level source pass distinguishes three operations: choosing
an admissible input region S, forming an output family, and choosing a hull
approximant after that family exists. They are not interchangeable. LANA's
compressed survey does not give a complete predicate for suitable S. This
limits its use as a standalone proof input; it does not establish that the
original theory has no such constraints. Original IUT approximants remain
inside a fixed hull. Their freedom alone cannot prove that an arbitrary
native pilot value is below the hull's existing numerical cap.

The attempted repair by matching raw volume fails as a sufficient argument.
Even compact-open regions of the same volume can have different ideal hulls.
For m>=2, the two regions

    3^m Z_3 union (1+3^m Z_3),
    3^m Z_3 union (3^(m-1)+3^m Z_3)

have common measure 2*3^(-m), but hulls Z_3 and 3^(m-1)Z_3. The hull
log-volumes differ by (m-1)log 3. The common raw measure varies with m;
no unbounded gap at one fixed positive raw measure is asserted. Additional
admissibility restrictions or retention of representatives may avoid this
diagnostic. It is not a counterexample to actual IUT.

There is a concrete sufficient local certificate. In a bounded product of d
local-field factors, the hull of an arbitrary family is determined by at most
d valuation witnesses. Native-ideal containment is equivalent to explicit
coordinate valuation inequalities in that same family. This does not produce
the admissible witnesses or settle the remaining places and global comparison.

Permutations inside a homogeneous tensor packet have also been treated
exactly. Different slots for the same local q differ only by units after
integral closure. The orbit hull is q_i times the symmetrized original hull;
if that hull is invariant, the inserted q power is retained. These factor
permutations do not license moving between separate j^2 stages.

Finally, the fixed-realization Ind2 source interface preserves a
mono-analytic lattice I. The elementary lattice calculation retains p-depth
up to an explicit lattice width a-b, where p^a J subset I subset p^b J and
J=O_A I. For an orbit of q^s I with common component valuation alpha, its
hull is contained in p^[floor(s alpha)-(a-b)] J. The exact source-to-output
identification, width uniformity, other actions and Ind3 remain separate
unproved obligations. This is a restricted control, not a global estimate.

## Evidence

The raw local algebra proofs, exact counterexamples, and focused reviews are
included. Review corrected the general integral-action lemma's hull domain
to bounded full-span sets; its earlier draft and the reason are preserved.
The finite-hull and tensor claims also received a context-free
replication. Source authentication/extraction is distinguished from proving
the IUT reconstruction leaves. No finite mathematical experiment or Lean
compilation was needed or run for these claims. No novelty claim is made.

See [claims](CLAIM_LEDGER_RR6.md), [sources](SOURCES.md), and
[next research obligations](HANDOFF.md). RR5's global counting result is
unchanged. The strongest new information concerns the compatibility mechanism.
