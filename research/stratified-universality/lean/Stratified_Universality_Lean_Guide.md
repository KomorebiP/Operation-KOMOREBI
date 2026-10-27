# Stratified Universality: Lean Guide and Formalization Concordance

Komorebi P. | Final edition, October 6, 2026

The PDF gives the full explanation and translation plan. This Markdown
companion records the exact evidence boundaries and correspondence register.

## Edition status

- A complete 602-line standalone `StratifiedFoundationsCore.lean` was inspected.
- Its textual inventory is 30 theorems, 12 definitions, two structures and 18
  `#check` commands. These are source counts, not fresh compiler results.
- The historical v0.7 README and AUDIT report seven modules and 183 theorem/lemma
  declarations with warning-as-error passes, no placeholders or custom axioms,
  and representative standard-foundation axiom reports.
- Those seven modules are not silently identified with the standalone Core.
- Lean and Lake were absent from PATH. No fresh Lean compilation or axiom check
  was executed for this edition.
- Matching ZIP materialization failed with HTTP 502. The standalone source was
  reconstructed from its complete read, restoring a terminal LF to match the
  published 22,747-byte size. No upstream hash authentication was available.

## Scope

The inspected source assumes a commutative ring, additive commutative module,
finite index types, and a complete orthogonal projector family. Its exact lane
space is the fixed-submodule coordinate space, not the unrestricted function
space. It proves module normalizations of L1-L6 and part of L8. The full typed
additive-category statement has separate recorded release coverage.

The semantic quotients and doctrine chapters are written results with exact
finite validators, but no declaration-level Lean correspondence was established
for them here. The broader atlas has explicit coherence/effectivity hypotheses.
This guide does not claim whole-manuscript Lean completion.

## Clause concordance

| Clause | Manuscript target | Evidence | Exact boundary |
|---|---|---|---|
| L1 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Finite module normalization; resolved laneSpace, not unrestricted function space. |
| L2 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Ambient corner blocks Q_j T P_i; categorical Hom-to-split-block bijection requires additional category layer. |
| L3 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Two-step finite contraction is inspected; iterated address-path expansion needs induction. |
| L4 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | One declared source and target refinement step, with fibre-sum hypotheses. |
| L5 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Selector endomorphisms on module morphisms; masks retain exact ambient blocks. |
| L6 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Support containment and exact three-term residual identity; no equality-of-support claim. |
| L7 | `thm:block15-universal-lane-transport` | RECORDED_RELEASE_ONLY | Historical v0.7 report describes CategoryCore; no matching declaration body inspected here. |
| L8 | `thm:block15-universal-lane-transport` | SOURCE_INSPECTED | Linear fold kernel and supplied-left-inverse criterion inspected; construction of injectivity/left inverse from globally typed Q_e and r_e hypotheses is not mapped. |
| RES | `prop:block15-certified-coarsening` | SOURCE_INSPECTED | Object-level prerequisite/analogue inspected; the Hom/block coarsening map and its multiplication compatibility are not declaration-mapped here. |
| H1-H5 | `thm:block16-holonomy-twisted-lane-transport` | RECORDED_RELEASE_ONLY | Reported v0.7 GroupoidLocalSystemCore/CategoricalAtlasCore coverage; ambient Hom coherence explicitly assumed. |
| BASE | `cor:block16-base-fiber-invariant-normal-form` | RECORDED_RELEASE_ONLY | Reported v0.7 local-system coverage; no source body inspected in this edition. |
| ORBIT | `thm:block16-orbit-descent` | RECORDED_RELEASE_ONLY | Reported v0.7 HolonomyFiniteCore coverage; object and pair orbits must remain distinct. |
| PAIR | `thm:block16-permutation-orbital-calculus` | RECORDED_RELEASE_ONLY | Reported v0.7 orbit basis and path-count coverage; no inspected declaration map. |
| CYC | `prop:block16-rational-cyclotomic-orbit-lanes` | RECORDED_RELEASE_ONLY | Partial recorded v0.7 coverage. Classical Möbius formula and cyclotomic factor/CRT identification remain explicit formalization obligations. |

## Inspected declarations

