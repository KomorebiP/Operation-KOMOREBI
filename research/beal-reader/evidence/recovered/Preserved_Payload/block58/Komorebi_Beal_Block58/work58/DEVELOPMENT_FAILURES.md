# Failures, corrected strengthenings, and nonclaims

1. A source-inspection shell command used a nonexistent *counts*.py glob.
It returned status2 after successful extraction. The exact discovered file
frobenius_certificate.py was then read. No arithmetic run depended on the glob.
2. The broad web searches for two Milne dependencies returned irrelevant
results. They were discarded. The author-hosted PDFs were opened directly and
the relevant theorem pages were rendered. No claim uses the irrelevant hits.
3. A rank-four congruence plus Weil bounds does NOT force the required scalar
precision. The exact2549 Weil polynomial with tau=-47+49phi is retained as a
counterexample to that shortcut. The valid lemma uses the actual rank-two trace.
4. Neither a new divisor nor eta=1 proves a contradiction by itself. The depth
bound uses the explicitly complete H(C) hypothesis; the highest-layer theorem
uses the explicitly complete highest-layer conductor.
5. Broad exploratory counts at79,89,101,109 and extra row probes were run while
selecting the smallest useful tests. They are NOT promoted to arithmetic
claims in this release; only41,59 and the separately proved2549 criterion are
in the released theorem scope. Exploration source/output is retained separately,
marked unverified for publication and containing original working paths.
6. No new Lean compilation or independent mathematical review. All historical
failures remain in the unmodified nested predecessor archives.
