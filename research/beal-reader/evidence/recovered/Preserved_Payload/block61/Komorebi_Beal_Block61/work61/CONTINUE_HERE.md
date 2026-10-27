# Continue with Block62

Open Komorebi_Beal_Block61_Twisted_Opposite_Depth_Two_Closure_v6.1.0.zip as the
sole execution checkpoint. It preserves the exact Block60 ZIP and all nested
predecessors. Read completely before editing:

README.md; work61/TARGET_CONTRACT.md; work61/REPORT.md; work61/PROOF_BOUNDARY.md;
work61/THEOREM_INDEX.md; work61/GAP_LEDGER.md;
work61/notes/OPPOSITE_FROBENIUS.md; work61/notes/TWISTED_DESCENT.md;
work61/notes/TWISTED_RECIPROCITY.md; work61/notes/DEPTH_TWO_CLOSURE.md;
work61/notes/SELF_REVIEW.md; work61/source_records/SOURCE_CHECK.md;
work61/DEVELOPMENT_FAILURES.md; work61/VERIFICATION.md.

Cleanly extract and run:
    python verify.py --replay-predecessors --report ../Block61_Replay.json

## New authoritative boundary

At actual n2, beta is locally ZERO (not just unramified) at both places above
29,71,491. This follows from eta2=1, exact toric trace/determinant, natural
residual inertia and phi's failure to be seventh power at those places.

A beta ramified only over S={197,883,1373,1667}, split at7, descends as a
chi^-1 COHOMOLOGY CLASS to Q. This is not semilinear Tate-lattice descent.
The correct twisted ray matrix over Q(zeta7), with rows29,71,491, is
[[4,2,6,1],[6,2,0,5],[3,6,1,6]]. It has rank3, not4; its k-kernel is
k*(1,0,0,3). Every nonzero vector forces197 and1667 ramification. These require
incompatible actual Kummer ratios6 and1. Thus n2 cannot have all beta support
in S, even with arbitrary extra C divisors unramified in beta.

Combining the old exclusions gives:
    COMPLETE H(C) subset U => n1,
    n2 => beta ramifies at some prime outside U,
    U={97,197,293,491,587,883,1373,1471,1567,1667}.

The four local49-torsion Frey families remain valid; no individual supporting
prime is excluded for a larger beta conductor. Do not reopen the all-S n2
branch by presenting those local families or the nonzero ray line again.

## Next target

Pursue depth1 with a genuinely justified complete allowed beta support, or
a support-uniform chi^-1 constraint for outside-U n2 ramification. At depth1,
29 and491 are not automatically bad: do not reuse their new local-zero rows
without a new argument. At new ramified primes add the correctly twisted
columns; do not impose eta's ordinary character rows on beta.

Preserve all common-alpha, natural local period, multiplicity and fixed-prime
conditions. Full local torsion is not global realization. No new Lean proof
or independent mathematical review is in this checkpoint. Timeouts are
inconclusive. Depth1, general n2, unrestricted high support, CM and higher
Hilbert levels, complete signature and Beal remain separate obligations.
