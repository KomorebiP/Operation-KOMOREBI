# Block 25 development record

The target was chosen from a fresh reading of the literal Claim 9.1 and the Section 8 compatibility data. The independent scope review isolated two gaps: transferring system nonisomorphism to a selected coefficient member, and supplying actual arithmetic Frobenius coverage after finite exclusions.

The first route proves character rigidity and assembles the system-to-member implication with good-place overlap density explicit. The separator then derives member nonisomorphism and retains each coefficient prime's trace-comparison domain. A separate actual $C_2$ boundary shows that ordinary quotient coverage cannot silently replace coverage surviving finite deletions.

The second route came from the source inventory. Komorebi's exact finite-table separator explicitly leaves Chebotarev density beyond its table unchecked. The pinned Mathlib sources do prove Dirichlet's prime theorem and the cyclotomic Galois equivalence. Their transfer yields actual prime coverage for a fixed cyclotomic number field. Equality of reduction maps on the integral root-of-unity generator proves the full residue-field Frobenius action. The ramification-index theorem proves unramifiedness. Lying-over then supplies the actual prime ideals witnessing these properties.

The arithmetic result is restricted to this specified cyclotomic extension. No new axiom or unproved arithmetic density premise is used to establish its prime coverage. No general Chebotarev theorem is claimed. Consequently the source ledger remains 17 checked / 3 partial.

## Retained development failures

- `privatechecks/rigidity_dev/compile_01.log`: the dependent two-member family initially had incompatible vector-space universes, together with local-instance style and unused-hypothesis lint failures. The corrected theorem permits distinct spaces in one universe. `compile_02.log` records a documentation/`omit` placement error; `compile_03.log` passed.
- `privatechecks/coverage_boundary_dev/compile_01.log`: an unnecessary `simpa` was rejected under warnings-as-errors. Replacing it by `simp [hn]` produced the passing second compile. The deliberately false density-after-deletion control reaches the intended goal `False`.
- `privatechecks/cyclotomic_dev/`: preliminary attempts needed an explicit `Finset.le_sup` function argument, less unfolding of the cyclotomic equivalence, the `Pointwise` scope for the ideal action, and the explicit coprimality argument in the ramification lemma. The final `compile_06.log` passed. API probes containing guessed names are discovery records, not verification evidence.
- `privatechecks/cyclotomic_system_dev/`: the concrete conductor-four field needed an explicit cyclotomic-extension instance. A later compile rejected `letI` where the proof-style linter required `let`; the corrected `compile_03.log` passed.
- `privatechecks/system_dev/` retains the overlap and system-separator development attempts and their final logs. They record tactic and elaboration revisions, not counterexamples to the source theorem.
- `privatechecks/cyclotomic_primes_dev/compile_01.log` records the same `letI` proof-style failure in the prime-ideal witness module. The corrected `compile_02.log` passed; its declaration check also passed.

The mathematical claims are universal Lean statements. No new bounded experiment is offered as their proof; the retained exact quadratic experiment belongs to a predecessor block.

**Final verification passed.** All 161 production modules passed the clean build. The 1,904 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 48 theorem/lemma declarations and 12 other named declarations; the cumulative theorem/lemma count is 1,333. Nine positive controls passed, and 23 false claims plus the placeholder were rejected as intended. All 153 predecessor source and rebuilt proof-object hashes match Block 24. Fresh archive replay reproduced all eight new proof objects and the retained Block 22 exact regression.

Independent audit compiled all eight exact final modules from the frozen 153-object baseline and audited all 60 new named declarations. Its development-only edge fixture failures are preserved with their corrected passing versions in `checks/claim91_audit/`. No production proof defect was found. Separate reviews confirmed the actual arithmetic Frobenius and prime-ideal existence results.

The manuscript patch was applied to a fresh predecessor copy and reproduced exact final bytes; lexical structure and mathematical proofreading passed. Original Claim 9.1 and its proof remain unchanged. No PDF was typeset.
