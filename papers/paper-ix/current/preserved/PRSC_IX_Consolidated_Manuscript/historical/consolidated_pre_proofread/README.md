# Paper IX: consolidated manuscript and proof archive

**Author: Komorebi P. — 8 September 2026.**

The 45-page consolidated manuscript integrates the original arithmetic packet framework, completion of the stated Nishibuchi conjecture, sharp dyadic towers and periods, isometric extensions, finite obstructions and lift counts, compatible polynomial towers, quantitative deformation, and local analytic regularity.

Start with [Paper_IX_Consolidated.pdf](manuscript/consolidated/Paper_IX_Consolidated.pdf). Editable TeX is in the same folder, with component sections under `sections/`.

The manuscript includes proof explanations and a precise open-question section. The statement index maps 57 main statements to 178 actual source declarations. The broader declaration index records 1,876 declaration/source-version rows across the preserved verification frontiers; this is not a unique theorem count.

## What this edition changes

- Integrates the earlier manuscript and the completed continuation blocks into one numbered text.
- Aligns normalizations, coefficient domains, notation and theorem references.
- Distinguishes the classical N=2 edge tower from the four N=4 packets.
- States the difference between fixed-presentation obstruction theory and the native presentation/descent conjectures.
- Corrects stale summary counts in the consolidated evidence table using actual inventory entries and axiom records. Historical inventories remain unchanged.
- Preserves all 2,194 files from the previous analytic-regularity archive byte for byte. Replaced root documents and the old manuscript README move to `historical/analytic_regularity_release_root/`.

## Evidence

The consolidation performed source and retained-log integrity checks, statement-reference resolution, a mathematical manuscript review, a three-pass LaTeX build, and visual inspection of the PDF. It adds no new Lean theorem and does not describe the earlier compiler runs as newly performed.

The most recent preserved polynomial build passed 91 checks across 55 mathematical modules, with 515 audited declarations including definitions, support modules and statement contracts. Older arithmetic and other verification frontiers have their own retained reports. The consolidated evidence check reconciles 644 source hashes and 713 recorded log hashes. Four older affine logs lacked recorded historical hashes and are identified separately.

- `consolidation/audit/STATEMENT_INDEX.json` and `.csv`: manuscript statements and actual source declarations.
- `consolidation/audit/EVIDENCE_INDEX.json`: the 15 recorded verification frontiers and their source/report linkage.
- `consolidation/audit/DECLARATIONS.csv`: declaration/source-version inventory with copied occurrences retained.
- `consolidation/audit/MANUSCRIPT_REVIEW.json`: independent manuscript review and exact source hashes.
- `consolidation/audit/PDF_VISUAL_REVIEW.json`: PDF visual review.
- `consolidation/audit/CONSOLIDATION_NOTES.md`: repairs, failed access attempts and limitations.
- `REMAINING_CHECKLIST.md`: current proved/open checklist.

## Reproduce the document and proof checks

Build the manuscript with an installed TeX Live distribution:

```sh
python3 consolidation/tools/build_manuscript.py \
  --source manuscript/consolidated --output new-pdf-build
```

The mathematical verification uses the separately supplied pinned Lean 4.34.0-rc2 / Mathlib kit:

```sh
python3 replay_paper9_regularity.py --kit /path/to/kit --output new-polynomial-run
python3 replay_shared_correction.py --all --kit /path/to/kit --output new-arithmetic-run
```

Use a new output directory for each proof run. The PDF contains the verification-scope table and the allowed standard axiom dependencies. The source archive does not duplicate the portable runtime.

## Remaining questions and historical limits

The stated Nishibuchi conjecture and the local analyticity/differentiability block retain their proved scope. General rank-deficient singular persistence, Native 13.2 and 13.3, further exact valuation/period classifications, historical formula recovery, and some chart-interface comparisons remain open.

The original 28-page manuscript is preserved. Its original TeX, figure-generation sources and complete historical experiment package were not recovered; this edition does not claim to reproduce those historical assets. The larger reconstructed Annals text retains its own provenance and does not receive blanket formal coverage.

Fresh access to the official arXiv endpoints failed with `DisabledError`. The edition therefore retains the earlier detailed source-to-Lean comparison, fixed paper version and file hashes, without claiming a new primary-source inspection.
