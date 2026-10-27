# Realization Calculus

*Projectors, Transfer and Arithmetic*

Komorebi P.

Open `output/Realization_Calculus.pdf` for the complete book. `output/Realization_Calculus_Design_Preview.pdf` is a selected-page design tour that retains the book's printed folios. It is not an abridged mathematical treatment.

The delivered book contains **2,759 pages**, including the twelve mathematical chapters, further arithmetic studies, formal companions and a **73-term glossary**.

## Reading the book

The twelve core mathematical chapters appear in chronological order. Worked visual studies accompany their chapters. Repeated visual plates are presented once, with the omitted copies' links redirected to the retained plates. Unique reading routes and substantive introductions are retained.

Further arithmetic studies follow the chapters. The formal companions and Lean reading guides are collected at the back, followed by a linked glossary. Chapter openings, contents, bookmarks and return links connect these reading paths. Plate labels include their chapter, such as **Plate VIII.32**, independently of page numbering.

The build specification records the actual sequence of preliminary matter, editorial openings, selected source pages and glossary pages. Page totals are calculated from that sequence. They are not obtained by appending every original reader or assuming a fixed component length. `book/book_layout_accounting.json` records the selected and omitted page accounting, and `book/page_map.json` records the final locations.

The design follows the Komorebi Physics format with plum headings, mulberry navigation and muted gold accents. Serif text and sans-serif navigation are coordinated across the source-built chapters. Compact visual and formal layouts are retained where they help keep diagrams, examples and code readable.

## Mathematical and editorial scope

This is a bounded editorial review of mathematical prose, references, chapter transitions and reading structure. It clarifies opaque release references, distinguishes current theorem boundaries from historical progress records, and consolidates repeated reader furniture. Source-level reports identify exactly what was reviewed, changed, moved and preserved. They do not claim a new correctness audit of every proof.

The stated hypotheses, conditional conclusions, open problems and formal coverage distinctions remain in force. Expanded prose results can exceed a chapter's Lean coverage. Chapter X's target-family and carrier-recovery witnesses remain separate unless the stated comparison premises are supplied. Chapter XI's Conjecture 66 remains open under its stated contracts. Chapter XII retains its required arithmetic, patching, support, compatible Hecke, classicality and representation inputs.

An additional grammar and prose pass covers the twelve chapters, their formal companions, the retained visual studies, the arithmetic studies and the glossary. It corrects agreement, articles, punctuation, spelling, local references and chapter terminology. Publication font bindings and muted colors are coordinated across the book. Exact journals, coverage records and preservation comparisons are supplied in `editorial/prose_review/`. The subsequent punctuation pass replaces optional semicolons and parenthetical dashes with natural sentence structure, recasts unnecessary compound modifiers, and simplifies formulaic phrasing. Mathematical punctuation, necessary technical compounds and exact source records are retained. Its contextual coverage, exact journals and checks are in `editorial/rhythm_review/`.

Three local technical wording clarifications are recorded separately from routine grammar edits. Chapter V takes the minimum cost among admissible prunings. The tensor packet example in Chapter XI uses length twelve. Chapter IV directs behavior at zeros of reciprocal powers to its existing order and branch conventions. These changes do not supply new proofs or resolve the stated open problems. The later bounded PDF pass also qualifies the original V-style routing labels in Chapter IV while keeping the mathematical glyphs in place. Optional wording that cannot safely fit beside fixed mathematical content is retained and reported.

No new Lean kernel execution, mathematical experiment, GPU benchmark or regeneration of figure data is claimed by the book build. Historical compiler and computation records retain their exact technical versions, dates and limitations where those identify evidence. Historical lists of remaining work are labeled as such. They are not current theorem claims.

The final checks have distinct roles:

- `book/final_pdf_audit.json` checks the assembled pages, source mapping, links, attachments and document geometry.
- `book/book_editorial_audit.json` records preservation and the bounded editorial review.
- `book/final_visual_review.json` records the inspected pages and visual findings.
- `book/preview_manifest.json` binds the design preview to the full book.

All delivery reviews identify the exact PDF SHA-256. Reports about an earlier PDF do not certify a later rebuild.

## References and preserved inputs

Theorem, equation, section and figure numbers belong to the named chapter and treatment. Global folios navigate the book. Original local labels remain available where useful for formal correspondences and source records.

References explicitly labelled **frozen** identify exact original reading editions. All selected original reader PDFs are supplied under `frozen_readers/` and attached to the complete PDF. Use the folder if a PDF viewer does not expose attachments. The final audit checks the attachment identities and embedded-reference destinations.

