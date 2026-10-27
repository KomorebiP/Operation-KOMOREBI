# AVOC v0.15.0 — development failures and repairs

The following failures occurred during this turn and were not counted as successful verification. Final source proofs pass. This is not a claim that the first scripts worked without revision.

## Environment and baseline recovery

- An interactive `session_name` container call failed because streaming sessions were unavailable. Ordinary bounded execution calls worked.
- The original portable runtime was reconstructed from its seven preserved ZIP parts. Every part and the assembled payload passed their integrity checks.
- An initial baseline compilation call encountered an outer host execution limit while entering a module. The unfinished target and remaining baseline targets were rerun. Those initial records are distinct from the final fresh 76-target rebuild.
- A development Lean call exceeded an outer host limit during difficult elaboration. Its remaining Lean child was explicitly stopped. The incomplete call has a log but no passing record and is excluded from the final build summary.

## Proof script repairs

1. **Finite-sum normalization.** A redundant `Finset.sum_add_distrib` rewrite failed after an earlier simplification had already distributed the sum. The redundant rewrite was removed.
2. **Underconstrained inequality elaboration.** Implicit arguments and placeholders around `add_le_add_left` caused a type-inference/heartbeat failure. Raising the heartbeat cap was not a satisfactory solution. The final proof supplies the correct expression types and uses the properly oriented `add_le_add` step; it compiles quickly with a modest explicit heartbeat setting.
3. **Missing import.** `abs_mul` was unavailable in the first guarded model file. A targeted absolute-value/ring import repaired it.
4. **Sum syntax.** An unparenthesized summand caused later occurrences of the bound index to parse outside the intended finite sum. Parentheses fixed the definition. Failed elaboration placeholders were never accepted as proofs; the final positive source has none.
5. **Finite-maximum inference.** An underspecified `Finset.le_max'` application left a typeclass metavariable unresolved. An initial edit did not address the offending application. The final proof explicitly unfolds the relevant table expression and supplies the finite set.
6. **Overaggressive simplification.** First-pass example proofs unfolded whole controller/channel records, eliminating named forms needed by later rewrite lemmas. Explicit `change` and local rewrites repaired the examples.
7. **Warnings treated as errors.** A deprecated `if_false` spelling was replaced with `ite_false`; an unnecessary sequence tactic was replaced by explicit branches. Neither warning was ignored.
8. **Function equality.** A partially applied transport-budget function did not simplify as an argument to another definition. A `funext` equality supplied the needed rewrite.
9. **Rare-example computation.** A monolithic `norm_num` reached the recursion limit. The calculation was split into separate common/rare branch lemmas, then combined by exact rational arithmetic.

## Evidence tooling repair

The first inventory-script edit accidentally selected a nonexistent v0.15 baseline inventory instead of the preserved v0.14 index. The path was corrected before generating the final inventory. The independent per-module census and complete kernel axiom name audit subsequently verified all 734 names.

## What did not happen

- No failed proof was admitted with `sorry`, `admit`, a project axiom, `native_decide`, or an unsafe declaration.
- No import failure or timeout was counted as a successful negative test.
- No stale initial/development compilation was substituted for a final current-source compilation.
- No source theorem about a real LLM's calibration or efficient planning was claimed from finite examples.
- The rare-branch instability was not 'fixed away': it remains a proved positive-library boundary example and a negative test against pointwise overstatement.

The final fresh build, exact name audit, negative suite and source checks all pass. Development logs remain under `results/v0.15.0/`; see `VERIFICATION_v0.15.0.md` for the accepted evidence set.
