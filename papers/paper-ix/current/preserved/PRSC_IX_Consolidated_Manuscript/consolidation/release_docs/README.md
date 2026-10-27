# Paper IX: arithmetic packets, lifting and deformation

**Komorebi P. — proofread edition, 8 September 2026**

Start with [Paper_IX_Consolidated.pdf](manuscript/consolidated/Paper_IX_Consolidated.pdf), the current {{PAGE_COUNT}}-page manuscript. The editable TeX and its component sections are in the same directory.

The paper develops the arithmetic packet framework, proves Nishibuchi's conjecture throughout its stated range, and gives sharp dyadic displacement and period results. Its lifting theory proceeds from finite obstructions and exact lift counts to compatible polynomial towers, quantitative deformation, and local analytic regularity.

This edition improves the prose and restores material omitted from the first consolidation: the explicit denominator product, Bernoulli boundary, Lucas reduction and common standard-window period, signed zigzag identity, and normalization counterexample. It also makes the depth-zero case of shared affine lifting explicit. The manuscript states the evidence for each restoration. In particular, the Bernoulli identity has a classical derivation here; no dedicated Lean bridge was matched. Previously recorded native progress is acknowledged with its separate evidence status.

The [remaining checklist](REMAINING_CHECKLIST.md) distinguishes completed results from research extensions and historical recovery. The unrestricted native conjectures and general singular persistence remain open.

## What was checked

The revision received a prose and notation pass, a source-based completeness review, an independent semantic review, a three-pass LaTeX build, and inspection of every final PDF page. The current statement index links {{MAPPED_STATEMENTS}} manuscript statements to {{SOURCE_LINKS}} source declarations. These reviews and indexes are bound to the final source hashes.

No Lean source was changed, and earlier compiler runs are not described as newly performed. Their original reports remain in the archive. The retained evidence index covers 15 verification frontiers and reconciles 644 source hashes and 713 recorded log hashes. Four older affine logs lack historical hashes and are identified separately. The declaration index contains 1,876 declaration/source-version rows; this is not a count of unique theorems.

- [Semantic review](consolidation/editorial/SEMANTIC_REVIEW.json): mathematical meaning and final source hashes.
- [Completeness review](consolidation/editorial/COMPLETENESS_REVIEW.json): coverage of the preserved original paper and completed continuation blocks.
- [Visual review](consolidation/editorial/PDF_VISUAL_REVIEW.json): inspection of the exact final PDF.
- [Statement index](consolidation/audit/STATEMENT_INDEX.json): manuscript-to-source references, with a CSV alongside it.
- [Evidence index](consolidation/audit/EVIDENCE_INDEX.json): retained verification frontiers and their evidence.
- [Package completeness](PACKAGE_COMPLETENESS.json): every prior file and its preserved location.

## Reproduce the document

With TeX Live installed, run:

```sh
python3 consolidation/tools/build_manuscript.py \
  --source manuscript/consolidated --output new-pdf-build
```

The preserved proof checks use the separately supplied Lean 4.34.0-rc2 / Mathlib kit:

```sh
python3 replay_paper9_regularity.py --kit /path/to/kit --output new-polynomial-run
python3 replay_shared_correction.py --all --kit /path/to/kit --output new-arithmetic-run
```

Use a new output directory for each run. The archive retains the individual verification reports and does not duplicate the portable runtime.

The package assembler and entry-document templates are preserved in `consolidation/tools/assemble_proofread.py` and `consolidation/release_docs/`. To reproduce this assembly with the previous consolidated ZIP available, use:

```sh
python3 consolidation/tools/assemble_proofread.py \
  --staging-directory /path/to/staging \
  --base-archive /path/to/previous/PRSC_IX_Consolidated_Manuscript.zip \
  --output-directory /path/to/new-output
```

The staging directory contains `manuscript/` with the current TeX and sections, plus `audit/`, `tools/`, `editorial/`, `release_docs/`, and `build/`. Copy the latter directories from `consolidation/`; put the current PDF in `build/` alongside its build report and logs. The assembler checks the fixed previous-archive hash, every current source hash, and the final review bindings before writing either deliverable.

## Preservation and historical limits

All {{PRIOR_FILE_COUNT}} files from the previous consolidated archive are retained byte for byte. Replaced documents and prior manuscript reviews are under `historical/consolidated_pre_proofread/`, with their original relative paths. A SHA-256 manifest covers the current package.

The original 28-page manuscript is preserved, but its original TeX, figure-generation sources and complete historical experiment package have not been recovered. The reconstructed Annals text has a broader scope than this manuscript and retains its own provenance. Preserving it does not certify every claim in it.

The earlier comparison with Nishibuchi's paper is retained with its fixed source version and hashes. This editorial revision does not claim a fresh inspection of that external paper.
