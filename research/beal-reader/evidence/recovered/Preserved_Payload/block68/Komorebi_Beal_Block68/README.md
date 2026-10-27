# Komorebi Beal research — Block 68, v6.8.0

Degree-two cyclotomic conductor columns, a complete 28-prime necessary-system
calculation, and a conditional seven-prime support barrier.

Start with work68/REPORT.md and work68/PROOF_BOUNDARY.md. The old 25-prime
conductor stays excluded. The full 28-prime system does NOT vanish: 94 tuples
remain after the three new actual Frobenius tests. They are not representations.

    python -B verify.py --report ../Block68_Replay.json

Add --replay-predecessors to rerun the entire selected historical chain. The
original Block67 ZIP is included unchanged. Its full selected-chain replay was
observed in this session and is retained in work68/verification/Block67_Replay.*.
The default command regenerates all new scientific outputs in a clean scratch
copy and checks the inherited source hashes. No network is needed.

Python's standard library is sufficient. When NumPy is already installed, the
new counters use optional exact int64 vectorization. Set BEAL_FORCE_STDLIB=1
to use the original scalar algorithms. No floating arithmetic is used.

No new Lean compilation or independent mathematical reviewer. The analytical
geometry and global representation inputs remain explicit conditional leaves.
