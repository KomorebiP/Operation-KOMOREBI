# Komorebi Beal research, Block 53
## Global diagonal rigidity and the good-13 depth-one reduction

Release v5.3.0, 19 September 2026.

Under the explicitly inherited actual-representation inputs, this block proves

    eta_n = 1 modulo 7^(floor(n/2)+1),
    13 does not divide C ==> actual depth n=1.

No ordinary multiplicity hypothesis is needed. This is a written theorem under
the geometric input contract, not a Lean certificate or a proof of Beal. The
reducible (3,5,7) branch, CM branch, other Hilbert levels, and full Beal remain open.

The first new theorem identifies the global diagonal correction through more
than half of the available precision. Its proof combines a characteristic-zero
local trace comparison, natural integral monodromy, and Cl(Q(sqrt5))=1. It also
forces 11*31|C if n>=2, and a stronger finite-field order divisibility at every
good place, without new point counts.

## Read and reproduce

Read work53/REPORT.md, TARGET_CONTRACT.md, PROOF_BOUNDARY.md, and the three notes
DIAGONAL_RIGIDITY.md, ARITHMETIC_CONSEQUENCES.md, LOCAL_INPUT_AUDIT.md.
From the extracted root run:

    python verify.py --replay-predecessors

Only Python 3.10+ standard-library facilities are needed. The report is written
outside this immutable directory. The command verifies all payload hashes,
replays the original Block52 (including Block51 and six selected historical
checks) in temporary copies, and independently reruns both new exact scripts.
It does not compile Lean or authenticate every external theorem by computation.
Timeouts are inconclusive, never successful proofs or exclusions.

The complete original Block52 ZIP is in predecessor/, byte for byte. It retains
the original Block51 ZIP, which retains the recovered Blocks49--50 and their
historical material. No predecessor has been overwritten or silently upgraded.
The interrupted Block50 independent review remains interrupted historical
review, not a successful review by virtue of this replay.

Next work: CONTINUE_HERE.md. The new diagrams/characters are not presumed to
descend under arithmetic conjugation. The remaining higher-depth branch is
necessarily bad at 13 and is not eliminated by the new required divisors.
