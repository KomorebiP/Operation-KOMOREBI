# Special Functions
## Realization Calculus · Komorebi P.

Open **START_HERE.html** in a browser for the complete reading map, or open the PDFs in **books/** directly. No server or internet connection is needed to read the collection.

## Reading volumes

| Volume | Location | Contents |
| --- | --- | --- |
| Special Functions | `books/Special_Functions.pdf` | 134-page proofread monograph. Five parts, seven chapters, ten proof appendices and 32 vector figures. |
| Expanded Visual Guide | `books/Expanded_Visual_Guide.pdf` | 180 pages, with 171 one-page worked lessons and 171 figure plates across the eight-paper series. |
| Resolution and Coupled Atlas | `books/Resolution_and_Coupled_Atlas.pdf` | 19 pages and 14 computed plates on coupled functions, growth, exact recovery and finite resolution. |
| Packet Realization Core | `series/Komorebi_Special_Functions_Consolidated_Manuscript_v0.1.pdf` | The preserved 38-page consolidated core, including the correction register for the original series. |
| Original Series Collected Reader | `series/Komorebi_Special_Functions_Complete_Reader_v0.1.pdf` | 469 pages: the 38-page core followed by all eight original papers, which total 431 pages. |

The three current reading volumes share the professional monograph design. The reference series retains its original layout and historical labels. The 38-page core is also included at the start of the collected reader, so the two reference PDFs are not disjoint content.

## What is included

`monograph/` contains the corrected book's editable LaTeX and all 32 vector figure assets. `research/` contains the discovery code, exact laboratories, proofs, examples, earlier research records and fresh computation receipts. `expanded_visual/` contains the complete visual-guide sources, 171 PDF/PNG figure pairs, all figure scripts, source data, provenance fixtures and review records. `coupled_atlas/` contains the current atlas source and its fourteen vector plates.

`series/original_releases/` preserves all eight original release archives and the earlier special-function registry. These contain the original manuscripts, code, figures, tables and tests. The registry is context, not a ninth numbered paper. The original archives are unchanged. Read their statements together with the consolidated correction register.

`reports/` contains the monograph proofreading report. `verification/` keeps previous proofread records distinct from the current release checks. The current manifest and checksums identify the delivered files. Superseded top-level visual PDFs and build scratch were removed, not scientific sources or figures.

## Archive repair and evidence

This is the replacement for the truncated earlier download. All current books and scientific source files were recovered and checked against the surviving manifest. Ninety-nine prior manifest-listed records or utilities were absent from the delivered tail. Their exact inventory is retained in `verification/recovery/missing_previous_records.json`; the missing prior-run byte sequences have not been fabricated. The old package verifier was replaced, and prior incomplete run folders are labelled. Fresh archive, build and execution checks are separate from inherited evidence.

## Verify archive contents

After extracting the ZIP, run from this directory:

```text
python tools/verify_package.py --strict
```

This uses the Python standard library. It checks every payload size and SHA-256 hash, rejects unsafe or duplicate paths and tests every preserved ZIP. A passing integrity check is not a mathematical proof.

## Rebuild the reading volumes

Install the dependencies separately as needed. Python 3.12 or later and a TeX distribution providing XeLaTeX are required. The Python versions used in the current checks are pinned in `requirements.txt`; the TeX packages are declared in each manuscript. No fonts or dependency installations are bundled. Each manuscript selects installed fonts with a TeX Gyre fallback. Different fonts or TeX versions can alter line breaks and should be visually checked.

```text
python monograph/build.py
python expanded_visual/build.py
python expanded_visual/validate_guide.py
python coupled_atlas/build.py
```

Each PDF is written below its source directory's `build/` folder. These commands do not overwrite the delivered PDFs in `books/`.

## Reproduce computations

Run without Python's `-O` option, which disables assertions. Existing destinations are refused where a fresh evidence directory is required.

```text
python verify_research.py foundation --output-dir local_checks/foundation
python verify_research.py coupled --output-dir local_checks/coupled
python expanded_visual/reproduce_guide.py --output-dir local_rebuild
python series/reproduce_tests.py
```

The expanded-guide command creates a complete isolated input copy, regenerates all 171 figure pairs, builds the guide and validates all lessons and links. Its inputs include the claim index, authority manuscript, OEIS provenance and convolution source extract. It does not fetch external data. The eight-paper command runs the original pytest suites in temporary extraction directories.

## Verification boundaries

The preceding proofreading records report that the discovery suites passed 25,143 exact assertion statements, 5,602 numerical assertion statements and 74 operational guards. These are finite implementation counts, not counts of independent theorems. The eight original-paper pytest suites passed 148 tests, with no failures, errors or skips. Figure generation and document/navigation checks are additional, separately recorded evidence.

The locally restored Lean environment now checks the unchanged 39-declaration finite core **and 29 new named declarations** for the coupled special-function recurrence, local convergence, tail bounds, and coefficient recovery. The new production module passes warnings-as-errors, exact axiom audits and same-kernel module replay. All five negative controls are rejected. A separate exact regression passes 15,658 rational assertions. This is not a full Lean formalization of the analytic monograph. See `LEAN_STATUS.md` and `formalization/Block01/REPORT.md`.

```text
python tools/verify_coupled_block.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work /tmp/sf-block01
python tools/check_coupled_exact.py --output /tmp/sf-exact.json
```

The three books, their mathematical sources, all original series archives and figures are unchanged from the repaired release. Prior build and figure receipts are inherited, not new reruns in this block. The current block has its own source-bound formal receipts and versioned progress ledger. The books' evidence pages retain their earlier snapshot; the new formal companion records the expanded scope.

## Rights and public-release status

This is the complete technical publication handoff. **No explicit redistribution/reuse license is present in the recovered Special Functions sources.** No license has been invented or silently applied. The rights holder still needs to choose and approve the intended manuscript/code licenses before this can be described as a licensed open-source release. Existing third-party notices and source provenance are retained. See `RIGHTS_AND_REUSE.md` and `RELEASE_STATUS.md`.
