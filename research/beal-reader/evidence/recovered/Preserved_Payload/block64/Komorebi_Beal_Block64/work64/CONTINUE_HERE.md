# Continue with Block65

Open Komorebi_Beal_Block64_Common_Frobenius_Conductor_Closure_v6.4.0.zip as the
sole execution checkpoint. It preserves the exact Block63 ZIP and its nested
history. Read README, work64/TARGET_CONTRACT, REPORT, PROOF_BOUNDARY, THEOREM_INDEX,
GAP_LEDGER, every work64/notes/*.md, source_records/SOURCE_CHECK, DEVELOPMENT_FAILURES
and VERIFICATION. Cleanly extract and replay:

    python -B verify.py --replay-predecessors --report ../Block64_Replay.json

Keep bytecode writes disabled and do not modify the predecessor extraction.
Timeouts are inconclusive. No new Lean certificate or independent reviewer.

Authoritative boundary:
- Both alpha=(+/-3w,4,1), beta113/617/883 tuples are EXCLUDED at281, with BOTH
  good and bad reduction covered. G281={+/-3w,4+/-3w}, whereas they require3+/-4w.
- The entire n1 beta conductor
  W64={43,113,127,197,337,463,547,617,883,953,1373,1667} is excluded.
  Sixteen candidates survive old tests before281; preserve them as controls.
- At split primes use a SINGLE actual quartic's correction set for both products.
  delta'=phi^2 delta justifies the finite-curve comparison, NOT a global semilinear
  Tate-lattice map or a base/coefficient radical identification.
- Adding743 yields6 uncoupled and2 coupled survivors. The coupled survivors are
  alpha=(+/-w,6,1), beta support547/743 with inertia(5,1). Their rational-test
  values at(71,29,491,43,211,239,281) are(0,0,1,3,3,4,0). They are not actual
  global Frey realizations. Additional period-unit/fixed-prime conditions remain.
- The full local13 zero value supplies no independent equation in the descended
  all-inert q=1 mod7 conductor regime; gamma(Frob13^2)=0 automatically.

Next substantive target: an ACTUAL common-representation constraint on the
547/743 tuples, or a support-uniform consequence of the paired Frobenius rule.
New test primes must be outside the stated beta ramification or handled with
ramification explicitly. Cover good AND bad cases; a new divisor is not a
contradiction. Add every newly allowed conductor column. Do not impose ordinary
eta reciprocity on chi^-1 beta.

The nonzero unit coefficient and13|C remain unconditional within the retained
conditional branch. The old local Frey positive families, smoothing-unit tests,
complete conductor/E(C)/H(C) distinctions, and all prior proof boundaries remain.
Unrestricted supports, whole reducible branch, CM/higher Hilbert levels, full
signature, full Beal and independent upstream mathematical review remain open.
