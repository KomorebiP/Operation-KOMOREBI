# AVOC v0.32.0 — verification record

## Result

**PASS within the declared theorem and bounded executable scopes.**

- 36 new theorem/lemma declarations; 1,692 total.
- 176/176 current local compilation targets passed from an empty local build directory.
- 1,692/1,692 exact-name axiom reports passed.
- Axiom union: `propext`, `Classical.choice`, `Quot.sound` only.
- 91/91 deliberately invalid Lean files were substantively rejected.
- 152/152 inherited non-audit modules are byte-identical to v0.31.0.
- Positive-source scan found no `sorry`, proof `admit`, project `axiom`,
  `native_decide`, or unsafe theorem-like declaration.

## New source

- `AVOC/AdaptiveProbeControl.lean`: uniform finite-catalogue Bayesian probe control,
  executable Bellman correspondence, legal/optimal adaptive plans.
- `AVOC/AdaptiveRankProbe.lean`: exact 2x2-minor/rank specialization.
- `AVOC/AdaptiveProbeCodec.lean`: bounded GF(5) JSON interface.
- `AVOC/AdaptiveProbeExamples.lean`: kernel-checked catalogue probabilities and
  immediate-value examples.
- `tools/AdaptiveProbeMain.lean`: executed single/batch entrypoint.

## Independent executable regression

The Python oracle uses determinant outcome tables and exact `Fraction` dynamic
programming, rather than reproducing the Lean definitions.

- 322 supported catalogue/history requests compared exactly.
- 206 returned a probe rather than stop.
- 6 malformed or zero-probability requests were rejected.
- 3 hand-audited examples passed: base adaptive plan, posterior-after-failure,
  and unequal-fee action change.

This regression supports the codec and runtime. The universal policy optimality
statement is established separately by Lean.

## Toolchain

Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`;
mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; nine exact cached dependency
revisions. External dependency sources were not rebuilt.

## Interpretation boundary

The catalogue, fees and terminal benefit are model inputs. The result does not
calibrate real workloads, prove noisy probe reliability, infer exact rank from
failed probes, or establish physical speedup or production-LLM usefulness.
