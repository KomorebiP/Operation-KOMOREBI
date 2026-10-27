# v0.40 release infrastructure preparation

Prepared independently of the mathematical development. The source tree and its local Lean build were not cleaned or modified by preparation. `FullAudit.lean` and `THEOREM_INDEX.md` are generated only after the source freeze.

- Verified all 186 inherited non-audit AVOC modules against the exact v0.39 release ZIP, SHA-256 `298b6daed3875697a59c15caa6d8546c9cfe2d30aa8cfbc4aab0275ad63be44c`.
- Added relocatable v040-only helpers, explicit `AVOC_LEAN_KIT` selection, warnings-as-errors invocation evidence, current direct-import hashes, bounded dependency-aware builds, and advisory locks preventing overlapping v040 build/prepare/audit processes.
- The theorem inventory handles Lean nested comments and preserves exact inherited private-name membership. A generated environment-constant collector audits explicit private helpers.
- The negative checker requires an ordinary Lean error exit (1), a substantive proof diagnostic, and current source/import/log hashes. Setup, parser, missing-typeclass, timeout, and crash failures do not count.
- The final collector independently enumerates current build targets, theorem inventory, source tokens, and negative files; validates bounded-oracle manifest hashes and canonical-result equality; requires current independently reviewed source hashes; and checks all five inherited executable regression cases.
- The inherited regression runner redirects old evidence destinations into a unique v0.40 directory, includes the calibration `--lean` case, and records original/adapted source and output hashes. Historical v0.39 evidence remains untouched.
- The package command runs the release gate first, then checks ZIP CRCs, exact payload membership, every archived byte hash, and absence of source changes while packaging.

Preparation checks passed: Python syntax compilation; nested-comment/string masking; allowed-axiom exact membership; duplicate and missing declaration rejection; and overlapping-lock rejection.

Review findings corrected before execution:

1. The first collector draft permitted empty JSON objects to skip truthiness-guarded evidence gates. Required evidence now rejects empty or wrong-type JSON before any gate can be skipped. Only the named inventory and build-order inputs accept nonempty lists; other evidence requires a nonempty dictionary.
2. The first negative checker draft admitted arbitrary nonzero process exits. It now requires Lean exit 1 so a crash following a proof diagnostic cannot count as a substantive rejection.
3. Runtime version smoke inspection established that Lean's version banner uses a comma after the version; the pin check matches that actual banner boundary.

These are infrastructure development corrections, not mathematical counterexamples or proof results.

4. The first full source scan treated the domain action/definition name `admit` as a proof shortcut, producing false positives in unchanged inherited modules. Inspection confirmed ordinary action constructors and admission functions. The scanner now recognizes tactic-position `admit`; the exact axiom audit independently rejects any proof using `sorryAx`. The initial scan report is retained as `release_source_scan_initial_false_positives.json`.

The shortcut scanner is a selected forbidden-token/tactic-pattern scan, not a complete Lean parser. In particular, its `admit` detection does not enumerate every tactic combinator. Warnings-as-errors and the exact theorem-by-theorem axiom audit are the substantive proof-admission safeguards.
