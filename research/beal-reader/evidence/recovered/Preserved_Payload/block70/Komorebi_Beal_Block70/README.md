# Beal research — Block 70
## Nine-prime classification and the limits of a finite zero-or-good sieve

Release v7.0.0. The authoritative predecessor is the exact Block69 archive in
`predecessor/`. All earlier checkpoints remain nested there, unchanged.

Two distinct results are recorded. Conditional on the retained Frey-representation
hypotheses, the complete depth-one beta conductor with rational ramification at
primes <=2000 now has eight necessary tuples, in four conjugate pairs. Each has
exactly nine ramifying rational primes and natural ratio6. Separately, an abstract
ray-character theorem shows why a finite set of homogeneous zero-or-good tests
cannot exclude every larger conductor when all bad alternatives remain permitted.
This is not a proof barrier for Beal or for other arithmetic constraints.

Start with `work70/REPORT.md`, `TARGET_CONTRACT.md`, `PROOF_BOUNDARY.md`, and the notes.
The eight tuples are not Frey representations or integer solutions. No new Lean
compilation, external mathematical review, or global novelty claim is made.

Reproduce with bytecode writes disabled:

    python -B verify.py --report ../Block70_Replay.json

The report must be outside this immutable directory. The default rebuilds only
Block70, including both arithmetic implementations and the abstract escape check.
The observed current Block69 replay is retained separately. Add
`--replay-predecessors` only to request its selected historical chain as well.

Python's standard library suffices in principle. NumPy, when installed, supplies
bounded exact int64 counting with no floating-point proof arithmetic. The largest
production counting residue field has 2311^2 elements. Pure-Python replay may need
a substantially larger `--job-timeout`. A timeout is inconclusive.
