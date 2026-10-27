# Komorebi Beal — Block 66
## Semilinear cohomology and actual Frobenius refinement

Version6.6.0. 20 September2026.

The original Beal/signature/reducible-branch goal is NOT solved. This bounded
block proves stronger conditional structural results and narrows a complete
finite conductor system, under the explicit inherited actual-model hypotheses.

New results:
- At depth one the normalized natural coefficients satisfy alpha=(v*w,r,1),
  v,r in F7^*, WITHOUT assuming beta descends to Q. The opposite class satisfies
  j beta=sigma beta in cohomology, not necessarily ordinary descent.
- Beta has two rational cohomology components of types chi^-1 and
  chi^-1 epsilon5. The second cannot ramify at inert variable primes and must
  satisfy a genuine locally trivial condition at13.
- Four exact good/bad Frobenius tests reduce the112 retained complete-P2000
  tuples to two, with alpha=(+/-w,6,1) and inertia337/547/673/1933=(4,6,2,3).
  They are necessary-system survivors, not actual Frey representations.

The original Block65 archive and all nested predecessors are preserved exactly.
Run with Python3.10+ and its standard library, with bytecode disabled:

    python -B verify.py --replay-predecessors --report ../Block66_Replay.json

Default mode rebuilds all six new output records and checks deliberately
corrupted inputs. The explicit flag also runs the retained selected predecessor
chain. A timeout is inconclusive, never a mathematical exclusion.

Proofs are written conditional arguments with separately implemented finite
arithmetic. No new Lean compilation or independent mathematical review occurred.
Start with work66/REPORT.md and work66/PROOF_BOUNDARY.md.
