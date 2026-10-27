# Traditional Stratified Universality publication report

Date: 6 October 2026

## Deliverable and inherited base

- Main source: `traditional/Stratified_Universality_Traditional.tex`
- Compiled PDF: `traditional/Stratified_Universality_Traditional.pdf`, 256 pages
- Mathematical base: version 2.0.0, 23 September 2026
- All 316 files from the inherited manuscript tree remain byte-for-byte unchanged. The final-use main and amended block copies are separate files.
- The complete original theorem-label set, 75 concordance component identities, and 75 component proof-status classifications are retained.
- The cover is dated 6 October 2026 and named Final Publication Edition. Source-availability prose explicitly includes `.md` files, TeX, figure generators, data, exact validators, and inherited reports.
- The supplied v2.0.0 source contains no `.lean`, `lean-toolchain`, or `lakefile` files. Separate related Lean work has its own source and correspondence obligations. This traditional build is not Lean certification.

## Five authorized mathematical amendment groups

1. Block 16 orbit descent: minimal nonempty compatible support atoms are distinguished from nonzero action on the compatible-section group. A single pair orbit need not support any nonzero compatible section. The claim-ledger summary and FND-17 correspondence are reconciled.
2. Block 18 observer packets: the branch alphabet and raw-history family are finite; empty monoid aggregation is zero. Convex packets may be empty, with `h_empty = -infinity`, `conv(empty) = empty`, and `max(empty) = -infinity`; the formula includes empty incoming fibers. CAR-02 and CVX-01 hypotheses/notes are reconciled.
3. Block 19 escape: the compactness argument uses an attained positive minimum on each compact conditioned defect sublevel. The conclusion and Hausdorff hypotheses are unchanged; sequential compactness is not assumed. ADM-01 is reconciled.
4. Block 17 coinduction: the proof shows every fixed point lies in the behavioral core and the core is itself a fixed point. Finite certification includes the containment induction from the initial invisible submodule. The theorem/corollary statements remain unchanged. SEM-02 and SEM-03 are reconciled.
5. Block 19 metric conventions: dimension is positive; determinant-normalized holonomy is `|det H|^(-1/n) H`; reverse traversal uses inverse transport. The sufficiency proof writes the spanning-tree metric construction and edge scale explicitly. ADM-02 notes and supporting metric-result metadata record the convention clarification.

These changes were checked by the bounded mathematics reviewer after application. Their precise review scope and counterexample evidence are recorded in `SCOPE_REVIEW.md`. The complete manuscript has not received a new independent proof audit.

The original concordance JSON and generated tables remain unchanged. `Komorebi_Theorem_Concordance_Final_2026-10-06.json` and `final_generated/` are separate final-edition versions. Inherited publication tables are explicitly marked as dated historical records in the final manuscript; their original 247-page artifact is not confused with this 256-page build.

## Conservative proofreading self-review

- Scope: changed cover/release-note prose, amended mathematical hunks, new concordance notes, and nearby definitions/proof context.
- Routine edits: cover title/date/provenance; source availability and evidence-scope note; one punctuation correction; historical-audit scope clarification.
- Mathematical-token/proof changes: the five groups listed above. These are explicit authorized proof or hypothesis amendments, not silently classified as typography.
- Unresolved issues in the changed hunks: none after reviewer recheck. The inherited conditional/conjectural boundaries are retained.
- Original theorem/proof content outside those groups was preserved rather than re-authored.

## Fresh validation

- Three final `pdflatex -interaction=nonstopmode -halt-on-error -file-line-error` passes completed with exit 0.
- Final publication audit: 77/77 checks PASS; zero failures.
- Source graph: 65 recursively included TeX files; 620 unique labels; 153 source-reference targets; 18 citation keys.
- No undefined references, unresolved citations, LaTeX warnings, overfull boxes, or fatal errors appear in the final log.
- All inherited manuscript files were compared byte-for-byte; no differences.
- Every page was checked for text blocks outside page bounds after accounting for PDF page rotation: zero out-of-page text blocks.
- Representative rendered pages were visually inspected, including cover, publication note, orbit amendment, coinduction/finite certification, convex packets, compact escape, and metric completion. No clipping or layout defects were found in that sample.
- This agent inspected inherited exact-validation records; it did not rerun their mathematical suites. Any separate fresh validator runs are reported by their own executing agent.

Reproduction: run `./Build_Final.sh` from the traditional source directory with the supplied Python dependencies and pdflatex. The script regenerates only final-edition concordance material and final-edition audit files; inherited reports remain untouched.

PDF SHA-256: `1d71dd8c3095b5a7e962d095e6f013b0ca2fcc7b63e066eab02f5bfdc7985944`

Main-source SHA-256: `4f8f6ccbcc2a948a834aa0ebf0b24f874355f88003c261f6034eca4cdbb757a0`

## Amended source hashes

| Final-use source | SHA-256 |
|---|---|
| `block16_section_final.tex` | `2b086cc6d806c3cf25b443a6ecefa871adba282d913deffaafabcadad2c0258a` |
| `block17_semantic_quotients_final.tex` | `ef408f87352057761b6bf55742f848612f585632691f71488d510393749b0735` |
| `block18_carrier_observer_change_final.tex` | `6babbf13d884e5bdf86174ce89729ccf69feb694cf84e03c0f52c32038775157` |
| `block19_admissibility_lifting_final.tex` | `038f352d1e9a82984963af0e90a14b104b8f17f7b2e8e4df2c8da627bc089799` |
| `appendix_claim_ledger_final.tex` | `4086d789d942d7e813d9b23e92a9692f15b8f2e1bce03a19e3e3d1bb6737d5b7` |

## Execution corrections

An initial amendment script failed because it addressed a nonexistent JSON key (`source_audit`); the actual key is `edition_control`. The key was corrected and the script reran successfully. An initial geometric page-bound check omitted page rotation and falsely flagged landscape pages; the check was corrected and all 256 pages passed. A visual-QA call requested an unrendered page number; the actual coinduction page (210) was then inspected successfully. None of these transient issues altered inherited files or the final mathematics.
