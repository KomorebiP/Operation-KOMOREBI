# AVOC v0.27.0 — current verification record

## Result and exact counting

**PASS: 150/150 current local compilation targets, 1,447/1,447 theorem axiom reports, and 71/71 substantive negative proof rejections.**

The release has 1,393 inherited declarations and 54 new declarations, including helpers and examples. There are 135 non-audit AVOC modules and 21,625 non-audit Lean source lines. This is not a count of independent discoveries.

- `AVOC/SemanticCostCertificate.lean`: 6 declarations.
- `AVOC/BooleanCostClosure.lean`: 20 declarations.
- `AVOC/SemanticLibrary.lean`: 18 declarations.
- `AVOC/SemanticLibraryCodec.lean`: 2 declarations.
- `AVOC/CostCertificateExamples.lean`: 8 declarations.

## Source and dependency provenance

The baseline is the semantic-feedback v0.26 archive, SHA-256:

`94557b17c46a6e0258de4ccdd959b71772192d1f39081d27551dae8956f885e2`

Its original 6,862-entry payload manifest passed before changes. The 130 inherited non-audit Lean modules are byte-identical. The alternate v0.26 learned-rewriting branch is not merged or added to the theorem count.

The current local build directory began empty. Each final successful compilation record binds its exact source bytes, imported local output hashes, resulting compiled output and log. All final records pass the evidence collector. Nine external dependency revisions are checked and retained at their pinned caches. Lean is 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. This is NOT a fresh source rebuild of mathlib or an independent kernel verification.

The runtime bundle's seven part CRC/SHA checks and combined hash passed during recovery. These are archive integrity checks, not an independent proof of the runtime.

## Axioms and negative tests

The full audit names every one of the 1,447 declarations. Reported foundational axioms are only:

    propext
    Classical.choice
    Quot.sound

No project-specific or native-evaluation axiom appears. The comment/string-aware positive-source scan finds no placeholders, native_decide, project axiom or unsafe declarations.

All 71 negative files fail with substantive mathematical diagnostics, no setup/import failure and no final timeout. Four new tests cover correct witnesses without cost closure, an impossible zero-cost witness, unfunded acceptance and an empty global library. Positive counterexample theorems establish the obstructions independently of failed scripts.

## Concrete data acceptance

The actual Lean importer accepted all 256 witnesses and 196,869 constructor/primitive cost inequalities. Its data SHA-256 is:

`901e8887f4190d6bcb1661ef1eceb9a9031bbabd3b81179564b5cabc9c157f11`

Witness costs total 1,640, with maximum 10. The independent Python height-layer producer and a fresh run of the existing Lean depth-three feedback generator exported identical programs. The separate size-layer bitset oracle agrees with all 256 minimum costs. Generation depth is not trusted by the global checker.

**One optional experiment did not succeed:** embedding the entire concrete table in a separate Lean source and attempting `by decide` exceeded a 30-second process cap. It was killed with no completed proof. The source and failure record are preserved, excluded from the successful theorem inventory. There is NO claim of completed standalone kernel reduction of that complete table. Instead, the general checker/global-minimum theorems are kernel-checked and the concrete checker was executed, with compiler/runtime trust stated explicitly. No native-evaluation shortcut was used.

## Independent executed regressions

- 25 actual Lean batch cases.
- 644 funded globally optimal query comparisons with an independently implemented exact-node-size oracle.
- 5,152 individual truth-value comparisons.
- 128 seeded random reference expressions among those queries, seed 20260913; all semantic classes also exercised.
- 13 protected-store cases, including two fresh-process reloads, no-overwrite behavior, partial publication, symlinks, checksum drift, false signatures/costs, a semantically valid but larger witness, and forged old approval/checksum rejection.

A correct alternative minimum witness is accepted. Historical approval metadata is not current proof authority. Queries do not regenerate candidate pools and leave saved store bytes unchanged. The publication interruption is a controlled Python exception, not SIGKILL or power-loss certification. Old live/recovery/retry suites were not rerun in this block.

## Paid revalidation demo

A fresh saved-bank query with 300,000 credit revalidates for 210,245 tariff units, charges 49+25+41=115 for three references, and returns 89,640 credit. Returned node sizes are 3,3,5. These are declared per-call tariffs, not persistent payments or complete CPU costs.

## Evidence locations

`results/v0.27.0/verification_summary.json`, `final_build_records.json`, `negative_final.json`, `full_axiom_audit.log`, `library_tests/`, `cold_lean_*`, `validated_lean_depth3.json`, `kernel_table_probe.json`, `experiments/KernelTableProbe.lean.txt`, and `saved_library/`.

The computation manifest records a timed fresh evidence-collection invocation, not the duration of all prior proof/test runs. Its validator is the inherited documented v1-only local adaptation, not full v2. Packaging hashes remain a separate integrity layer.
