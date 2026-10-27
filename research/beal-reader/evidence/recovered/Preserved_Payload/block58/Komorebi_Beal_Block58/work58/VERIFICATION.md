# Verification contract, Block58

Python3.10+, standard library only:

    python verify.py --replay-predecessors --report ../Block58_Replay.json

The startup Block57 replay passed, including the selected older chain.
The verifier checks exact payload membership and SHA256, pinned source leaves
inside nested original archives, and byte-identical copied arithmetic modules.
All new outputs are regenerated in a temporary scratch copy and compared in full.

Primary:104 curve orbits, BOTH degree-one and degree-two counts;5062 memberwise
admissible pairs;15 rows at12 conductor places; exact full-column determinant.
Independent:5062 DIRECT degree-one and5062 DIRECT degree-two counts without
orbit reduction;5062 polynomial-gcd smoothness checks;180 direct seventh-power
symbols in different residue-field bases; independent determinant and2549
arithmetic, including all18 generic quartic-only controls.
Algebra:2940 trace/discriminant identity cases;4902 complete small principal-unit
root tests; exact2549 bounds and a retained same-coefficient-field counterexample
to replacing scalar precision with quartic congruence. No2549 curve counts.

Two altered-arithmetic controls must be rejected: an N1 count and a new residue
row. A separate extracted-archive audit also tests payload corruption rejection.
The report records observed processes, commands, Python/platform, timings, exit
codes, stdout/stderr, script/result hashes, and inputs before/after execution.
Default per-job wall cap180seconds; no extra CPU or memory cap beyond the current
environment. Nested timeout status is inconclusive. Reports are external to the
immutable package, so final artifact checksums are not circular.

No new Lean compilation, no independent mathematical reviewer, no upstream
geometry re-proof, and no inference from bounded computations to full Beal.

The observed development replay passed all new certificates and both altered-arithmetic rejections. Its selected predecessor replay was NOT_REQUESTED; the separate successful startup record covers that phase. Its hashes describe its own earlier snapshot. The final extracted-ZIP replay requests the full selected chain again and is authoritative for final bytes.
