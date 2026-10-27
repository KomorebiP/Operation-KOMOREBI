# AVOC — Complete Publication Set

**Komorebi P. · 7 October 2026 · Publication edition 1.0**

The publication contains three complementary PDFs, totaling 111 physical pages and 18 exact figures:

1. `output/AVOC_Traditional_Final.pdf` (35 pages): mathematical definitions, proofs, planning, calibration, recorder composition, recovery, exact examples, and limitations.
2. `output/AVOC_Visual_Guide_Final.pdf` (35 pages): an extended worked route with exact Python figures and contrasting examples.
3. `output/AVOC_Lean_Companion_Final.pdf` (41 pages): actual theorem/proof excerpts, hypotheses, dependency maps, negative controls, and pinned reproduction commands.

## Formal baseline

The intact `inputs/AVOC_Formal_v0.41.0.zip` is the authoritative delivered formal source. SHA-256:

`04efab87010b3b88c9a119275e190423a2465da32ba1e526edb7e6d2e0cd077e`

It contains the complete v0.41.0 formal theory, Python tools, Markdown instructions, historical failures and corrections, verification records, and exact experiments. The source archive excludes the Lean runtime and compiled dependencies. The original archive is preserved, rather than silently rewritten for publication.

## Evidence status

The archived release reports 222 passing build targets, 195 non-audit mathematical modules, 2,268 named theorem/lemma axiom reports, and 135 substantive negative proof rejections. Allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`. These are different evidence counts and are not a count of independent discoveries.

Fresh publication checks include payload digest verification, source/receipt inventory consistency, exact rational example recomputation, the declared bounded Python recorder comparison, independent proof/exposition review, and PDF rendering review. Detailed records are under `reviews`.

**Fresh Lean compilation and actual Lean endpoint execution were not run for this publication edition.** Lean/Lake and the exact portable dependency kit were unavailable. Archived kernel checks are preserved and clearly labeled. Finite Python tests do not establish universal parser, host, storage, or physical-operation refinement.

## Rebuild documents and examples

Python 3.10+ is required. Figures use matplotlib and numpy. The documents use pdflatex with standard TeX Live packages and Latin Modern fonts. No generated figure is an AI image.

From the publication root:

```bash
python3 -m zipfile -e inputs/AVOC_Formal_v0.41.0.zip source
python3 scripts/lean_inventory.py
python3 scripts/verify_exact_examples.py --output reviews/exact_example_replay.json
python3 scripts/avoc_figures.py
python3 scripts/build_publication.py
```

Read the script's help or source before changing arguments. Its default source root is the extracted `source/AVOC_Formal_v0.41.0` tree. These publication checks do not replace the pinned formal build.

To reproduce Lean evidence, use the original `REPRODUCE.md`, `lean-toolchain`, and `lake-manifest.json` inside the source archive. The compiler is Lean 4.34.0-rc2; the nine dependency revisions must match. Do not regenerate historical evidence in place unless you intend to replace it. The provided workflow explains separate replay outputs and build resumption.

## Key mathematical boundary

The final statistical theorem bounds the unconditional probability of issuing a plan without the stated episode certificate by the sum of fixed scheduled error allowances. It is a theorem about the defined finite rational source-generative recorder. It does not infer the source law from accepted raw log syntax, guarantee issuance, or assert the same nominal error bound conditional on completion.

The completion-order example shows why this boundary matters: even honest, complete, unique, fully resolved logs can give biased reported prefixes when successes finish before rejections. Physical-attempt coupling, initiation-indexed sample contracts, authentication, universal host refinement, and changing quotes within an episode remain open extensions.

## Package contents

`manuscripts`: editable LaTeX sources. `figures`: vector PDFs and raster previews. `scripts`: figure, exact-example, inventory, build, validation, and packaging programs. `reviews`: source maps, independent audit, computation results, and rendering checks. `inputs`: intact original formal archive. The included Markdown files explain claims, corrections, failures, and reproduction.
