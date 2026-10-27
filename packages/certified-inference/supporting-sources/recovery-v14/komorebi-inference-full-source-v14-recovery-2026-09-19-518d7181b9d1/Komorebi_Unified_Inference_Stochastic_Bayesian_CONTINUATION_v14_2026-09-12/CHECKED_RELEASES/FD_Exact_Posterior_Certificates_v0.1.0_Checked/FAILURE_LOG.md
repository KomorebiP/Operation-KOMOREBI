# Failure log

Failed or interrupted attempts are not counted as successful theorem checks.

## Execution/environment failures

- Streaming execution was unavailable. No Lean process ran in that attempted streaming invocation.
- An initial outer call ended without a RationalMatrixCertificates completion receipt. The leftover child process group was explicitly killed. A broad tactic import was removed; the final bounded build passed.
- FDGaussianKernel reached its 40-second process cap while an earlier build was still active. Its serialized retry passed; only the successful final receipt supplies the retained output hash.

## Corrected draft compilation failures

The completed failed checks are listed below. RC=1 entries were import/API, proof-elaboration, or warnings-as-errors failures; RC=124 is the resource timeout.

| Module | Exit | Seconds | Receipt |
|---|---:|---:|---|
| FDGaussianKernel | 124 | 40.001 | `audit/20260912T044453955305Z/FDGaussianKernel.json` |
| RationalMatrixCertificates | 1 | 4.528 | `audit/20260912T044613507607Z/RationalMatrixCertificates.json` |
| RationalMatrixCertificates | 1 | 3.233 | `audit/20260912T044735292369Z/RationalMatrixCertificates.json` |
| RationalPacketCertificates | 1 | 2.377 | `audit/20260912T044923146602Z/RationalPacketCertificates.json` |
| RationalPacketCertificates | 1 | 2.721 | `audit/20260912T045033980846Z/RationalPacketCertificates.json` |
| RationalCertificateChecker | 1 | 2.771 | `audit/20260912T045153554309Z/RationalCertificateChecker.json` |
| GramNoiseFloor | 1 | 19.422 | `audit/20260912T050151234154Z/GramNoiseFloor.json` |
| RationalModelSemantics | 1 | 12.19 | `audit/20260912T050314658006Z/RationalModelSemantics.json` |
| PosteriorEnclosureBounds | 1 | 18.026 | `audit/20260912T050438516324Z/PosteriorEnclosureBounds.json` |
| RationalPosteriorCertificate | 1 | 19.398 | `audit/20260912T050608798143Z/RationalPosteriorCertificate.json` |
| GeneratedExactScalar | 1 | 2.398 | `audit/20260912T050730787831Z/GeneratedExactScalar.json` |
| GeneratedExactScalar | 1 | 10.109 | `audit/20260912T050848093779Z/GeneratedExactScalar.json` |

Corrections included rational cast/sum imports, explicit unused-section-instance omission, the pinned matrix-notation import path, a nondeprecated application lemma, inequality argument ordering, and explicit rational-to-real tolerance simplification.

Concrete exact checks initially used elaborator reduction, which could not reduce the imported finite rational expressions. The final proofs use `decide +kernel`: kernel reduction, not native evaluation. All final instance theorems compile and are included in the axiom audit.

## Negative-control diagnostics

The first forged-certificate control was rejected, but its diagnostic described a failed reduction. The final control first rewrites by the separately kernel-proved rejection theorem and then attempts the false Boolean equality. Both the initial and final records are retained. Negative controls are deliberate rejections, not release failures.

## Verification tooling

The official Mathbox manifest validator executable was unavailable. `audit_integrity.py` verifies the project receipts, source/compiled-output/dependency hashes and complete axiom coverage. It was run successfully; no official-validator run is claimed.

No failed draft is labeled checked. The final receipt records all 51 successful active modules and all 232 audited theorem/lemma declarations.
