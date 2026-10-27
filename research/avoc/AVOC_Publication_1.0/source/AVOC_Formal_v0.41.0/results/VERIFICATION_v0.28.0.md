# AVOC v0.28.0 — final verification

## Summary

- 52 new theorem/lemma declarations; 1,499 cumulative declarations, including helpers and examples.
- 140 non-audit AVOC modules; 22,218 non-audit Lean lines.
- 156/156 final local compilation targets pass with warnings treated as errors.
- 1,499/1,499 exact-name theorem axiom reports pass; union is propext, Classical.choice, Quot.sound.
- 75/75 invalid files are substantively rejected, including one explicit dimension/type error. Missing imports and timeouts are not counted as successful negative tests.
- 135/135 inherited non-audit modules are byte-identical to the supplied v0.27 ZIP.
- Positive-source scan finds no proof placeholders, project axioms, native-evaluation shortcuts or unsafe declarations.
- Nine exact dependency heads were checked. The portable runtime assembly verified all seven part checks and its combined SHA-256.

The local output directory began empty after the prototype checks. The complete local graph was rebuilt against pinned cached dependencies. An interrupted slice was resumed only after confirming no child remained. The final collector validates current source hashes, direct-import output hashes, output hashes and log hashes. The result is not a fresh source rebuild of mathlib or an independent kernel implementation.

## Executed new-domain regression

The final independently implemented Python oracle uses exact arithmetic modulo five. Normalization uses homogeneous augmented matrices; input evaluation independently walks the original AST.

- 1,137 actual Lean requests.
- 937 complete-equivalence comparisons, including all 625 pairs of scalar GF(5) affine maps.
- 185 normalizations with coefficient, offset, output and cost-accounting comparisons.
- 7,120 input-vector cases; exhaustive vectors for each sampled input dimension <=3, finite samples for larger dimensions.
- 15 malformed/unsupported requests rejected, including shape errors, wrong composition dimensions, invalid residues, nonlinear syntax and bound violations.
- Deterministic seed: 20260913.
- Test and source hashes agree before/after. Fresh final tests were run after local rebuild.

`results/v0.28.0/affine_tests/summary.json` records commands, return codes, timings and source pins. Batch requests and raw replies are retained next to it. `demo_fusion.json`, `demo_bottleneck.json`, and `demo_compare.json` are additional actual CLI outputs.

These tests are bounded implementation evidence. The general all-input, all-dimension ring theorems are separately kernel checked. Old live-artifact, crash, store and retry experiments remain historical and were not rerun.

## Strongest declarations

- Komorebi.AVOC.Affine.eq_of_zero_basis
- Komorebi.AVOC.Affine.check_iff
- Komorebi.AVOC.Affine.normalize_correct
- Komorebi.AVOC.Affine.checkProgram_iff
- Komorebi.AVOC.Affine.context_congr
- Komorebi.AVOC.Affine.context_cost_mono
- Komorebi.AVOC.Affine.lower_bound
- Komorebi.AVOC.Affine.attained_global_minimum
- Komorebi.AVOC.Affine.worthwhile_certificate

Source and artifact hashes, not this prose alone, determine current run provenance. See verification_summary.json and REPRODUCE.md.
