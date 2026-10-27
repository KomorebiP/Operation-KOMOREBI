# Komorebi Space
## Coherent realizations, obstructions, and descent

**Expanded monograph edition 1.4.0 · Komorebi P. · 11 October 2026**

The reader set contains a **105-page monograph**, a **33-page visual guide with 30 plates**, and a **33-page Lean/evidence guide**. The monograph has six parts, 29 numbered sections, and four appendices. It continues the accepted version 1.2.0 formal baseline without changing any formal file.

Five additional chapters develop variable-rate exactification, residual floors, independent transformation costs, a coherent phase obstruction, and a complete Hilbert-space example in which exact finite repairs escape the intended ambient space. Nine solved reader problems and a hypothesis atlas support navigation and applications. The existing finite-observation, repair-comparison, stack-descent, and worked-loop developments remain intact.

## What the expansion establishes

The principal source map contains **80 items and 211 declaration references**. KS71–KS80 develop results already present in the accepted formal library. Separately identified models have complete written derivations and finite exact checks, not newly compiled Lean instances. The infinite Hilbert example has a nonzero algebraic obstruction and zero residual floor: every finite prefix is solvable, and a coherent full-product point exists, but no protected square-summable realization exists. Every sequence of protected candidates with vanishing residual has unbounded correction norms.

The new six plates show polynomial convergence, residual bursts, different exact limits with the same residual history, escaping correction sizes, directed transformation costs, and the phase table. They are plots or diagrams of explicit mathematical models.

## Formal evidence and current execution

The **retained version 1.2.0** record covers 138 production modules plus one root, 139 successful compilation targets, 4,745 audited project declarations, and 1,507 explicit named theorem/lemma declarations including auxiliaries. **No new Lean compilation or axiom audit was run for this edition.** All 156 formal-tree files match the predecessor, including sources, metadata, scripts, and tests. The official kernel, compiler, standard axioms, and pinned imported dependencies retain their recorded trust boundary.

Five freshly rerun exact finite suites pass **144,366 assertions**. The added suite contributes **13,817 assertions and eight rejection controls**. Infinite convergence, closure and nonexistence are established by the supplied proofs, not by extrapolating those finite tests. Source correspondence remains an editorial relation, not a machine translation of prose.

## Start here

- `publication/`: the monograph and both companions.
- `source/`: editable LaTeX, figure sources, and chapter files.
- `formal/`: the unchanged canonical Lean project and offline verifier.
- `data/claim_ledger.json`: principal IDs, exact source names, hashes, and scope notes.
- `data/deepening_models.json`: separate evidence scopes of the worked models.
- `examples/approximation_models.py`: exact rational path, prefix-repair, and phase examples.
- `audit/publication_release_v1.4.0.json`: current publication evidence.
- `audit/formal/release.json`: the retained **version 1.2.0** formal record.
- `PROGRESS_LEDGER.md` and `REVIEW_NOTES.md`: changes, failures, and restart instructions.

## Verify and rebuild

```bash
python3 checks/verify_payload.py
bash build.sh
```

The publication build does not invoke Lean. A new formal replay requires the separate pinned runtime and a fresh label, as explained in `BUILD.md`. Original source/evidence archives and earlier publication snapshots are included. No standalone font files or external runtime are distributed.

## Scope

The previously identified KS54–KS58 formalization tasks remain closed in the retained baseline. This edition does not assert a universal view doctrine, arbitrary higher-stack theorem, unrestricted semantic realization, universal Python refinement, or a new formalization of the infinite Hilbert model. Historical novelty is not inferred from a source count or a successful test.
