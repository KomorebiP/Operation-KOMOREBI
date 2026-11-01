# Polyphase and FIR tap split: scope and self-review

30 October 2026. Same-assistant mathematical self-review and proofreading of
the new section **Split an FIR filter into polyphase taps**. This is separate
from the retained reviews of the rest of the Euler derivation. It is not an
independent review, a Lean execution, a performance comparison, or a novelty claim.

## Mathematical contract

The sequence is `a(n)=E_(2n)`, with the signed sech convention already defined
in the page. The operator is a finite **forward** filter
`y(n)=sum h[r]*a(n+r)`, for `n>=0` and a nonempty finite tap list. The phase
shift sends `b(q)` to `b(q+1)`. The displayed filter has taps `(1,-2,3,1)`.

For an even output index, an even tap selects `a0(q+j)` and an odd tap selects
`a1(q+j)`. For an odd output index, those selections become `a1(q+j)` and
`a0(q+j+1)`. Reindexing the finite sum proves the displayed two-by-two phase
law. No convergence assumption is needed. The lower-left advance belongs to
this forward-shift convention; it must not be copied unchanged from a delay
convention or the earlier formal-series multiplication matrix.

The first four direct outputs are `-43,1191,-46239,2548371`. The two phase
contributions are respectively `(16,-59)`, `(1375,-184)`, `(4160,-50399)`, and
`(2699995,-151624)`. Omitting the advance gives the incorrect first odd output
`-181`, rather than `1191`.

## Implementation and finite evidence

[The standalone program](../../examples/euler_polyphase_taps.py) generates signed
Euler values by the integer cosh reciprocal recurrence. One implementation
filters complete signal windows directly. The other splits the input and tap
lists and computes the two phases with separate index expressions. It
interleaves only the outputs for which the full declared tap window exists.
There is no padding, periodic extension, or floating-point arithmetic.

The finite assertion and exclusions are in
[polyphase-taps-contract.json](polyphase-taps-contract.json). The bounded
[run manifest](polyphase-taps-002/manifest.json) has `run.status=completed`.
Its [results](polyphase-taps-002/results.json) and
[printed output](polyphase-taps-002/stdout.txt) record:

- 600 comparisons: four signal families, all lengths 0 through 24, and six
  explicitly recorded tap lists, including odd-length filters and zero taps.
- 468 comparisons: every unit impulse at every position in lengths 1 through
  12, for the same six tap lists.
- The displayed arithmetic, its interleaving, the missing-advance control,
  short-input boundaries, and rejection of an empty tap list.

The implementations and finite assertion were verified in these stated
ranges. The general identity follows from the written finite-sum argument,
rather than from the number of passing cases. The tested lists are not all
possible integer filters.

To reproduce the standalone finite assertion with Python 3.10 or later:

```text
python -B examples/euler_polyphase_taps.py
```

For a new result file, add `--output fresh-tap-results.json`. The program
refuses to overwrite an existing result file. The manifest retains the actual
bounded command, Python version, source hashes before and after execution,
elapsed time, and output hashes. It validates with the computation-audit
validator using this checkout as `--root`.

The initial `polyphase-taps-001` run also completed, but recorded the Git commit
as unavailable because the bundled Git executable was outside the runner path.
It is retained as predecessor evidence. The selected `polyphase-taps-002` run
repeated the same finite assertion with Git available and records the base
commit and dirty state alongside the unchanged program hash.

## Proofreading and navigation review

Proofread: the added FIR section, its output block, and the revised introductory
navigation and source links in the Euler page.

- Routine edits: explicit nonnegative indices, forward-shift wording, carry
  description, display punctuation, and distinct meanings of filter and phase.
- Mathematical-token changes to existing formulae: none. The FIR identities
  and numeric example are new material with the derivation above.
- Unresolved issues in this scope: none.
- Coverage: only these changes; earlier proofs and their confidence labels
  were not reassessed.

The reading guide groups all 65 section anchors into seven consecutive parts.
Its default view is collapsed, with direct links to the start, the tap example,
and checks/downloads. The generated part navigation preserves every original
section anchor and mathematical block. Regression tests reject missing,
duplicate, or out-of-order guide destinations and verify the supplementary
program's source-bound publication.

The source-bound `cross-check-008` also completed successfully. It reproduced
the original accepted Euler results and the pinned library comparisons, then
compared the tap program with its selected JSON and the new page output block.
Its evidence record validates with the same validator; the older cross-check
is retained as historical evidence.
