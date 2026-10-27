# Continue with Block58

Open Komorebi_Beal_Block57_Forced_Bad_Frobenius_v5.7.0.zip as the sole verified
execution checkpoint. It includes the exact original Block56 ZIP and its
nested predecessors. Read completely before editing:

README.md; work57/TARGET_CONTRACT.md; work57/REPORT.md;
work57/PROOF_BOUNDARY.md; work57/THEOREM_INDEX.md; work57/GAP_LEDGER.md;
work57/notes/LOCAL_DECOMPOSITION.md;
work57/notes/AUGMENTED_RECIPROCITY.md;
work57/notes/FINITE_CLASSIFICATION.md;
work57/notes/ARITHMETIC_CONSEQUENCES.md;
work57/notes/SELF_REVIEW.md;
work57/source_records/SOURCE_CHECK.md;
work57/DEVELOPMENT_FAILURES.md; work57/VERIFICATION.md.

Extract cleanly and run:

    python verify.py --replay-predecessors --report ../Block57_Replay.json

Preserve the hypotheses and evidence boundary. No new Lean compilation or
independent mathematical review was performed. Timeouts are inconclusive.

## New authoritative results

At a variable bad place with h=v7(Nv-1)=0, the actual eta is trivial on the
FULL decomposition group. With general h, its local image has exponent at
most7^h, so the highest global exponent7^e layer is locally trivial if h<e.
The six forced bad prime ideals above11,19,31 add six rows to the original five.
Use their individual generators, not just rational rows:
3+phi,4-phi,4+phi,5-phi,5+2phi,7-2phi.

Highest-layer ramification contained in97/293 is now IMPOSSIBLE regardless
of additional primes dividing C. Do not reopen it using the old five-row
line or its local matrices: the new obstruction is actual Frobenius elsewhere.

For U={97,197,293,491,587,883,1373,1471,1567,1667}, a nonzero highest layer
ramified only above U has exactly one of these patterns, up to a common scalar:
A. alpha=(0,3,1), inertia at97,both491 places,587,1567.
B. alpha=(0,1,1), inertia at97,293,both1471 places,1567.
Both have cyclic order7 image, so eta equals its highest layer. Both genuinely
satisfy the augmented system. Other primes can divide C without eta ramification.

If COMPLETE H(C) subset U, then n<=3. Nontrivial eta has n3 and the two patterns.
All five displayed eta places also support beta with t=1. Pattern B may have
one extra beta place1373 with v7(v_1373(C))=2; pattern A has no extra beta support
under this complete H(C) hypothesis. Without1567, eta=1; without1373 as well,
n<=2. Trivial eta is not trivial beta.

## Next substantive target

Target an ACTUAL common-representation obstruction to one of the two surviving
five-place patterns, allowing the forced divisors197 and491. Possible avenues:
compatible bad-prime toric Frobenius values and monodromy directions; an integral
representation relation tying the known natural Kummer ratio to beta; or an
order-sensitive local-value/ray constraint that extends to unrestricted support.
A new auxiliary prime requires a justified good-reduction hypothesis. A newly
forced divisor alone is not a contradiction.

The rational-uniformizer cancellation in the two classified abelian characters
is proved without a semilinear comparison of Frey lattices. Do not silently
upgrade it to such a comparison. At an inert prime outside their conductor it
gives full local triviality; at a split rational prime it gives only cancellation
of the two values. The Q29 local control prevents claiming that all h>0 bad
places are locally trivial.

Do not confuse highest-layer support, eta ramification, beta ramification,
and H(C). The n<=3 theorem needs COMPLETE H(C) subset U. Arbitrary outside
high primes may reopen deeper beta support. Depth1, general depth2, unrestricted
support, independent proof audit, CM nonboundary points, three higher Hilbert
levels, full signature and full Beal remain separate unresolved obligations.
