# Self-Improving Intelligence
## Representation, Discovery, and Recursive Revision

**Komorebi P. · Operation Komorebi · v0.6.0 · 8 October 2026**

This is the recursive-acquisition theoretical edition, progressing from v0.3 toward a consolidated first edition. The canonical manuscript is `Self_Improving_Intelligence_v0.6.0.tex` and its compiled PDF. Earlier publications are unchanged.

## What this revision adds

A task-independent equation learner proposes arithmetic identities from finite observations. A local derivation checker admits proved identities. The resulting ordered grammar quotient preserves the original learner's candidate/counterexample transcript while reducing repeated task evaluations. A stronger supplied normalizer and preparation-cost ledger are included as controls.

A separate repair-relative extension uses checked nonnegative cover weights. Streaming search then handles repairs that succeed in several cases without silently reusing a singleton-identification bound. Exact checking detects an invalid old certificate when the repair language changes.

These are executable finite constructions, not neural-agent experiments or a demonstration of unrestricted recursive acceleration. `CLAIMS.md` distinguishes the supplied, generated, proved, and open components.

## Reading and review

- `REVIEW_NOTES.md`: actual review, execution, correction, and rebuilding scope.
- `STATEMENT_INDEX.md`: canonical theorem/proposition numbers and assumptions.
- `CLAIMS.md`: claim boundaries and the supplied/generated interface.
- `SOURCE_MAP.md`: inherited source review plus the three new public foundations.
- `FIRST_EDITION_PLAN.md`: what remains before a scoped 1.0 freeze.
- `CHANGELOG.md`: revision history.
- `lineage/`: preserved predecessor source and evidence records.

## Reproduce

The mathematical programs use Python standard-library exact arithmetic. Matplotlib is needed only to regenerate figures. A normal LaTeX installation including the declared `newtx` packages and `latexmk` is required for the PDF. PyMuPDF and `pdffonts` are used by the optional PDF preflight.

```sh
python code/verify_release.py      # Check the frozen snapshot before any rerun.
python code/run_validation.py     # Reruns all four suites, demonstrations, and audits.
python code/check_computation_record.py
bash build.sh
python code/preflight_pdf.py --renders ./page_renders
```

Selected entry points:

```sh
python code/demo_meta.py
python code/check_meta_models.py
python code/make_meta_figures.py
```

The reference demonstrator freezes the equation library and quotient before evaluating its new target cases. It reports the original capacity-rule reacquisition, nine additional arithmetic targets, finite grammar exhaustion, a stronger-normalizer control, multi-case repair bounds, and certificate invalidation. `meta_synthesis.py` and `weighted_repair_pruning.py` are the new reference libraries.

The validation wrapper enforces a 90-second wall limit for the unchanged first suite and 45 seconds per other subprocess. It is not a memory limit or OS isolation guarantee. Rerunning timed receipts changes their hashes by design. Snapshot verification should be done first.

## Evidence boundary

The document's proofs are conditional prose arguments. The exact tests are bounded implementation checks. No independent peer review, external attestation, comprehensive novelty review, Lean verification, Windows execution, PDF/A, or tagged-accessibility certification is claimed. The archive contains no standalone font files, third-party full papers, private conversation transcript, model checkpoints, or external-service integration.
