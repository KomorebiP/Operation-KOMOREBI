# Main paper: final mathematical self-review

Mode: conservative self-review, read-only manuscript review. Date: 2026-10-07. The parent author owns source edits and the final rebuild. Reviewed `manuscripts/main.tex` against the preserved `historical_companion/Komorebi_Theorem_Companion_Source/theorems.tex`, using the changed hunks produced by `scripts/build_main.py` and surrounding definitions, proofs, result index, and evidence-status prose. The earlier adversarial audit is separate; this pass does not reopen unchanged proofs or constitute a new independent proof audit.

## Findings

No unresolved mathematical or LaTeX issue remains in the reviewed changed hunks.

- **Resolved during review — C03 combined lower-bound wording.** The initially generated source retained “one-packet bound … gives only `n−1`.” The parent corrected the generation script and regenerated the manuscript. The current paragraph after Corollary `cor:family-cost` explicitly displays `max{0,deg F_k−1,2 max_ell alpha_1(F_k+ell)−3}` and states that its immunity-only term is 3. This agrees with the proved values and adjacent table.
- **Validation timing — final rebuild still required.** The existing `build/main/main.log` contains no LaTeX warning, package warning, overfull/underfull box, or error line. It predates the currently reviewed `main.tex`, which includes the C03 clarification and latest reproduction-paragraph edit. This review did not recompile; the parent should rebuild the final source before treating that log as validation of these final bytes.

The new register-product statement and proof match the local `workspaceDegree_initial`, `workspaceDegree_toggle`, and `workspaceDegree_run` conventions. The list can contain repeated wire indices; target repetitions are reduced by Boolean idempotence; the remaining length satisfies `|R|+1≤r`; NOT/CNOT add no budget and Toffoli adds at most one. The empty list produces the constant-one function. Arbitrary affine initial coordinates are covered by the formal initial-invariant hypothesis. The cited coordinate specialization fixes either boundary target bit and does not assume clean intermediate states.

The nonzero condition is correctly attached to the minterm minimum/maximum formulas while the preceding monomial-basis and positive-point statements remain valid for the zero function. The scalar-summary paragraph correctly separates `m≥1` loss from the unique empty witness at `m=0`. The conditional SAT proposition retains explicitly represented characteristic-two fields of polynomial size and a uniform exact evaluator on verifier descriptions. The disjoint factorization statement uses `P_A(z_u)P_B(z_v)` and its proof sums each factor over its own variable block. Both overlap inequalities retain their needed conditions, `z≠0` and `z²≠z`.

No stale claim of fresh Lean success was found. The front matter and evidence appendix distinguish the archived Block 02 verification from this edition's failed compiler-environment attempt. C02's dual and C03–C08 are not promoted to Lean proofs. The generic XOR–AND degree lemma remains separate from the formally scoped NCT register theorem. The conditional evaluator remains explicitly unimplemented.

## Mathematical-token changes in the edition diff

This reviewer made **no mathematical-token change and no source edit**. The following mathematics-bearing changes made by the parent author were inspected:

1. **Added `thm:register-products`.** New quantifiers over affine initial register contents, a finite repeated-index list `L` of length `r`, and `t` counted Toffolis; conclusion `deg(product_{i in L}s_i)≤t+r`. Its proof adds the target-removal list `R`, control count `q∈{0,1,2}`, two-term Boolean expansion, and `max{q−1,0}` budget increment.
2. **Restricted `thm:monotone` consequences.** Added the hypothesis “for nonzero `f`” immediately before the minterm formulas for `alpha_1(f)` and `beta(f)`. This avoids undefined empty extrema without changing the preceding ideal or pointwise formulas.
3. **Corrected scalar-loss boundary after `cor:scalar-eval`.** Added `m≥1` for loss of another singleton and the explicit `m=0` identity/evaluation exception. The dimension theorem and evaluation classification are unchanged.
4. **Clarified C03's combined lower bound.** Replaced the ambiguous attribution of `n−1` with the explicit degree/affine-immunity maximum and the immunity-only value 3. No claimed bound value or adjacent family formula changed.
5. **Added numerical/formal scope in front matter and evidence prose.** The statements `deg f≤T+1` and `2 beta*(f)≤T+3`, the 115-declaration inventory, and exact fresh bounded ranges are attached to their stated evidence categories. The index includes the new invariant as a supporting statement rather than a ninth claim group.

The efficient-field condition, ordinary formal `z` variables versus Boolean `w` reduction, and own-variable-set disjoint factorization were preserved from the historical theorem companion; they are not newly changed mathematical tokens. Formatting, author-order, version, and reproduction-path changes are nonmathematical editorial changes.

## Local validation and coverage

A read-only parser check found exactly **30 numbered theorem/lemma/proposition/corollary/counterexample environments** and **30 unique result-index entries**, with the same order and a bijective label match. No duplicate labels, missing literal references, or missing bibliography keys were found. The apparent `#1` reference in a naive scan is the `resultrow` macro parameter and is not an undefined document reference.

Reviewed source SHA-256:

`17d606cc2d03f04340a6a7a7da950517392abc1bd84ad7e3d2cab5b9c9495f9e`

Coverage is the edition diff plus enough unchanged context to check notation, dependencies, conditional hypotheses, finite ranges, the complete 30-entry index, and stale formal-status wording. Original archived proof files were not modified. A new compiler replay, a new visual PDF pass after the final edits, and a fresh Lean run were not performed by this reviewer.
