# Komorebi Beal — Block 64
## Common-polynomial Frobenius compatibility and the prime281 obstruction

Version6.4.0. 20 September2026.

The retained conditional research problem is the reducible Frey-representation
branch for primitive integer triples A^3+B^5=C^7. This package does not solve
that branch, the whole signature, or Beal.

The two Block63 tuples on beta support113/617/883 are excluded by the ACTUAL
Frobenius corrections at281, considering both good and bad reduction. The
complete depth-one beta conductor

    W64={43,113,127,197,337,463,547,617,883,953,1373,1667}

is excluded. Additional divisors of C unramified in beta remain unrestricted.
A new common-polynomial test prevents using two unrelated good Frobenius
polynomials at the two split places. After743 is added, TWO tuples still
survive this stronger system, with beta support547/743. They are not asserted
representations or integer solutions.

The original Block63 ZIP is in predecessor/, unchanged, including its entire
nested history. Run with Python3.10+ and the standard library:

    python -B verify.py --replay-predecessors --report ../Block64_Replay.json

Default mode replays the six new computational outputs and negative controls.
The explicit flag also executes Block63 and its declared selected predecessor
chain. Read work64/REPORT.md, PROOF_BOUNDARY.md and CONTINUE_HERE.md.

No Lean compiler, independent mathematical reviewer, or global novelty claim
is supplied. Two arithmetic implementations are not two proof reviewers.
