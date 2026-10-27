# Paper II open release 1.1.1

**Release date: 20 October 2026**  
**Reading edition: 19 October 2026**  
**Author: Komorebi P.**

This release completes the project license decision and supplies the reviewed
Paper II package for public distribution within its stated mathematical scope.

## Licenses

Original software, Lean sources, scripts, and machine-readable material use
MIT. Original papers, guides, figures, and explanatory writing use CC BY 4.0.
The full terms and scope are in `LICENSE.md`, `LICENSE_STATUS.json`, and
`LICENSES/`. Each reading PDF has an adjacent license notice. The historical
Python wheel has an adjacent complete MIT notice for separate redistribution.

Third-party sources and fonts retain their original terms. The release adds
the complete LPPL 1.3c text and matching upstream Type1, AFM, OTF, and TTF
materials for the eight URW font faces used in the papers. All 24 existing
OTF copies match the pinned upstream files. The AINTLIB source location in
the third-party notice has been corrected.

## Contents

| Reading file | Pages |
| --- | ---: |
| Traditional paper | 80 |
| Visual guide | 26 |
| Lean guide | 51 |
| Total | 157 |

The package also includes editable sources, figures, current Lean sources,
Python examples, replay and review evidence, correspondence maps, and the
versioned closeout ledger.

## Verification

The accepted scope remains 53 of 53 enumerated manuscript proof records under
their displayed hypotheses, with no partial or pending records in that set.
The successful 19 October Lean run contains 75 production modules, 2,112
logical declarations replayed, and nine negative controls.

The 20 October release pass confirmed that all 75 source modules, three Lean
configuration files, 57 audit inputs, seven manuscript chapters, and all three
PDFs retain their reviewed hashes. The existing 48 Python tests passed with
warnings treated as errors, including a fresh finite experiment comparison.

The licensing release does not alter the scientific inputs or increase the
accepted theorem scope. It does not claim a new Lean replay. Exact results,
commands, environment versions, and input hashes are supplied under
`verification/open_release_2026-10-20/`.

## Reproduction and distribution

Start with `READ_FIRST.txt`. Use `REPRODUCIBILITY.md` for current verification,
Python test, strict Lean replay, and PDF build commands. The pinned Linux Lean
runtime is an external dependency. It is not included in this archive.

Run `python3 scripts/verify_package_integrity.py` immediately after extracting
the release to check every included file against the final manifest.
