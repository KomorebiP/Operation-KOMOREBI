# Continue with Block63

Open Komorebi_Beal_Block62_Trace_Product_Depth_One_Exclusion_v6.2.0.zip as the sole
execution checkpoint. It preserves the exact original Block61 ZIP and all nested
predecessors. Read completely before editing:

README.md; work62/TARGET_CONTRACT.md; work62/REPORT.md; work62/PROOF_BOUNDARY.md;
work62/THEOREM_INDEX.md; work62/GAP_LEDGER.md;
work62/notes/TRACE_PRODUCT_IDENTITY.md; work62/notes/TWISTED_TRACE_DATA.md;
work62/notes/DEPTH_ONE_EXCLUSION.md; work62/notes/LOW_CONGRUENCE_EXTENSION.md;
work62/notes/ARITHMETIC_CONSEQUENCES.md; work62/notes/SELF_REVIEW.md;
work62/source_records/SOURCE_CHECK.md; work62/DEVELOPMENT_FAILURES.md;
work62/VERIFICATION.md.

Cleanly extract and run:
    python verify.py --replay-predecessors --report ../Block62_Replay.json

## Authoritative new results

At actual n1 and Q=1 mod7, with beta unramified at the test place,
(tr_O(F)-Q-1)/7 = alpha(F)*beta(F) mod7. At good primes use the actual trace
correction set; at bad primes use0. Do NOT force29 or491 bad at depth one.
Only71 supplies the initial unconditional local-zero row in this block.

All depth-one beta ramification contained in
Splus={43,113,127,197,883,1373,1667} is now IMPOSSIBLE. Arbitrary extra C divisors
unramified in beta are allowed. The base four-prime proof leaves9 tuples after
29,43,491, then1 after211, then0 after239. Preserve these intermediate survivors.
The added low-h43/113/127 cases are eliminated with new twisted columns, not with
an unramified43 test at a ramified43 place.

With U={97,197,293,491,587,883,1373,1471,1567,1667}, V=U union{43,113,127},
actual n1 beta must ramify outside V. Under COMPLETE H(C) subset U the remaining
supporting q outside V necessarily has h1, v7(v_q(C))=0, and phi and75A seventh
power residues. That old entire H(C) class is NOT eliminated: low-h outside
primes remain possible.

At ANY n with FULL eta_n=1, beta must ramify outside V. The n>=2 part extends
the old three forced-bad rows and incompatible197/1667 ratios; it does not follow
from half precision alone. Define E(C) to include ALL variable divisors with
norm1 mod7 and phi seventh-power residue. COMPLETE E(C) subset V is excluded in
the retained branch, because nonzero highest eta needs h>=2 and then U would
contain its support. No bound on arbitrary E(C) has been proved.

## Next substantive target

Pursue outside-V low-h depth-one ramification with the correctly twisted beta
columns, or a support-uniform same-representation trace/reciprocity relation.
A new beta ramification prime can alter all global Frobenius values. Do not
reuse the four-prime rows without adding that column. A newly forced divisor
alone is not a contradiction. Never identify base-field sqrt5 with the
coefficient-field root used for trace corrections without a comparison map.

Preserve the actual local Frey families and complete period criterion. They
are local positive controls, not global solutions. Larger depth-one conductors,
general n2 and higher support, independent upstream review, CM nonboundary points,
higher Hilbert levels, full signature and full Beal remain separate obligations.
No new Lean compilation or independent mathematical reviewer is in this checkpoint.
Timeouts are inconclusive.
