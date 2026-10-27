# Consolidation work and limitations

The current edition consolidates existing mathematical results. It does not add a Lean theorem, modify inherited Lean sources, or claim to rerun their full compiler gates.

## Changes and checks

- Integrated the original framework and all principal completed continuation blocks into a 45-page LaTeX manuscript.
- Mapped 57 statements to 178 actual source declarations. These are manuscript mappings, not 57 new theorems.
- Reconciled the preserved verification frontiers, source hashes, log hashes and axiom-declaration inventories. The independent review separately checked the mathematical meaning of statements and proof explanations.
- Preserved all 2,194 files from the preceding source archive, relocating only superseded entry documents.
- Completed final self-review of changed mathematical prose, labels, references, coefficient domains and normalization. A separate independent review records exact coverage and hashes.

## Issues found and repaired

1. An older strengthening inventory had stale summary scalars. The consolidated table uses the actual entries: 215 theorem commands, 10 lemma commands, 20 definitions and one abbreviation, matching the 246-name axiom audit. The original file remains unchanged.
2. The draft reused the residue-projector symbol for a normalized inverse Euler series. The arithmetic author changed that series symbol to distinguish the two objects.
3. The Riccati induction explanation needed its higher-order restriction and initial case stated explicitly. The exposition was clarified against the existing source, with no new mathematical hypothesis or source edit.
4. The analytic inverse proof initially described the source neighborhood ambiguously. The text now identifies it as the source of the open partial homeomorphism defined by the original augmented map, whose inverse is the constructed inverse function.
5. A long unbreakable Mathlib revision identifier overflowed the text width. It now uses a breakable identifier format.
6. Two contents entries spilled onto an almost blank page in the first integrated PDF. A local contents font/spacing adjustment places the entire contents on one page. The final PDF has 45 pages.
7. The build-warning scanner initially mistook the package-description word “Rerun” for a rerun warning. It now matches actual warning phrases. The final build has no overfull boxes, undefined references, duplicate labels or missing glyph warnings. One underfull theorem-heading line was visually inspected and is harmless.
8. Two initial orchestration snippets were rejected by JavaScript parsing before their tool calls ran. Corrected syntax was used; neither failed snippet changed files.

## Unresolved access and historical limits

Fresh official arXiv HTML, abstract and PDF requests all returned `DisabledError`. The edition retains the prior detailed source-to-Lean review and its fixed-version PDF/text hashes, and does not claim a fresh primary-source inspection. The attempts are recorded in `EXTERNAL_ACCESS_ATTEMPT.json`.

The original 28-page manuscript PDF remains available, but its original TeX, figure-generation sources and complete historical experiment package were not recovered. The consolidated manuscript does not claim to recreate those missing original assets. Preserved reconstructed texts retain their own evidence status.

General singular persistence, Native 13.2 and 13.3, further exact valuation and period classifications, historical formula recovery and some older chart-interface comparisons remain research or interface work. Their status is explicit in the manuscript and checklist.
