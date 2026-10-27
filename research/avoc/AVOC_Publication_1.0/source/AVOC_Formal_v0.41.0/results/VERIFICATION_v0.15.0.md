# AVOC v0.15.0 — verification record

## Final result

**PASS: 76/76 fresh local compilation targets, 734/734 theorem axiom reports, 24/24 substantive negative rejections.**

- New theorem/lemma declarations: **55** in seven modules.
- Total theorem/lemma declarations: **734** (679 inherited + 55 new).
- Non-audit modules: **75**, plus aggregate `AVOC.lean` as a compilation target.
- Non-audit Lean source lines: **12,402**.
- Definition-like declarations: **287**.
- All **68** inherited non-audit modules are byte-identical to the frozen v0.14 archive.
- Previous audit-only corollaries remain outside the release count.

Counts include supporting lemmas and examples, not independent discoveries.

## Compiler and dependencies

Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.

mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The portable kit was restored from all seven original parts. Part CRC/SHA and full assembled SHA checks passed. The assembled SHA-256 is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`. Assembly evidence is in `v0.15.0/runtime_assembly.log`.

All nine dependency checkout revisions match the frozen manifest; the final audit reports no tracked dependency worktree changes. The external binary cache was retained. This is **not** a fresh source rebuild of mathlib or an independent Lean kernel.

## Fresh local compilation

After development and all final Lean source changes, only this project's local `.lake/build` was removed. Every one of the 76 local targets was recompiled in import order, in bounded calls, with `-j1 -DwarningAsError=true`. No older development compilation replaces a final target.

Every final record has return code zero, no timeout, identical pre/post source hashes, a matching current source hash, matching log hash and matching output hash. `v0.15.0/final_local_build_summary.json` names all records. Final logs begin `clean_`; earlier development and initial-baseline logs have different prefixes.

## Full axiom and source audit

`AVOC/FullAudit.lean` reports exactly all 734 expected fully qualified names. Its checked source and output log hashes are recorded. The dependency union is only:

    propext
    Classical.choice
    Quot.sound

There are no custom/project axioms or native-evaluation axioms. A comment-aware positive-source scan finds no `sorry`, `admit`, `native_decide`, `axiom`, or unsafe declarations. The independent per-module census agrees with the complete declaration inventory.

The usual compiler/kernel/dependency-cache trust boundary remains. Ordinary theorem assumptions, such as channel validity, exact guard matching, residual bounds and original checker soundness, remain explicit; the axiom audit does not prove empirical premises.

## Negative tests

All **24** deliberately invalid files fail substantively, with no import/setup/parser failure, timeout, or deprecated-lemma warning counted as a mathematical rejection. New tests:

- `FalseAverageIsPointwise.lean` attempts to impose the average bound on the rare posterior branch. The positive library proves the obstruction; the attempted proof reduces to `False`.
- `FalseIgnoreBackupResidual.lean` attempts to erase the example's nonzero `1/15` residual. The goal reduces to `False`.
- `FalseLearnedPolicyNoRegret.lean` attempts to assert zero regret where the positive library proves `1/10`. The goal reduces to `False`.

`v0.15.0/negative_summary.json` aggregates both executed batches. Failure of a script is not itself a proof of the negation: the corresponding positive obstruction/equality statements are also kernel-checked.

## Independent exact regression

`python checks/test_model_bridge.py` uses exact `fractions.Fraction` arithmetic on two worlds and two observations. Priors and each channel row use Bernoulli parameters from `{0,1/4,1/2,3/4,1}`.

- **15,625** joint/predictive/mean-posterior/continuation comparisons.
- **15,625** posterior-quantization/codec comparisons.
- **6,500** zero predictive entries exercised.
- **255** deterministic action sequences enumerated for horizons 0 through 7.
- **56** model-Q error checks.
- **3** invalid probability rows rejected.

The rare branch has probability `1/200`, posterior L1 error `2`, and probability-weighted average error `1/50`. The imperfect model has actual regret `n/10`, and the derived conservative bound holds. The model example has genuine reward error and nonzero backup residual; it is not a zero-error identity example.

The regression is bounded implementation evidence, not a substitute for the general Lean proofs, not a Lean-extracted implementation, and not an experiment on real LLMs. It does not claim full adaptive-tree enumeration for the new Bayesian grid. Historical v0.14 protocol regressions are retained as historical evidence, not freshly rerun here.

## Reproduction and provenance

See `../REPRODUCE.md`, `../AUDIT.json`, `../SOURCE_PROVENANCE.json`, and the records under `v0.15.0/`. `tools/summarize_v015.py` checks current build/axiom/negative/regression evidence, source identity and dependency revisions before writing the PASS summary.

The input v0.14 ZIP SHA-256 is `03468d75ddf6c5d2af93e7446a064f851210813d24828e688b9d86c19becf2e0`.

Final packaging integrity is checked separately. File hashes and ZIP CRCs are not substitutes for proof verification.
