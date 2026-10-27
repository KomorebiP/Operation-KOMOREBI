# Komorebi Beal research — Block67, v6.7.0

Deep cyclotomic semilinearity, complete P2000 depth-one conductor closure, and
an explicitly scoped minus-component reciprocity condition at13.

Start with work67/REPORT.md and work67/PROOF_BOUNDARY.md. The new proofs are
in work67/notes. Production code needs only Python3's standard library:

    python -B verify.py --replay-predecessors --report ../Block67_Replay.json

The original Block66 archive is preserved byte for byte under predecessor/,
with its own nested history. The new finite certificate has separate arithmetic
implementations and deliberate rejection controls. No new Lean compilation or
independent mathematical review is claimed. The original Beal goal remains open
within this project; all arithmetic applications retain the inherited hypotheses.

Continue using work67/CONTINUE_HERE.md. Do not treat the finite P2000 exclusion
as a bound on an arbitrary conductor, nor extend the fixed13-zero condition
from low depth to all depths solely because semilinearity now holds generally.
