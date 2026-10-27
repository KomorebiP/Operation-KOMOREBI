# Verification protocol and observed pre-release evidence

The predecessor was extracted cleanly. Its first replay was contaminated by
our concurrent exploratory bytecode writes and failed its corruption test.
That failed execution is preserved. The second, clean extraction completed
Block62 and its declared selected predecessor chain with returncode0, in
204.20163798332214 seconds. Original predecessor bytes were never changed.

The five new production output JSON files were generated successfully before
packaging: count83, jacobian83, independent83, conductor, independent_conductor.
The independent83 program checked6806 direct pairs in BOTH extension degrees,
6806 smoothness gcds,77 divisor additions, all6888 nonzero field inverses,
the exact order49 witness and its alternative-basis scalar ladder. The independent
conductor program checked390 direct seventh-power symbols and six cyclotomic
norms. It found zero strict-W survivors, three without the nonzero-unit
restriction, and two after adding617. Its strict-W enumeration inspected
119808 coefficient/vector pairs; the control enumerations are separately
recorded, not mislabeled additional representations.

The release verifier rehashes every payload, pins ten selected nested input
leaves, removes every new expected result in a fresh scratch copy and regenerates
them. It compares COMPLETE JSONs, not only PASS flags. It also requires rejection
of altered group arithmetic, point counts, twisted columns, claimed survivor
counts and payload bytes. With --replay-predecessors it executes the preserved
Block62 verifier and its declared selected chain. It does not claim to reprove
every historical theorem or execute unselected research branches.

Final extracted-ZIP execution timing, exit codes and archive-member audit are
recorded OUTSIDE the immutable ZIP, avoiding self-referential hash statements.
A successful process or large finite count is not an independent mathematical
review. No Lean certificate is created. Every timeout remains inconclusive.

Observed new-block development replay: PASS in45.295737089999875 seconds,
including all five complete JSON regenerations and all five malformed-input
rejections. The execution record is verification/DEVELOPMENT_REPLAY.json.
The final ZIP is verified again separately, with the predecessor flag enabled.

The first final full replay reached a successful predecessor process but the
new wrapper rejected its PASS_DECLARED_CHECKS status because it expected PASS.
The failed status-parser record and exact draft hash are retained. A rebuilt
archive with the corrected exact status comparison is replayed anew; the final
external report, not the superseded draft report, is authoritative.
