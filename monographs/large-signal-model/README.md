# Realization Calculus: Large Signal Model

Mathematical foundations for realization, refinement, predictive closure and learning with certified probability domains.

This release combines the complete mathematical volume, its verified Lean companion, scientific reference examples and GitHub repository support. All **87 registered propositions have complete Lean mappings** under the assumptions recorded in the coverage guide.

## Start here

- [Read the complete monograph](Monograph/build/Realization_Calculus_Large_Signal_Model.pdf).
- [Explore the theoretical atlas](Visual_Companion/build/Realization_Calculus_Large_Signal_Model_Theoretical_Atlas.pdf).
- [Read the Lean guide](Lean/LEAN_GUIDE.md) and [exact proposition coverage](Lean/COVERAGE.md).
- [Inspect the accepted execution](Lean/verification/current/report.json) and [current status](Lean/CURRENT_STATUS.json).
- [Run the reference examples](Reference_Laboratory/REPLAY_README.md).
- [Read the release notes](RELEASE_NOTES.md) and [contribution guidance](CONTRIBUTING.md).

## What is checked

| Item | Accepted result |
|---|---:|
| Registered proposition mappings | 87 complete |
| Partial or unformalized registered propositions | 0 |
| Mathematical Lean modules | 254 |
| Named source declarations | 4,454 |
| Named source theorems | 2,887 |
| Compilation targets, including the root | 255 |
| Individual module kernel replays | 254 |
| Isolated mathematical rejection controls | 183 |

The accepted execution also includes a full named-declaration axiom audit, exact rational executable examples, 145 metadata checks, 15 lexical guard cases and 33 diagnostic-classifier cases. The only permitted logical axiom dependencies are `propext`, `Classical.choice` and `Quot.sound`.

A complete mapping concerns the registered proposition's stated scope. Statistical model assumptions remain explicit hypotheses. The coverage count does not assert formalization of every surrounding prose sentence or empirical validation of a generating model.

## Repository layout

| Directory | Contents |
|---|---|
| `Lean/` | Immutable checked source, guides, coverage, history and source-bound verification receipts |
| `Monograph/` | Complete publication, corrected editable body, figures, fonts and reproducible publication builder |
| `Visual_Companion/` | Specialized theoretical atlas, vector diagrams, exact rational examples and proposition-to-proof navigation |
| `Reference_Laboratory/` | Worked scientific examples, exact data, original replay instructions and retained results |
| `.github/` | Pinned GitHub workflows and issue and pull-request templates |
| `docs/` | Verification boundaries, release provenance and distribution guidance |

The current visual companion is the atlas in `Visual_Companion/`. Earlier reading guides and visual notes under `Reference_Laboratory/` are preserved historical companions. Their edition-specific audit and proof-kernel statements describe those earlier checkpoints. See [reading order](docs/READING_ORDER.md).

## Check the delivered Lean source

Use Python 3.12 or later. The following checks need only the Python standard library:

```bash
python3 Lean/scripts/verify_hashes.py
python3 Lean/scripts/check_metadata.py
python3 Lean/scripts/test_source_scan.py
python3 Lean/scripts/test_negative_control_classifier.py
```

Run the pristine inventory check before creating build objects or new reports under `Lean/`. The GitHub quick workflow uses a checkout-aware integrity check for tracked distribution files.

For complete Lean verification, restore the pinned portable runtime described in [PORTABLE_LEAN.md](Lean/PORTABLE_LEAN.md), then run:

```bash
python3 Lean/scripts/verify.py --kit /absolute/path/to/portable-kit --out verification/new-run --timeout 900
```

The verifier checks compiler and dependency pins, rebuilds every mathematical module with warnings treated as errors, audits named declarations, replays each module in the kernel and checks all isolated rejection controls. Some exact certificate files take several minutes. See [verification guidance](docs/VERIFICATION.md).

## GitHub workflows

The `.github` directory is part of this release, including the workflows and contribution templates. Quick checks run on pushes and pull requests. Full verification is available through manual dispatch and prepares the pinned environment before invoking the full checker.

The delivered mathematical verification ran locally in the pinned environment. The included workflows have been reviewed and checked locally; their hosted GitHub execution will occur after upload. No hosted CI badge is presented as evidence of a run that has not occurred.

## Publication and licensing

Original project code, documentation, manuscript text and original figures are released under the [MIT license](LICENSE). The P052 font files have separate terms preserved in [third-party notices](THIRD_PARTY_NOTICES.md). Runtime binaries and upstream dependency source trees are supplied separately.

Public attribution uses the pseudonym **Komorebi P.** [CITATION.cff](CITATION.cff) supplies citation metadata. [AI_USE.md](AI_USE.md) records the human and AI collaboration separately from the mathematical exposition.
