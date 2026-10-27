# AVOC v0.26.0 — verification record

**PASS.** 144/144 current local compilation targets, 1,393/1,393 complete-name theorem axiom reports, and 67/67 substantive negative rejections.

## Source and trust

Baseline archive SHA-256: `543afa90b23ec54910abe46348fd82abb3b98582092b7e2e19e8713a2d005707`.

The original v0.25 manifest had 6,257 matching entries. All 123 inherited non-audit modules are byte-identical to that ZIP. The release adds 83 declarations in seven new modules, yielding 1,393 declarations, 130 non-audit AVOC modules, and 20,894 non-audit Lean lines. Counts include examples and helpers.

Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine package revisions match. The portable runtime was assembled from its seven already available parts, with part CRC/SHA and combined archive SHA checked. The local project output began empty. External binary caches were retained, not rebuilt from their full sources.

Every final local compilation has return code zero, no timeout, warnings as errors, unchanged source/import inputs, and matching output/log hashes. `FullAudit.lean` names all declarations. The exact name set matches the census and only `propext`, `Classical.choice`, and `Quot.sound` occur. The independent comment-aware source scan has zero forbidden proof shortcuts.

## Negative tests

The 63 prior files remain, plus four semantic-library cases. All 67 fail substantively with no import failure or timeout:

- one-sample agreement is not semantic equivalence;
- a larger equivalent representative is not no-larger;
- zero credit does not create a funded bank;
- the compressed next layer does not have the old full raw count.

Positive library examples separately prove the relevant counter-statements. Failure of a proof script alone is not treated as universal mathematical negation.

## Executed comparison

`checks/semantic/protocol.json` freezes the comparison before the main regression. Both arms use the same full eight-input semantics, grammar constructors, stable index, and tariff. Frozen expansion uses raw preceding lists; feedback expansion uses retained representatives.

Matched depths 0,1,2 have identical truth-table signatures and optimum node counts. All 256 query functions are included at each tested build. The feedback-only depth-3 extension attains all 256 truth tables; the huge frozen depth-3 pool was not executed.

| Cumulative depth-2 metric | Frozen | Feedback |
|---|---:|---:|
| Emitted entries | 21,935 | 991 |
| Node mass | 144,885 | 5,081 |
| Index probes | 306,154 | 26,870 |
| Retained semantics | 109 | 109 |
| Structural charge | 4,226,171 | 293,631 |

Depth-3 feedback: emitted 36,852; node mass 402,945; probes 3,337,060; retained 256; charge 34,099,842.

Median process-inclusive depth-2 times from three runs each: frozen 1.762176233 s, feedback 0.996792104 s. Small descriptive sample, fixed alternating order, no randomness. Do not equate the 14.4x structural tariff ratio with physical speedup.

## Regression size and actual command lines

The independent Python oracle uses integer truth bitsets and dictionary signatures, not the Lean feedback recursion. Actual Lean requests validate 1,792 query cases, 32 budget cases, 512 equivalence cases, 27 campaigns, and 12 malformed wire cases. `tools/record_semantic_cli.py` adds 12 executed wrapper cases. Four succeed with explicitly supported statuses and eight reject invalid configurations.

The fresh CLI campaign returns the generated three-node conjunction for a six-node equivalent reference. Search/query/promotion/switch spending is 293,631 + 10,520 + 80 + 1 = 304,232. With one million declared deployment calls, modeled net is 2,695,768. That workload is illustrative, not measured future demand.

The budget CLI requests depth 3 with 10,000,000 credit, attains depth 2, and retains 9,706,369 credit. No requested-depth completion is fabricated.

All request/output/stderr hashes and source-before/after pins are retained under `results/v0.26.0/semantic_tests/` and `cli/`.

## Limits

No current rerun of the older filesystem/crash suites is claimed. The new runtime is read-only/in-memory. Structural tariffs omit general physical costs. The test is a finite synthesis ablation, not autonomous self-modification, a production model evaluation, a novel identity discovery, or a benchmark against all alternative synthesizers.

Current summary: `results/v0.26.0/verification_summary.json`. Detailed build, import, source, output, axiom, and negative logs are in the same directory. `tools/summarize_v026.py` rejects stale evidence before packaging.
