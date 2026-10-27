# Machine-Native Reasoning
## Representation, Learning, and Computational Organization

**Komorebi P. · Operation Komorebi · Collection edition 1.0.0 · 9 October 2026**

This is a connected, theory-first compilation of twenty-four selected source documents. It is not a claim that their software components have all been integrated into one learning agent.

## Start here

Open **index.html** for the offline directory. The main reader is **readers/Komorebi_Machine_Theory_Compendium_v1.0.0.pdf** (1,919 pages). Start with the new **editorial/connected_synthesis.pdf** (27 pages), also included near the beginning of the main reader.

| Reader | Pages | Contents |
|---|---:|---|
| Complete selected compendium | 1,919 | Synthesis, all 24 source PDFs, navigation and entry cards |
| 01_Core_Machine_Theory.pdf | 511 | Synthesis and ten core works, from grounding to machine societies |
| 02_Mathematical_and_Architectural_Foundations.pdf | 697 | Seven extended works on representation, inference, workspaces, complexity, execution and preservation |
| 03_Formal_Visual_and_Lineage_Companions.pdf | 714 | Seven formal guides, visual companions, continuity protocol and historical recursive-improvement monograph |

The source documents contain 1,859 original pages. New material and navigation add sixty pages to the full reader. The split readers repeat selected navigation; the core split also includes the synthesis. Do not add their page counts to obtain a count of distinct work.

## The connected argument

The synthesis connects evidence, representation, executable operations, correction, discovery, shared work and institutions. Four elementary connecting results expose the assumptions needed for composition. They are explicitly restatements and compositions, not four mathematical priority claims. A sixteen-interface register distinguishes established conditional bridges from open or proposed integrations.

The new exact example follows an eight-world sensor through initialization, a changed repair question, calibrated translation, correction-preserving memory, two-agent communication and a repair-language revision. Its small code has eight groups and 18,316 exact assertions. It is not a trained agent, and it does not join all source runtimes.

## Files and source preservation

- **sources/** contains all 24 original PDF files, byte-identical to the retrieved editions.
- **source_archives/** contains six unchanged complete archives from the recent books and visual work. Full editable source archives were not recovered for every older PDF.
- **editorial/** contains the new LaTeX synthesis, source catalogue and selected historical source/review notes.
- **code/** contains the new exact illustration, figure generators, PDF assembly and validation programs.
- **figures/** contains four new analytical diagrams/charts as PDF, SVG and PNG. No image-generation assets are used.
- **companion/** contains the retained Python agent-dynamics animation and offline HTML player.
- **SOURCE_CATALOG.json** records selected identities, versions, hashes, roles and boundaries.
- **DOCUMENT_INDEX.csv**, **ASSEMBLY_MAP.json** and the four **\*_PAGE_MAP.csv** files map every imported page into the readers.
- **BRIDGE_REGISTER.csv** records the sixteen connections discussed in the synthesis.
- **validation/** records the actual assembly checks and execution boundaries.

Original source pages are neither reflowed nor stamped. Their printed pagination remains visible. PDF page labels identify source-local physical pages, for example `GA-8`. Source-card buttons link to connected works. In the smaller readers, a button leading outside that volume opens the companion full reader; keep the `readers/` directory together.

Historical experiments inside an unabridged source remain historical. Their inclusion does not convert them into evidence for the whole collection. Source-specific formal status, licensing and applicability are not homogenized.

## Rebuild

The supplied scripts were executed on Linux with Python, PyMuPDF, ReportLab, NumPy, Matplotlib and pdfLaTeX. The editor uses standard TeX Live packages including `tgpagella`, `tgheros`, `tocloft` and `hyperref`. The navigation generator requires system DejaVu fonts at `/usr/share/fonts/truetype/dejavu`. These are external dependencies; no standalone font files are distributed. Windows execution is not certified.

First check the frozen package before a rebuild overwrites timing records:

```text
python code/verify_release.py
```

Then rebuild using the shipped vector figures:

```text
python code/build.py
```

To regenerate only the new illustrations and figures:

```text
python code/check_connections.py
python code/make_figures.py
```

The build script runs only the new small example, the editorial typesetting, PDF assembly and preservation checks. It does **not** run every source archive's scientific suite or Lean project. Each command has a 60-second wall timeout; no separate memory quota is claimed.

## Scope

This is a substantial selected machine-theory corpus, not an exhaustive inventory of every Operation Komorebi archive. `UNASSEMBLED_BRANCHES.md` identifies source families not fully ingested. `REVIEW_NOTES.md` states the review depth and actual corrections. No blanket relicensing, repository publication, independent peer review, new kernel certification, hardware realization or unrestricted AGI result is implied.
