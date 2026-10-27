# Resume Paper I after completion Block 03

Read `VERIFICATION.json` first. Only a final PASS receipt is accepted. Failed or exploratory runs remain in `evidence/development` and the run index and must not be used as completion evidence.

## Frozen source closure

- Original formal v1.0.2: `predecessor/baseline/source/main`, unchanged.
- Block 02 additions: `predecessor/source/extension`, unchanged.
- Block 03 additions: `source/extension/PaperICompletion3` and the new root.

The new sources prove actual arbitrary-field primary presentations, residue-field lower bounds, CRT generators, the exact operator seed minimum, presentation-independent maximum, a primary cyclicity criterion, and the conditional invariant-factor count.

## Immediate next mathematical obligation

Stay on Paper I. Close the literal intrinsic-primary quotient identification for `PSC-I-T-SINGLE-OPERATOR`.

1. Define or select the intrinsic p-primary submodule for the actual action `Module.AEval' T`. Do not replace it by an unrelated witness carrying the desired conclusion.
2. For a positive primary presentation, prove its grouped p-labelled factor is equivalent to that intrinsic primary submodule. Show other irreducible factors have no p-primary contribution using coprimality.
3. Restrict the existing `residueFiberMap` to this grouped factor. Prove that its kernel is exactly multiplication by p, coordinatewise, and transport this equality to the literal image p(T)X_p.
4. Construct the induced residue-field linear quotient equivalence. Conclude that the intrinsic dimension equals the fibre count for each irreducible p, not merely that the maximum agrees.
5. Combine with `exists_operator_primary_seed_formula` and update record 43 only after its complete printed type is mapped and kernel checked.

The residue-map surjectivity, positive-exponent handling, exact lower/upper bounds and transport machinery already exist. Do not repeat them as though they were still missing.

An alternative global-quotient-first route is detailed in `docs/NEXT_INTRINSIC_QUOTIENT_ROUTE.md`. It may reduce dependent-submodule bookkeeping. That document is a proof plan, not an accepted Lean theorem.

## Follow-on obligations

Derive the algebraically closed arbitrary-operator geometric-multiplicity formula, including non-diagonalizable operators. Then assemble the remaining six-way cyclic criterion, especially the scalar-extension/eigenspace clause. The previous self-adjoint result remains verified and must not be mistaken for the arbitrary-operator result.

Nonsplit semisimple, module-top/Nakayama, expanded packet and topological records, and executable certification remain separately tracked in `coverage/COVERAGE_108.json`. Papers II–XII have not been rerun in this audit sweep.

## Scope notes

The invariant-factor count corollary is now covered at its printed conditional scope. A sorted invariant-factor presentation is an explicit input of that statement. Existence and computation of such a presentation are not claimed by the corollary's proof.

The new primary construction is noncomputable. Source-owned declaration totals include generated helpers and are not independent-theorem or novelty counts.

## Reproduce

From Linux or WSL with Python 3 and the pinned portable runtime:

```bash
bash scripts/run_block03.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output
```

The output directory must not exist. The launcher rebuilds all 28 project modules into that empty directory, resolves the declaration maps, executes the source-owned gate, replays each module serially, and runs the positive and rejection controls. Do not run `lake update`.
