# Paper VIII — complete source and visual reader edition

**Packet Operator Algorithms, Exact Compilation, and GPU Realization**  
**Author:** Komorebi P.  
**Formal checkpoint:** v0.6.0, the 392-declaration / 40-module branch with all 56 registered manuscript-proved finite items covered.

## Read

`reading_editions/Paper_VIII_With_Visual_Appendix.pdf` contains **81 pages**:

- the original 45-page manuscript, unchanged;
- the authoritative eight-page sixth-block completion supplement, unchanged;
- the new 28-page visual appendix, with 26 editable vector plates and worked calculations.

The standalone appendix is `reading_editions/Paper_VIII_Visual_Appendix.pdf`. Its gray source lines link to the original or supplement in the combined edition. Bookmarks and page labels distinguish the three parts. Earlier supplements are preserved in the source archive rather than interleaved with the current reading edition.

## Main folders

| Folder | Role |
|---|---|
| `original_snapshot/` | All 725 files of the selected complete formal handoff, byte-for-byte. Includes the 40 active Lean modules, historical sources, all six supplements, recorded axiom/compiler evidence, pins, and the original manuscript package. |
| `original_companion/` | All 132 files extracted from the original manuscript package, byte-for-byte. Includes LaTeX/BibTeX, the Python implementation, vector figures, numerical tests, and historical benchmark corpus. |
| `visual_appendix/` | New LaTeX, exact mathematical models, Python checker, editable TikZ plates, figure generator, and isolated PDF build/assembly script. |
| `editorial_evidence/` | Current editorial checks, original test and figure replay, fresh numerical recompression mirror, original TeX comparison, and development corrections. These are not new Lean proofs. |
| `reading_editions/` | Combined and standalone PDFs with the build/assembly audit. |

## Verify or rebuild

Run these commands from the extracted bundle root. `verify` uses only the Python standard library.

```powershell
python Run-PaperVIII.py verify
python Run-PaperVIII.py examples
python Run-PaperVIII.py appendix
python Run-PaperVIII.py original-tests
python Run-PaperVIII.py original-figures
python Run-PaperVIII.py original-paper
```

Except for `verify`, outputs go under `rebuilt/` by default. Builds operate in temporary copies; they do not overwrite shipped source trees. An optional `--output-dir PATH` selects another output directory. Dependency versions actually used are in `visual_appendix/requirements.txt` and the audit. `original-figures` replots saved benchmark rows; it is not a GPU benchmark run.

## Formal boundary and reproducibility

The source release records 392 named theorem declarations (373 Paper VIII and 19 reused foundation), plus 66 separately counted construction audits. The four classical entries remain tracked separately. Small-core optimality is proved from ordered thin-SVD equations; general SVD existence, a floating-point QR/SVD algorithm, and canonical singular-values API identification are not silently included.

**Lean was not rerun for the visual addition.** To run the inherited Lean verifier, follow `original_snapshot/README.md` with the separately provided Linux/WSL portable kit. The compiler and Mathlib cache are not in this ZIP. The source release does not ship local compiled interfaces. The pinned formal environment is Lean 4.34.0-rc2 and Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The new exact checks validate particular rational, complex-rational, symbolic, and finite-enumeration examples. The numerical recompression replay uses declared floating-point tolerances. No device timing, new generic matrix exponent, numerical algorithm verification in Lean, or unrestricted structure-discovery result is claimed. No installed TeX distribution, Python environment, compiler, Mathlib cache, or raw fonts are bundled.

## Preservation and integrity

`PRESERVATION.json` identifies every original file and its hash. `MANIFEST.json` covers all payload files except itself and `SHA256SUMS.txt`; the latter also records the manifest hash. These are consistency checks, not independent authenticity signatures. Extra files created by a later replay are allowed. Source statements and historical audit records are retained, not retrospectively rewritten.
