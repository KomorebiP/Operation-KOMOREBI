# Continue with Block61

Open Komorebi_Beal_Block60_Diagonal_Period_Local_Criterion_v6.0.0.zip as the sole
execution checkpoint. It contains the original Block59 ZIP and all nested
predecessors byte for byte. Read completely before editing:

README.md; work60/TARGET_CONTRACT.md; work60/REPORT.md; work60/PROOF_BOUNDARY.md;
work60/THEOREM_INDEX.md; work60/GAP_LEDGER.md; work60/notes/DIAGONAL_PERIODS.md;
work60/notes/LOCAL_CRITERION.md; work60/notes/LOCAL_SURVIVORS.md;
work60/notes/SELF_REVIEW.md; work60/source_records/SOURCE_CHECK.md;
work60/DEVELOPMENT_FAILURES.md; work60/VERIFICATION.md.

Cleanly extract and run:
    python verify.py --replay-predecessors --report ../Block60_Replay.json

## New exact result

For a primitive local triple at q outside{2,3,5,7}, C=q^k C0, the three actual
marked period classes are epsilon*kappa_a,epsilon*kappa_b,-phi^-4, where
kappa_a=-phi^2/(675sqrt5), kappa_b=phi^-2/(675sqrt5), epsilon=C^7/A^3.
The full Kummer matrix is [[Z+2X,-4X],[-4X,Z-2X]], with X=[phi] and
Z=7[C]-3[A]-3[3]-5[sqrt5]. This is a local marked identity, NOT a global
semilinear comparison or an identification of base and coefficient fields.

Full local natural J[49] rationality is EQUIVALENT to
49|Q-1,7|k,phi49, and E=3*5^9*A/C0^35 a49th residue power. At actual beta
support n2 the stronger inherited multiplicity is v7(k)=1. At level7 the
unit criterion is75A a7th power. Principal units cannot add another7-primary
obstruction at q!=7, so the torsion-power period calculation is complete.

## Critical surviving controls

ALL FOUR primes197,883,1373,1667 still survive. For C=q^7 the local families
with A residues148,228,1028,1449 and B residues81,27,497,984 have full49-torsion.
B is a q-adic fifth root, NOT asserted an ordinary integer. These realize local
Frey geometry, not merely abstract matrices, but do not construct a global
reducible representation, common alpha, beta or an integer solution. Do not
reopen the failed 'all period powers exclude883' route without an additional
same-global-representation constraint.

## Next substantive target

Tie these TWO actual local Kummer coordinates to the SAME global natural
class and chi^-1-twisted opposite endpoint, including fixed-prime data. Preserve
the new actual A,C0 unit congruence as well as all old ratio/multiplicity
conditions. A full local torsion test is not sufficient for global beta.
Do not apply eta's ordinary ray rows directly to beta; do not identify R^2=5I
with the missing global lattice comparison. Independent upstream proof review
is still an obligation. No new Lean certificate or independent reviewer is
claimed. Depth1, general depth2, unrestricted support, CM, higher Hilbert
levels, full signature and Beal remain separate open obligations.
