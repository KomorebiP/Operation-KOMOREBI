# AVOC v0.30.0 — verification record

## Final result

**PASS: 166/166 current local compilation targets; 1,612/1,612 named theorem axiom reports; 84/84 substantive negative rejections; 1,361 executed differential requests; 17/17 new live store cases.**

The new block contains 64 theorem/lemma declarations in four modules. The cumulative source contains 148 non-audit AVOC modules and 23,297 non-audit Lean source lines. Counts include supporting lemmas and concrete examples, not independent discoveries.

## Baseline and build

The frozen v0.29 ZIP SHA-256 is:

`99da727bf29b5a2712df8f236ec1c01d7c42a46684b1b67a0b76d4ec02c97b49`

Its original internal manifest had 8,555 matched entries before modification. All 144 inherited non-audit mathematical modules remain byte-identical. Aggregate imports, full audit/index, current-version runners and current documentation are updated separately.

The new project build directory began empty. Every final local source target has a successful `lean -j1 -DwarningAsError=true` record. The evidence collector rechecks source-before/source-after, direct imported output hashes, own compiled output and diagnostic-log hashes. No historical build result substitutes for a current record.

Runtime: Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine recorded external dependency heads match their pins. The compiled external caches were retained, not rebuilt from source. This is not an independent Lean-kernel or whole-host verification.

## Theorem and negative audit

`AVOC/FullAudit.lean` names exactly the complete inventoried 1,612 theorem/lemma declarations. The union of their reported axiom dependencies is only:

`propext`, `Classical.choice`, `Quot.sound`.

The comment/string-aware positive-source scan finds no proof placeholders, project-specific axioms, `native_decide`, or unsafe declarations. Legitimate `.admit` action names are not confused with the proof tactic.

All 84 negative files have current source and import hashes, nonzero return codes, actual error diagnostics, and no timeouts or setup/import failures. The four additions challenge:

- unchanged old factors after changing the requested affine offset;
- cost-free cache validation;
- an assertion that passing optimistic preflight guarantees profitability;
- accepting a certificate for a different linear map.

The corresponding obstruction statements are proved in the positive library. Failed proof scripts alone are not taken as proofs of negation.

## Independent executed differential regression

`checks/test_affine_cache.py differential` sends actual requests to `tools/AffineReuseMain.lean`. Its separate oracle uses homogeneous augmented matrices, direct source-program execution and explicit image enumeration for small dimensions. It does not reuse Lean's normalization recursion or the proposer's row-reduction algorithm as its rank oracle.

Final range:

- 1,361 requests: 728 reuse queries, 625 preflight requests and 8 malformed requests;
- every one of the 625 two-by-two GF(5) linear matrices, with specified varied stored and query offsets;
- rectangular and zero-dimensional shapes plus additional bounded seeded inputs;
- 16,049 individual-vector comparisons;
- seed 20260913.

This is not exhaustive over every affine map/offset in every runtime dimension. The general retargeting and preflight statements are separately proved by Lean.

Both the request payload and exact stdout hashes of all twelve batch invocations are reconstructed from the preserved requests/responses and matched to the run records. The final test-source and wrapper/generator pins are current.

## New live store regression

The initially unsplit live suite exceeded its outer 90-second host limit. That partial run is excluded. After splitting, all final source-pinned groups were run from fresh temporary stores:

- `--group basic`: 6 cases;
- `--group economics`: 6 cases;
- `--group integrity`: 5 cases.

The differential suite was also rerun after the test-script change.

Cases establish actual cold publication, fresh-process warm revalidation with no proposer invocation, changed-offset reuse without modifying the saved certificate, equivalent different source syntax, cold/warm preflight stops, a profitable ten-call warm query, an unprofitable eleven-call cold search that passed preflight, identity retention, resource failures, corrupt saved offset rejection, key/descriptor drift, symlink rejection, and interrupted publication without a certificate file.

The publication interruption is a **controlled Python exception**, not SIGKILL or power failure. Store/IO/serialization is independently tested, not a universal formal refinement. The cache is not a migration of AVOC's older research/recovery stores.

## Exact modeled economics

For the rank-one 4x4 example:

- original execution tariff: 36;
- selected factor tariff: 21;
- cold setup: 240;
- warm setup with fresh revalidation: 149;
- warm ten-call modeled net: +1;
- cold eleven-call modeled net after permissive preflight: -75.

Costs are declared arithmetic/meter tariffs, not timings or all physical resource use. The remaining-opportunity theorem has an explicit implementation-class and setup-floor premise. It is not a global optimal metareasoning theorem.

## Reusable evidence

Per-source and per-negative records, raw batch requests/responses, source-pinned test summaries and demos are in `results/v0.30.0/`. `tools/summarize_v030.py` validates those records. Its manifest duration covers the collector only, not the earlier builds/tests. The included manifest validator is the inherited local v1-only adaptation; it does not authenticate the mathematical interpretation.

Historical live, crash, retry, synthesis and empirical-looking examples remain historical. No old operational suite or real LLM evaluation is claimed as newly executed here.
