# Komorebi Beal research — Block 59
## Natural torsion, nodal periods, and the depth-two opposite extension

Version 5.9.0. Continuation of the exact original Block58 checkpoint.

Main conditional arithmetic result: if the actual opposite extension beta
ramifies at depth two at a variable place v, then the full natural twisted
Jacobian J^nu[49] is locally rational and phi=(1+sqrt5)/2 is a forty-ninth
power in the residue field. More generally every beta-supporting place
requires phi to be a seventh power. The geometric restriction uses the
unit period of the two-node stable reduction, with residue -phi^(-4).

On the complete ten-prime high-divisor class from Block58, depth two now
has beta support only above {197,883,1373,1667}. No theorem eliminates
these remaining places. Beal and the full (3,5,7) signature are not solved.

Read work59/REPORT.md, TARGET_CONTRACT.md and PROOF_BOUNDARY.md first.
The proofs are in work59/notes/. Reproduce with Python 3.10 or later:

    python verify.py --replay-predecessors --report ../Block59_Replay.json

Only Python's standard library is required. The predecessor ZIP is retained
byte for byte. All earlier sources, computations, failed routes and retractions
remain nested inside it. New evidence consists of written proofs, exact
computations and an adversarial author self-review. No new Lean compilation
or independent mathematical review was performed. A successful verifier run
checks declared finite assertions and file integrity, not the analytic theorems
or all upstream Frey-geometry hypotheses.
