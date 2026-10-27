# Paper VII — complete sources with a visual appendix

**Author:** Komorebi P.  
**Selected formal checkpoint:** v0.6.0, finite proofs complete.  
**Editorial addition:** 28-page visual appendix, 12 September 2026.

## Read

`reading/Paper_VII_With_Visual_Appendix.pdf` has **60 pages**:

- The 25 original manuscript pages, unchanged.
- The seven-page v0.6.0 finite-completion supplement, unchanged.
- The 28 new appendix pages, labeled V-1 through V-28.

The formal release deliberately preserved its original manuscript and supplied
corrections in supplements and ledgers. In particular, retain both invertibility
assumptions in the Feshbach theorem. The appendix states the corrected assumptions,
not an unconditional version. The combined edition's bookmarks and source-line
links navigate to the corresponding preserved passages.

`reading/Paper_VII_Visual_Appendix.pdf` is the standalone appendix.

## Folder map

| Folder | Content and authority |
|---|---|
| `original_snapshot/` | All 586 files of the selected v0.6.0 handoff: 25 current Lean modules, prior sources, theorem ledger, compiler/axiom records, manuscript, supplements, verification software and pins. Preserved byte-for-byte. |
| `original_companion/` | All 68 files of the separately recovered July 2026 original numerical release: manuscript TeX, 19 PDF/PNG figure pairs, Python library, tests, raw results, table and launchers. Its main PDF matches the formal checkpoint's original PDF byte-for-byte. |
| `visual_appendix/` | Editable LaTeX, 26 TikZ plates, Python models and graphics generator, exact checks, isolated build script and dependencies. |
| `related_editorial_v0.5.1/` | Separately retained 31-page proofread editorial sibling, its TeX and review report. Not merged into the current proof count or treated as a replacement for the broader v0.6.0 proof corpus. |
| `editorial_evidence/` | Actual new build/assembly reports, original numerical replay, source preservation, failure/correction records and visual inspection record. |
| `reading/` | Finished standalone and combined PDFs. |

## Reproduce

Run these commands from the extracted bundle root. Verification uses only Python's
standard library. Example and PDF commands require the listed dependencies.

```powershell
python Run-PaperVII.py verify
python Run-PaperVII.py examples
python Run-PaperVII.py build
python Run-PaperVII.py original
```

The three replay commands operate in temporary directories and place outputs in
new `rebuilt_*` directories. They do not overwrite the retained source/evidence
files. `--output-dir PATH` selects a different output directory.

For the manuscript's original formal verification procedure, consult
`original_snapshot/README.md`. Its Lean compiler and Mathlib cache are **not** in
this bundle. No new Lean build was performed for this editorial addition. The
saved runtime pins are Lean 4.34.0-rc2 and Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Actual new checks

The appendix's check script reports **180 checks in total**: 171 positive exact,
symbolic or rational-enclosure assertions and nine deliberate false controls
rejected. These counts include supporting identities and are not theorem counts.
The original numerical companion passed **22 tests**, regenerated all **19 figure
pairs**, and matched all **1,045 numeric fields** in its saved result records.
The original TeX reproduced all **25 pages** after three passes. The verifier
software's **16 regression tests** also passed; that is not a Lean compilation.

All original, supplement and appendix pages retain identical extracted text and
72-dpi renders in the assembled PDF. TeX compilation, internal links and vector
content were checked, followed by visual review. Raw image coordinates only
illustrate the formulas; the exact mathematical evidence lives in the scripts.

## Boundary

The selected saved formal ledger covers 19 finite items and records 323 theorem
declarations in 25 current modules. This editorial addition changes none of them.
The five continuum/physical existence targets remain unproved. The TeX distribution,
Python environment, compiler, Mathlib cache and font files are not bundled.
