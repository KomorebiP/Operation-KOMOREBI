# Visual-guide mathematical proofreading and QA

Proofread: all authored `visual/main.tex` spreads, source page and `visual/figures.py` labels.

- Routine edits: grammar, legible figure labels, consistent correspondence and character conventions, explicit primary source versions.
- Mathematical-token changes from broader audit, recorded separately from conservative proofreading: contained-frame hypothesis, nonorthogonal-range wording, proposed all-degree dyadic status, rational CM-orbit boundary and explicit fivephase parameter range. No further mathematical-token change was made during final proofreading.
- Unresolved proofreading issues: none. Mathematical construction obligations remain stated in spreads18 and34.
- Validation: `python visual/figures.py`, exact integer/rational assertions, `python build.py --only visual`, no overfull boxes or undefined references. All34 figure input pins match. Font embedding/subsetting/Unicode maps pass, with no Type3 fonts.
- Visual coverage: all36 pages rendered at150dpi with Poppler and inspected in contact sheets. Critical and changed pages also inspected individually. Initial figure clipping, weak contrast and overlap findings were corrected before freeze. Independent literature and computation reviewers pin their assigned pages.

The final PDF identity and numerical QA record are in `SELF_QA.json`. The figure contract explains which drawings are schematic, which are exact arithmetic examples and which carry manuscript dependencies. A finite PASS is never presented as the general Hodge conjecture.