| Line | Kind | Qualified declaration |
|---:|---|---|
| 23 | structure | `Komorebi.StratifiedFoundations.ProjectorFamily` |
| 37 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.analyze` |
| 41 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.synthesize` |
| 44 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.synthesize_analyze` |
| 49 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.eq_of_projectors_eq` |
| 63 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.laneSpace` |
| 74 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.analysisLinear` |
| 80 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.synthesisLinear` |
| 86 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.synthesisLinear_analysisLinear` |
| 93 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.analysisLinear_synthesisLinear` |
| 109 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.laneEquiv` |
| 117 | def | `Komorebi.StratifiedFoundations.ProjectorFamily.changeResolution` |
| 125 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.changeResolution_symm` |
| 134 | theorem | `Komorebi.StratifiedFoundations.ProjectorFamily.changeResolution_trans` |
| 156 | theorem | `Komorebi.StratifiedFoundations.linearMap_fintype_sum_apply` |
| 164 | def | `Komorebi.StratifiedFoundations.transferBlock` |
| 172 | theorem | `Komorebi.StratifiedFoundations.transferBlock_reconstruction_apply` |
| 188 | theorem | `Komorebi.StratifiedFoundations.transferBlock_reconstruction` |
| 198 | theorem | `Komorebi.StratifiedFoundations.transferBlock_ext` |
| 217 | theorem | `Komorebi.StratifiedFoundations.transferBlock_comp` |
| 235 | theorem | `Komorebi.StratifiedFoundations.transferBlock_comp_matrix` |
| 256 | def | `Komorebi.StratifiedFoundations.maskBlocks` |
| 263 | theorem | `Komorebi.StratifiedFoundations.maskBlocks_idempotent` |
| 273 | theorem | `Komorebi.StratifiedFoundations.maskBlocks_inter` |
| 283 | theorem | `Komorebi.StratifiedFoundations.transferBlock_self` |
| 294 | theorem | `Komorebi.StratifiedFoundations.transferBlock_ne_target` |
| 304 | theorem | `Komorebi.StratifiedFoundations.transferBlock_ne_source` |
| 314 | def | `Komorebi.StratifiedFoundations.select` |
| 323 | theorem | `Komorebi.StratifiedFoundations.transferBlock_select_of_mem` |
| 355 | theorem | `Komorebi.StratifiedFoundations.transferBlock_select_of_not_mem` |
| 384 | theorem | `Komorebi.StratifiedFoundations.select_idempotent` |
| 399 | theorem | `Komorebi.StratifiedFoundations.select_inter` |
| 422 | def | `Komorebi.StratifiedFoundations.composeSupport` |
| 427 | theorem | `Komorebi.StratifiedFoundations.select_comp_of_supported` |
| 462 | def | `Komorebi.StratifiedFoundations.residual` |
| 470 | theorem | `Komorebi.StratifiedFoundations.select_add_residual` |
| 479 | theorem | `Komorebi.StratifiedFoundations.select_all` |
| 487 | theorem | `Komorebi.StratifiedFoundations.residual_all` |
| 496 | theorem | `Komorebi.StratifiedFoundations.composition_residual_identity` |
| 509 | theorem | `Komorebi.StratifiedFoundations.selected_composition_residual_identity` |
| 524 | structure | `Komorebi.StratifiedFoundations.Refines` |
| 533 | theorem | `Komorebi.StratifiedFoundations.transferBlock_refinement` |
| 571 | theorem | `Komorebi.StratifiedFoundations.fold_eq_iff_sub_mem_ker` |
| 576 | theorem | `Komorebi.StratifiedFoundations.ker_eq_bot_of_leftInverse` |

## Recorded v0.7 boundary

The v0.7 record reports finite categorical transport, compatible local-system
sections, base-fiber loop invariants, finite holonomy orbits, pair-orbit
intertwiner coordinates, and cyclotomic rational projector descent. Its source
bodies and logs were not recovered in this edition. Recorded axiom examples
are historical evidence, not fresh execution.

The recorded open identifications are the classical Möbius formula for the
integral Ramanujan coefficients, the corresponding classical normal form,
the cyclotomic factor/CRT decomposition, and derivation of `CoherentHomPair`
from a full category-valued pseudofunctor/descent-object layer.

The later Blocks17-26 manifest lists Markdown, Python and JSON only. The ZIP
was unread and supplies no further Lean coverage claim.

## Reproduction

Recorded pins: Lean `4.34.0-rc2`, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Use the actual recovered project and dependency lock. Once a source is available:

```bash
lake env lean -DwarningAsError=true src/CyclotomicGaloisCore.lean
```

For the standalone Core in a compatible project:

```bash
lake env lean -DwarningAsError=true StratifiedFoundationsCore.lean
```

Its compatibility with the v0.7 pin has not been tested here. Retain exit codes,
logs, source hashes, actual revision pins and declaration-level axiom reports.
An unexecuted `#check` is not a compiler pass.

## Included registers

- `Lean_Concordance.csv` and `.json`: exact clause mappings and boundaries.
- `Inspected_Declaration_Inventory.csv`: all inspected declarations.
- `Manuscript_Result_Inventory.csv`: 242 statement environments in the frozen
  original v2.0.0 source graph, retaining original coordinates rather than
  amended final statement text.
- `Component_Status_Concordance.csv`: canonical 75-row final-edition component
  table, from `traditional/Komorebi_Theorem_Concordance_Final_2026-10-06.json`,
  with amended hypotheses, publication-amendment notes and unchanged IDs/statuses.
- `Component_Status_Concordance_Inherited_v0.4.csv`: historical 75-row table
  preserving the original hypotheses. It does not define final-edition scope.
- `Recorded_v0.7_Audit_Evidence.json`: complete readable historical audit data,
  with source identity and an explicit historical-evidence classification.
- `inspected_source/`: the reconstructed standalone source and provenance.

To regenerate the guide text and registers from the preserved frozen source,
extract that archive and run `python3 lean/build_guide.py --upstream PATH`, where
`PATH` is its extracted root. This generation command does not execute Lean.

The full guide supplies explanations of analysis/synthesis, transfer blocks,
refinement, selectors, residual propagation, fold kernels, complete resolution
change, recorded holonomy/cyclotomic coverage, and an explicitly unverified
translation plan for the semantic and doctrine extension.
