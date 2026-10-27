# Continue with Block60

Open Komorebi_Beal_Block59_Natural_Torsion_Nodal_Period_v5.9.0.zip as the sole
verified execution checkpoint. It preserves the exact Block58 ZIP and all
nested predecessors. Read completely:

README.md; work59/TARGET_CONTRACT.md; work59/REPORT.md;
work59/PROOF_BOUNDARY.md; work59/THEOREM_INDEX.md; work59/GAP_LEDGER.md;
work59/notes/LOCAL_TORSION.md; work59/notes/NODAL_PERIOD.md;
work59/notes/GEOMETRIC_SUPPORT.md; work59/notes/KUMMER_LIFT_BOUNDARY.md;
work59/notes/SELF_REVIEW.md; work59/source_records/SOURCE_CHECK.md;
work59/DEVELOPMENT_FAILURES.md; work59/VERIFICATION.md.

Extract cleanly and run:
    python verify.py --replay-predecessors --report ../Block59_Replay.json

Preserve all source/hypothesis boundaries. No new Lean compilation or
independent mathematical review is present. Timeouts are inconclusive.

## Authoritative additions

At beta ramification, the SAME natural representation is I modulo7^d,
d=min(t,floor(t/2)+1). At depth2, t2,s0 and full J^nu[49] is locally rational.
At maximal-order eta inertia it is I modulo7^t, even with beta unramified.
The actual twisted two-node normalization has paired cross-ratio -phi^-4.
Its node-cycle off-diagonal Jacobian period has precisely this residue,
up to inverse, by the audited Schottky product. Full natural7^d-torsion
rationality therefore forces phi to be a7^d residue power.

All beta places require phi a7th power; depth2 requires49th. In U fromBlock58,
only197,883,1373,1667 survive. The other six U primes cannot support beta,
but may divide C. COMPLETE H(C) subsetU still gives n<=2. If H(C) is contained
in{97,293,491,587,1471,1567}, n1 follows even with arbitrary low-h divisors.
At n2 support197 forcesr=a3/a5=6, support1373/1667 forcesr=1;883 is unrestricted
by these four residue rows. All actual support multiplicities require
v7(v_q(C))=1, not an assumption that they are ordinary.

Bad13 now forces a_phi!=0. Combined with Block52, a_phi=0 iff13 does NOT
divide C. Thus every n>=2 case has nonzero unit coefficient. This is a
vanishing equivalence, not its numerical value. Good13 additionally forbids
97,293,587,1567 as divisors, via inert-minus natural residual triviality.

The full transpose Kummer correction map from already-forced prime generators
to twelve U residue places is SURJECTIVE for unramified local errors. Do not omit7d[pi_v] terms from an
abstract mod49 lift. This surjectivity does not realize the actual natural
class or preserve all fixed local values. Exact n2 local matrix controls
at97 and14503 are NOT Frey-realizable because of the new period obstruction.
The197 control passes this necessary test and remains. Phi at14503 and both
18229 places is a7th but not49th power, so the precision distinction is real.

## Next substantive target

Compute other ACTUAL nodal Jacobian periods, especially invariant combinations
of diagonal periods and their smoothing-unit residues, to constrain the four
remaining depth2 primes. Track the primitive equation, scaling and twist.
Or prove a same-natural-lattice comparison tying the actual mod49 Kummer
class and fixed-prime local values to beta. Focus first on883, where the
present period and residual Kummer tests are both silent.

Do not turn one period power into full torsion splitting; do not apply eta's
ordinary ray rows to chi^-1-twisted beta without proving a comparison; do not
assume arbitrary Kummer corrections are actual geometry. Distinguish beta,
maximal eta inertia, all eta inertia, and H(C). General depth1/depth2,
unrestricted support, CM, higher Hilbert levels, signature and Beal remain
separate obligations. The16 pinned upstream source leaves and their original
archives remain authoritative conditional inputs, not fresh independent proofs.
