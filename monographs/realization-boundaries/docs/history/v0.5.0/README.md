# Realization Boundaries — checked Lean companion v0.5.0

**Current checkpoint:** `verification/accepted_v0.5.0/run.json`, PASS. This continues v0.4.0 and does not claim that the entire book is formalized.

## New in this checkpoint

The actual direct sum D and every paired selector group G_A have exact full-endomorphism seed rank aleph_0. Their topological full-endomorphism rank and ordinary topological rank are separately proved aleph_0. Every finite seed family is trapped in a proper closed coordinate kernel, even when every endomorphism is admitted.

In contrast, the product P has ordinary topological rank one. A finite Chinese remainder construction proves density of the ordinary cyclic subgroup of the all-one vector. The theorem is transported to the actual canonical completion, providing a named generator and exact rank one there. The generator is not an original G_A element.

The ordinary cyclic subgroup of the all-one point is proper despite being dense. Under the different contract admitting all endomorphisms of P, its algebraic operator hull is P. Arbitrary coordinate multipliers may contain infinite information, so this does not certify finite-grammar description or computability.

All 26 inherited production modules, the publication PDF, and the original publication ZIP are unchanged. Five new modules contain 51 additional named theorem/lemma declarations.

## Entry points

| Declaration | Use |
|---|---|
| `coordinate_obstruction` | Simultaneous algebraic and topological closed-coordinate certificate. |
| `finiteSupport_seed_certificate` | Missing prime witness for a finite seed family in D. |
| `paired_seed_certificate` | Missing unselected-prime witness for arbitrary finite paired-group seeds. |
| `generationCardinals_isLeast_aleph0` | Exact minimal cardinal, including a true upper witness. |
| `paired_seed_rank_separation` | Original ranks aleph_0 and canonical-completion rank one. |
| `finite_coordinate_interpolation` | Real integer matching any finite prime pattern. |
| `completionGenerator_generates` | Actual generator in the canonical completion. |
| `primeSeed_not_in_all_one_cyclic` | Positive counterexample to confusing density with equality. |

All names are in `RealizationBoundaries`; import the root `RealizationBoundaries` module. Exported types, hypotheses and source locations are in `docs/NEW_EXACT_TYPES_v0.5.0.md` and `docs/NAMED_THEOREMS.json`.

## Verification

31 cleanly rebuilt production modules, 311 named theorem/lemma declarations, 698 audited declarations, 134 positive contracts, 33 intended rejections, and 31 kernel replays. All 100 command gates passed. These counts measure different things, not original discoveries or completion percentages.

## Reproduce

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Choose a new output directory. The pinned offline kit is excluded from this package. The verifier checks all dependency revisions, snapshots source/cache bytes, deletes project build output, rebuilds serially, audits every project declaration, compiles positive tests, checks intended rejection diagnostics, replays every production module and compares final hashes. Failed gates exit nonzero. Negative controls are never imported by production.

## Handoff

`CURRENT_CHECKPOINT.json` identifies the receipt. `PROGRESS_LEDGER_v0.5.0.md` supplies the next restart point. `LEAN_VERIFICATION_REPORT.md` describes results and trust limits. Three newly COMPLETE entries in the unchanged 45-result map are 2.3, 2.4 and 7.9. Earlier documentation and accepted records remain preserved.

The next block is the exact root-fiber equivalence/cardinality and cyclic CRT quotient identification. General graph reachability, subgroup-spectrum and dimension refinements, oracle semantics, and infinitely repeated grammar diagonalization remain separately tracked.

## Trust and license

Allowed transitive axioms are `propext`, `Classical.choice`, and `Quot.sound`. Production has no admitted proof, custom axiom, unsafe declaration, or native-decision trust axiom. Replay uses the same Lean kernel and restored pinned dependency caches, which were not rebuilt or independently authenticated upstream. No independent second kernel, external peer review, Python extraction theorem, or historical-priority certification is claimed.

The open license remains in `LICENSE`. Archived publication materials retain their own licensing. No compiler, dependency cache, or font file is included.
