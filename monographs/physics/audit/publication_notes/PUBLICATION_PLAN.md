# Physics centered continuum publication update

Status: completed after PASS_SCOPED_CENTERED_EXTENSION, accepted receipt SHA-256 f530e4bb0c55204fe3d7d55c9cf71c60781f5db949541bfc9b3c649241799d11. The final book has 572 pages and 574 bookmarks. Publication QA is audit/continuum_publication_qa.json. The plan below records the scoped work that was performed.

Baseline source and PDF identities are recorded in `BASELINE_PUBLICATION_INPUTS.json`.
The publication-facing tree is `../publication`. Its `formal/` directory was intentionally
omitted because root owns the formal release integration. No new Lean source is copied
or edited by this publication work.

## Minimal editable scope

1. `assemble_reading_volume.py`: central front-matter verification paragraph.
2. `book/reading_text.json`: current versus retained verification, exact source correspondence,
   and the new formal scope while retaining the production-energy obstruction.
3. `source/generator/Block50_Spectral_Generator_Bridge.tex`: two verification-status
   paragraphs, and the explicit nonnegative time-horizon assumption in the compact-time
   statements. Original proof arguments remain unchanged.
4. `source/monographs/chapters/orientation.tex` and `chapters/boundary.tex`: remove inherited stale wording that the
   accepted generator has no compiler certificate.
5. `source/monographs/lean/lean_body.tex`: precise new declaration correspondence and
   verification boundary. Keep abstract spectral-functional-calculus linkage open.
6. `source/monographs/Physics_Lean_Companion.tex`: broaden the companion cover wording
   to include the checked centered approximation without a redesign.
7. `source/monographs/visual/visual_body.tex`: update the formal-scope plate and current
   written-versus-formal descriptions. Retain the fixed infinite-space distinction.
8. `source/monographs/gauge_lean/lean_body.tex`: reconcile one stale paragraph, while
   retaining background-coupling and dynamical gauge obligations.
9. `source/monographs/figures/12_frontier.pdf` and `.png`: update only the schematic
   verification diagram using Python/matplotlib. All numerical figure data remain unchanged.
10. Root README and publication QA records: only after final proof status and actual
    PDF page counts are known. Historical verification records stay historical.

## Mathematical-token correction

The independent target review found that the compact-time supremum needs `T >= 0`
explicitly. Add that hypothesis to the generator/propagator rate statement's uniform
consequence and to the physical torus corollary. This is a reviewed hypothesis clarification,
not a new proof. Keep `h != 0`, the exact third-order Fourier moment, `|t|`, and the
coefficient `1/6` unchanged.

## Build and completed checks

Rebuild the five affected components with three TeX passes:

```
python3 build_documents.py Block50_Spectral_Generator_Bridge Physics_Dirac_Monograph Physics_Lean_Companion Physics_Visual_Atlas Physics_Gauge_Lean_Companion
python3 assemble_reading_volume.py
python3 audit_design.py
python3 render_design_audit.py
```

The baseline component page counts are 7, 32, 15, 15, and 14. The full book is 570 pages.
Final component page counts are 7, 32, 17, 15, and 14; the assembled book is 572 pages. TeX, font lookup,
Poppler and Python PDF libraries are available.

Run a tailored preservation comparison that permits only the reviewed hypothesis
clarifications, status prose and new technical correspondence. The generic inherited
`audit_design.py BASELINE` requires all theorem statements and `formal/` files to be
unchanged, so it is not an appropriate acceptance gate for this explicitly scoped edit.
Its independent layout/log check without a baseline remains applicable.

Render every final page. Inspect all changed component pages and all changed front matter
at readable scale, check running folios, internal links, bookmarks, text bounds, embedded
fonts and final TeX warnings. Preserve failed build attempts separately from accepted logs.

The publication edit does not run Lean, certify cosmology, add numerical experiments,
or establish whole-book independent review.
