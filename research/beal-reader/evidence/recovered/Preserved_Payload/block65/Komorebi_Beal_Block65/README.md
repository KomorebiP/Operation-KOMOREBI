# Komorebi Beal — Block 65
## Coefficient rigidity and the prime-379 conductor obstruction

Version 6.5.0. 20 September 2026.

The original goal, the retained reducible branch of A^3+B^5=C^7, is not solved.
The next bounded block is complete. All arithmetic conclusions retain the
explicit geometric and representation hypotheses in work65/TARGET_CONTRACT.md.

New results:
1. At depth one, if the opposite class descends to Q as a chi^-1 cohomology class,
   its normalization with a5=1 has an F7-valued representative and
   alpha=(v*w,r,1), v,r in F7^*. This does not require a finite bound on its conductor.
2. Both retained 547/743 tuples fail the actual good AND bad Frobenius conditions
   at 379. The complete 21-prime conductor W65 listed in the report is excluded.
3. The larger declared 25-prime conductor system has 112 surviving tuples.
   They are preserved as necessary-system survivors, not actual representations.

The original Block64 ZIP is retained byte for byte, with all earlier releases
nested unchanged. Production uses Python 3.10+ and the standard library.

    python -B verify.py --replay-predecessors --report ../Block65_Replay.json

Default mode regenerates all six new outputs and checks deliberate errors.
The explicit flag also replays the entire declared selected predecessor chain.
Timeouts are inconclusive. Do not enable bytecode writes in frozen extractions.

The proofs are written conditional arguments. Arithmetic has separate code
implementations. No new Lean compilation, independent mathematical review,
global novelty claim, global Tate-lattice descent, or Beal solution is supplied.
