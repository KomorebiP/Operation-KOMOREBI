# Final Audit Report — Papers I, II, and III

**Author:** Komorebi P.  
**Audit date:** 2026-09-03

## Outcome

Papers I, II, and III are ready to serve as the authoritative foundation for Paper IV. This aggregate preserves the accepted Paper I and II v1.2.1 artifacts byte for byte and incorporates the final-proofread Paper III v1.0.1 release. The aggregate packaging pass verifies the complete expanded file set against both canonical child bundles.

## Final verification matrix

| Gate | Paper I | Paper II | Paper III |
| --- | ---: | ---: | ---: |
| Manuscript PDF | 40 pages, pass | 31 pages, pass | 27 pages, pass |
| Python tests / generated figures | 18/18 tests | 48/48 tests | 3 deterministic figures |
| Warning-fatal Lean build | 8,883 jobs | 8,879 jobs | 3,076 jobs |
| Formal contract / map | 35/35 rows | 25/25 rows | 41 rows |
| Unique mapped declarations | 84 | 160 | 143 |
| Fail-closed namespace audit | 1,126 declarations | 1,034 declarations | 468 declarations |
| Permitted Lean foundations | `propext`, `Classical.choice`, `Quot.sound` | `propext`, `Classical.choice`, `Quot.sound` | `propext`, `Classical.choice`, `Quot.sound` |
| Deterministic PDF | pass | pass | pass across four rebuilds |
| Full-page render inspection | pass | pass | all 27 pages pass |
| Internal checksum completeness | 90 files | 97 files | 34 files |

The previously recorded clean combined Papers I–II project imported both public aggregates and kernel audits and passed a warning-fatal 8,895-job build without namespace or import conflicts. Paper III remains in its own pinned Lean root and records its inherited Papers I–II dependency boundary explicitly.

## Paper III final-proofreading corrections

The last proofreading pass made only precision and presentation corrections; it did not enlarge the paper's theorem scope.

- The set-level naturality statement now quantifies the coordinate equivalences, defines the induced map explicitly, and states its composition law.
- Obstruction blocks and residuals are now distinguished cleanly from nonzero obstruction certificates.
- The holonomy subtraction formula now states the required ring setting, identifies the diagonal Kronecker term, and notes that off-diagonal blocks are unchanged.
- The heterogeneous-product formula now states its endpoint convention and the empty-tuple convention for length one.
- Several proof descriptions were tightened to match the compiled declarations exactly, including inverse cancellation, orbit language, operation-tree locality, and the triangle-holonomy conclusion.
- Figure placement, table-of-contents order, arrow visibility, PDF title metadata, DOI presentation, and US spelling were normalized.
- Citation metadata was corrected to valid CFF 1.2.0 structure and independently validated.

The resulting Paper III PDF was rebuilt four times with byte-identical output, structurally inspected, rendered page by page, and checked for embedded fonts, malformed actions, attachments, forms, JavaScript, placeholder text, private paths, and undisclosed author identity. No blocking issue remains.

## Selected artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| Paper I PDF | `437f7acc3f1a26592020dae1cbe050f521e0ce4f92a24f41ef666dcb9eb45b5c` |
| Paper II PDF | `3a5a7660c5250f99f0219617ebb291e628fe81da40e9f2b465cc3217deafc164` |
| Paper III PDF | `dea6a4e1958c4deefd1646131705db6e500d1fd0905b74428b9b4a1a66de9843` |
| Paper III LaTeX source | `96750e95867c0c0bed17b8031e6190a237b33a5fde4388f09ff1d1289ce98d84` |
| Paper III theorem map | `41c4d14674d14bfaabeab6c311e7a2ef1298f230fa776648402f50ee2df27866` |
| Paper III kernel audit | `503d1a7ae975fadf3a2b44e3260eb19f81a22248c7044f6e5d7e1f2e044071bf` |
| Canonical Papers I–II bundle | `a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052` |
| Canonical Paper III bundle | `dea3d734e55c6fed1c2301fbe53c7e1a16ce5dd24ab36b446da258a2578fd26c` |

## Interpretation boundary

“Lean-complete” means complete relative to each frozen, scope-explicit contract and theorem map. It does not establish novelty, priority, external peer review, or any mathematical statement outside those contracts. Numerical checks cover the finite cases recorded in the releases; they do not replace abstract proofs.
