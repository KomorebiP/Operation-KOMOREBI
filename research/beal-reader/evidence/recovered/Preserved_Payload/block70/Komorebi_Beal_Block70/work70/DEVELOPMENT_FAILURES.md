# Development failures and unsuccessful strengthenings

## Corrected mathematical implementation error
The first draft of the new target-specific acceptance condition allowed bad
reduction only when beta(F)=0. This was too restrictive: beta(F) can be nonzero
while alpha is locally zero, so BOTH products still vanish. At2269 this incorrectly
rejected valid necessary-system candidates. The first exploratory output gave six
individual survivors there; the corrected output gives sixteen. The affected scan
was stopped, both implementations were corrected before release, and all selected
primary/secondary outputs were rebuilt. REJECTED_ZERO_PRODUCT_DRAFT.zip retains
the erroneous source/output as explicitly UNACCEPTED history. A new negative control
checks that the wrong flag is rejected. No released conclusion uses the bad draft.

## Unsuccessful stronger conclusions
The three selected tests leave eight, not zero. Additional corrected exploratory
tests2339,2381,2521,2549,2591 leave those eight intact. The latter prime rejects two
of the original18, but they were already excluded by the selected tests.
A complete bounded exclusion has therefore not been obtained.

An unrestricted finite homogeneous character-sieve exclusion is false in the
specified zero-or-good model. The explicit nonzero21-prime vector annihilates all
24 fixed test rows. This is not a counterexample to Beal or to an actual global
representation theorem with stronger inputs.

## Engineering and evidence
The sorted eligible-pair cursor replaced repeated set minima without changing
representative order. The earlier source and optimization record are retained.
The current Block69 default replay completed and its observed logs are preserved.
No new full historical-chain replay is claimed unless separately requested and
observed. All future timeouts are inconclusive. No independent mathematical review
or Lean execution occurred.

A documentation-packaging helper initially matched both count JSONs and their run
metadata, causing a KeyError before writing the new documentation. It was changed
to distinguish the two schemas and rerun. No arithmetic output was modified.
