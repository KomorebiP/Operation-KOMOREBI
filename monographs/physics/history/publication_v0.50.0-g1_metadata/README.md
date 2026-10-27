# Komorebi Physics
## Continuum, Geometry and Refinement

Open `Komorebi_Physics.pdf` for the complete book. The PDF has **570 pages**: one unnumbered cover, seven preliminary pages numbered i–vii, and 562 pages numbered 1–562. `Komorebi_Physics_Design_Preview.pdf` contains twelve selected pages with their original printed folios.

The book uses a coordinated navy, dark teal, and copper identity, a serif reading face, quieter sans-serif navigation, and uniform treatment of section headings, chapter openings, captions, and mathematical statements. It preserves the seven research themes and their verification boundaries. Local equation, theorem, figure, and section numbers belong to the named treatment in which they occur. Global folios and PDF bookmarks navigate the whole book.

## Package map

- `source/`: editable LaTeX texts, typography styles, figure assets, and retained data.
- `compiled/`: eighteen source-built component PDFs and final TeX logs.
- `book/`: front matter, part leaves, page mapping, reading text, assembly specification, and navigation checks.
- `audit/`: design and preservation checks, build records, complete-book render contact sheets, and the retained earlier editorial records.
- `formal/`: byte-preserved baseline archive, checked generator source, API and axiom audits, mutation controls, and the offline replay launcher. The earlier uncompiled scaffold is retained only under `audit/prior_formal/`.
- `reference_record/`: selected earlier computation and provenance records, unchanged.

Historical filenames and compiler identifiers remain in the supporting records for traceability. They are not new verification claims. Original project material is now openly licensed under the grants in `LICENSE`. Historical source archives remain byte-identical; third-party rights are unchanged.

## Rebuild

Required: Python with `requirements.txt`; a TeX installation providing `xelatex`, `pdflatex`, and `kpsewhich`; the packages imported by the preambles; separately installed URW Base35 OpenType, Latin Modern, TeX Gyre, and Palatino-compatible mathematical fonts.

The XeLaTeX documents explicitly select the P052 and Nimbus Sans OpenType files to avoid substituted bold faces. Set `source/monographs/font-location.tex` to your local URW Base35 font directory. Its Linux default is `/usr/share/fonts/opentype/urw-base35/`. Latin Modern Math and Mono are resolved by the TeX installation. The PDFLaTeX sources use their installed TeX font packages. The outer-book script discovers TeX Gyre Pagella and Heros metric/program files through `kpsewhich`. Font files are **not** distributed in this package.

Run from the package directory:

```text
python build_documents.py
python assemble_reading_volume.py
python audit_design.py
python render_design_audit.py
```

The first command makes three passes for each component; a nonzero status means at least one component failed. To rebuild a subset, pass filename substrings, for example `python build_documents.py Physics_Dirac_Monograph`. Assembly preserves source vector pages and rebuilds their internal links in the global page map. The audit checks final logs, destinations, text bounds, and document structure. The render command checks every page using PDFium and writes contact sheets.

For a fresh source-preservation comparison, pass an extracted predecessor source directory to `audit_design.py`. Without that optional baseline, the audit does not invent a new source comparison. The current source comparison is `audit/closeout_2026-10-21/source_preservation.json`. Older design comparisons are historical records. The older `audit_with_original_sources.py` belongs to the preceding editorial project and is not needed for a standard design rebuild.

Layout reproduction depends on matching the installed TeX/font environment. Byte-identical output across operating systems or compiler installations is not promised. The numerical experiments and Lean proofs are not rerun by a document build. Some historical experiment scripts also require external data or their original directory tree.

## Formal replay

The checked extension is in `formal/generator/`. From the package directory, use an existing exact-pin Linux x86-64 or WSL2 portable Lean kit:

```text
python formal/generator/replay_generator.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work-dir /path/to/new-physics-replay
```

The work directory must not already exist. The script verifies the baseline and overlay hashes, checks compiler and Mathlib pins, extracts a new project, attaches dependencies without a download, and writes separate gate records. `--prepare-only` checks setup without claiming compilation. The kit is not embedded in this publication ZIP. Do not replace its exact pins silently.

## Verification boundary

The free-field strong generator now has a compiler-checked implementation: 37 named theorems and two definitions. The exact physical differentiability domain, generator value, invariant domain, Hamiltonian commutation and strong Schrödinger equation are covered. The formal link to an abstract unbounded spectral-calculus API, centered resolvent convergence, and quadratic-rate estimates remain outside this certificate. Their written mathematical proofs remain in the book.

The baseline operator target was rebuilt. Thirteen generator/compatibility gates passed, including a separate-path source check and imported-environment kernel replay. Axiom dependencies for all 39 named declarations were checked. Five supplied computation suites were rerun. This does not claim a compiler bootstrap, a rebuild of all Mathlib from source, or a fresh cumulative audit of every historical physics module. The old generic aggregate root remains historical; `formal/generator/PhysicsRelease.lean` identifies the current explicit imports.

Five modified component documents were rebuilt in three TeX passes. All final component logs were inspected and all 570 book pages rendered. Original explicit proof environments are unchanged. The verification-scope diagram was updated, not a numerical figure. This is a focused scientific and publication audit, not an independent line-by-line specialist review of every chapter or bibliography.

See `RELEASE_VERIFICATION.md` and `.json` for the accepted results, trust boundary, preserved failures, and remaining obligations. `PROGRESS_LEDGER_v0.50.0-g1.md` gives the exact restart point. `PACKAGE_MANIFEST.json` records file identity, not mathematical validity.
