# AVOC v0.16.0 — final verification record

**Result: PASS.** Recorded UTC: `2026-09-12T04:22:56.370312+00:00`.

| Check | Final result |
|---|---:|
| Inherited theorem/lemma declarations | 734 |
| New declarations | 62 |
| Complete axiom-audited declaration inventory | 796 |
| Non-audit AVOC modules | 81 |
| Non-audit Lean source lines | 13,204 |
| Definition-like declarations | 333 |
| Current local compilation targets | 84 / 84 |
| Complete axiom reports | 796 / 796 |
| Deliberately invalid files substantively rejected | 28 / 28 |
| Unchanged inherited non-audit modules | 75 / 75 |
| Forbidden positive-source proof shortcuts | Zero |

Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Nine dependency revisions match. The union of axiom dependencies is `propext`, `Classical.choice`, `Quot.sound`. No new project or native-evaluation axiom appears.

The 84 targets comprise 81 non-audit modules, aggregate `AVOC.lean` and two trusted checker drivers. Local outputs started empty. Every final target has a current-source successful result; a final source-consistency lemma repair was followed by recompilation of its dependent modules and drivers. External binary caches were retained. This is not a fresh mathlib source build or an independent kernel validation.

One development build slice and a final negative-test slice were interrupted by outer host limits. No interrupted result was counted as success. No remaining Lean child was observed before rerunning the unfinished part. The final collector verifies every required source, output and log hash and every non-timeout return code.

## New formal declarations

Six modules: `CertificateLogic`, `ArtifactBinding`, `CertificateCodec`, `BindingCodec`, `CertificateResearch`, `ArtifactExamples`. The executable checker and binding function themselves are the subjects of the soundness lemmas. The source parser theorem connects the exact retained candidate string to the parsed derivation. The controller adapter proves admission/budget safety, not unchanged probabilistic policy value after receipt filtering.

## Expected negative cases

All 28 invalid files reached their intended proof obstruction. New cases: false empty-context certificate soundness, changed candidate-source acceptance, receipt replay, and changed environment acceptance. Import errors, parser/setup errors, timeouts and merely stale logs are excluded by the evidence collector.

## Independent runtime regression

- 6,363 proof requests compared with an independently implemented inference function.
- 692 semantic implication checks across the finite Boolean valuations used by the test.
- 35 exact ticket/binding cases.
- 21 real-file workflows: 2 positive workflows and 19 expected rejections.
- 20 actual single-request checker invocations in those workflows.

Positive paths register, check and consume a root identity proof and a dependent proof. Rejections exercise changed exact candidate/target text, replaced pending generations, replay, environment drift, task substitution, dependency-version drift, forged dependency proof/approval, missing/self dependencies, unsupported code-like proof tags, duplicate fields, bad atoms, locks, symlinks and changes during admission.

These tests do not prove Python/IO correctness universally or evaluate real LLMs. The general mathematical claims are the separate Lean theorems. `artifact_gate_regression.json` records source hashes, request hashes, actual checker exit codes and outputs. The current verifier checks those source hashes before reporting PASS.

## Provenance

Frozen v0.15 ZIP SHA-256: `c7dae6f260e14d183cb52a3e9ee9bdb91f167adff6ea445ee099c1d65b4f0e8b`. Every inherited non-audit module was compared directly to that archive. Original v0.15 top-level documentation is preserved under `provenance/v0.15_documentation/`. Historical evidence is retained in its original version directories.

`AUDIT.json` and `results/v0.16.0/verification_summary.json` are the final current-run summary. Packaging checks are additional byte-integrity evidence and do not replace compilation or semantic review.