Editable sources, exact pre-edit backups, scientific figure assets and editorial change reports are included. Some source layouts are retained and adapted through a recorded PDF editing step. The original PDFs remain separately preserved. The full formal research distributions are already retained in their separate durable archives. This publication package does not duplicate those large archives or claim to replace them.

## Package contents

| Path | Contents |
|---|---|
| `output/` | Complete book and design preview |
| `compiled/` | Current display components used by the assembly |
| `frozen_readers/` | Exact selected original reader PDFs |
| `source_i_iv/`, `source_v_viii/`, `source_ix_xii/` | Editable reading sources, original-file backups, scientific assets and component build records |
| `book/` | Reading sequence, page and link maps, glossary layout, adaptation records and final audits |
| `editorial/` | Proofreading journals, preservation comparisons, overlap maps, glossary sources, design reviews and historical publication records |
| `publication_notices/`, `LICENSES/` | Per-paper notices and current project licence terms |
| `scripts/` | Portable package-integrity checker and its provenance |

Generated test PDFs, contact sheets, reproducible review-page renders, Python and TeX build caches, and byte-identical superseded build PDFs may be omitted from the package. Editable TeX inputs, rendered PDFs and verification logs are retained. Their useful source and review records remain. External font programs are not bundled. Font identities and license notices are retained. Earlier authoring scripts and reports are historical records, not the supported rebuild sequence.

## Rebuilding

Use Python 3.11 or later and install the dependencies in `requirements.txt`. Source recompilation also needs the recorded TeX environment and packages, including XeLaTeX, pdfLaTeX, BibTeX and `kpsewhich`. Install URW Base35, Latin Modern and DejaVu fonts separately. The outer renderer uses explicit P052 and Nimbus Sans Type 1 files. Component builders may verify exact font hashes. Missing fonts are not silently substituted.

From the extracted package directory, run:

```bash
python3 rebuild_monograph.py
```

The default pipeline is **prepare → assemble → audit → preview**:

1. `prepare_book.py` copies the selected components, applies the recorded display adaptations, resolves glossary references and creates the book sequence through `book_layout.py`.
2. `assemble_monograph.py` inserts selected source pages and editorial matter, resolves redirected links, adds global navigation and attaches the frozen readers.
3. `audit_monograph.py --render-samples` checks the assembled PDF and renders review samples.
4. `make_preview.py` selects a design tour from the actual book map.

`book_component_adapter.py`, `preserved_pdf_proofread.py`, `atlas_book_routes.py`, `render_book_matter.py` and their editorial JSON inputs are required build dependencies. The atlas-route pass binds the arithmetic atlas references to their final book folios. They are included in this package. The obsolete initial rebranding audit is retained as historical evidence and is not part of the default rebuild pipeline.

To compile the available edited LaTeX sources first:

```bash
python3 rebuild_monograph.py --from-sources
```

Preserved PDF treatments continue to use their recorded display adapters. Another TeX or font environment can change pagination or PDF bytes. Portability beyond the recorded environment and cross-platform byte identity are not promised. The sequence is recalculated from the rebuilt components, but the reviewed page-selection map is not inferred anew. If source pagination changes, review and update `editorial/book_revision/frontmatter_keep_overrides.json`, the affected source-page references and any exact PDF-edit anchors before accepting the rebuilt reading sequence.

A rebuild does not automatically renew the editorial or visual review. Before packaging, those reviews must be completed for the rebuilt PDF and identify its hash. To check the delivery gates without creating an archive:

```bash
python3 package_publication.py --check-only
```

After all three final reviews and the preview binding pass, `python3 package_publication.py` creates and verifies the publication ZIP. It does not perform a mathematical proof audit or a Lean replay.

## Integrity and rights

Before editing or rebuilding a pristine extracted package, run:

```bash
python3 -B scripts/verify_integrity.py --strict
```

The manifest verifies exact regular-file membership, sizes and SHA-256 hashes. Rebuilding intentionally changes files and invalidates the delivered manifest until a new package is made. Integrity verification does not establish mathematical truth.

Original writing, figures and editable writing sources use CC BY 4.0. Original software and machine-readable material use MIT. Third-party and font terms remain separate. Earlier unassigned-licence statements in preserved records are historical and superseded for original project material by the current grants. See `LICENSE.txt` and the supplied notices.

No public website, repository publication or external deployment is performed by these build commands.
