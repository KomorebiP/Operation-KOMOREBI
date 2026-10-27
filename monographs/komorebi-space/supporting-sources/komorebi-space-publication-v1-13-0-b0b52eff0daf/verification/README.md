# Verification scope

`EDITION_VERIFICATION.json` records the source identity, environment, accepted proof coverage, and PDF hashes. `LEAN_THEOREM_MAP.json` gives 69 selected declarations discussed in the Lean guide. These counts distinguish explicit theorem/lemma declarations from the larger compiler export.

The publication source is byte-identical to the accepted production Lean source. Package metadata was updated to the publication version, and the dependency manifest root name was aligned with the package configuration; dependency revisions are unchanged.

The separate Technical Record contains the accepted full verification, original controls and command logs, editorial comparisons, compilation logs, visual-review coverage, example runs, and archive checks. The finite examples and visual reviews support only their recorded scopes.
