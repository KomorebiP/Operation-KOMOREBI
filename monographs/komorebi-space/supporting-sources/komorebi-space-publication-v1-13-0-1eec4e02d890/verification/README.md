# Verification scope

`EDITION_VERIFICATION.json` records the source identity, environment, accepted proof coverage, and PDF hashes. `LEAN_THEOREM_MAP.json` gives 69 selected declarations discussed in the Lean guide. These counts distinguish explicit theorem/lemma declarations from the larger compiler export.

The publication source is byte-identical to the accepted production Lean source. Package metadata was updated to the publication version, and the dependency manifest root name was aligned with the package configuration; dependency revisions are unchanged.

The separate Technical Record contains the accepted full verification, original controls and command logs, editorial comparisons, compilation logs, visual-review coverage, example runs, and archive checks. The finite examples and visual reviews support only their recorded scopes.

`VISUAL_GUIDE_REVIEW.json` records the current nineteen-page guide and its sixteen new visual investigations. The files in `visual/` give the recorded checks for the worked values. The 52 generator checks include typography checks; the 23 independent checks concern the declared models and examples. These are finite computational and editorial checks, not new Lean proofs. Run `python3 tools/run_visual_checks.py` from the package directory to regenerate the figure checks. The monograph and Lean guide retain their original bytes.
