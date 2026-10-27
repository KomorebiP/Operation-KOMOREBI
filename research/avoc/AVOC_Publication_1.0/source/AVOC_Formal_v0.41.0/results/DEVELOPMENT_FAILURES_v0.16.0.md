# AVOC v0.16.0 — failures, corrections and remaining risks

These are actual development failures and review-driven corrections, not examples relabeled as successful proofs.

## Lean proof and elaboration failures

1. The first induction proof for the natural-deduction checker used underconstrained formula placeholders when applying projections or implication hypotheses. Lean did not infer the intended conjunction/implication/disjunction/falsity. Explicit constructors repaired those goals.
2. Initial receipt-equality proofs needed corrected equality orientation and explicit Option cases. The final proofs use the executable gate's exact conjunction characterization.
3. A monadic `Except` formulation of JSON acceptance did not simplify as intended. It was replaced with explicit result cases and a theorem about the resulting exact parse/check output.
4. A reserved identifier in an early parser draft was replaced. An early batch driver assumed an unavailable JSON-printing method, and then had an underconstrained lambda/result type. It now has explicit types and prints the finite Boolean output format.
5. The final `source_artifact_consistent` proof initially supplied the original parse equality after case splitting had already rewritten the goal to a reflexive equality. Lean rejected that argument. Replacing it with reflexivity repaired the proof. BindingCodec, its dependent modules and both drivers were recompiled afterwards.
6. A legal function named `admit` conflicted with the repository's deliberately conservative shortcut scanner. The new formal transition was renamed `consume`; no proof-admission shortcut was used. Existing inherited source was not changed.

## Independent test failure

The first Python binding-differential fixture retained shared object aliases when deep-copying an in-memory request. Mutating the supposed receipt also changed the current/pending identity in the fixture, so a supposed negative case became a legitimate matching request. A JSON round trip now creates independent wire-data occurrences, matching actual serialized input. The test was rerun and all 35 final cases passed. The checker was not altered to accommodate the faulty test expectation.

## Resource interruptions

An earlier build chunk and a final negative chunk reached outer host limits. Processes were checked before resumption, and unfinished targets were rerun. Final records have current hashes, completed return codes and no timeout. These interruptions are not proof rejection evidence.

## Admission hardening from review

The first runtime admission path checked live input identity before proof execution. Review showed that a persistent source change during checking should be detected before commit. A second exact capture was added after the proof and binding executions. A test now mutates the live candidate from inside a checker invocation and confirms rejection. This is a bounded race-hardening test, not a proof against a hostile OS or every TOCTOU pattern.

## What was intentionally not attempted

No arbitrary user Lean source is executed as certificate data. Such a backend needs a separate isolation and theorem/type/environment audit design. The present language is a small propositional certificate grammar. Receipts are not signatures, the host/store remain trusted, and no full stochastic-equivalence theorem is asserted for receipt filtering. See `PROOF_BOUNDARY.md`.

## Packaging filename correction

The first packaging helper used `Path.with_suffix` on a dotted version-directory name and produced `AVOC_Formal_v0.16.zip`, omitting the final `.0` version component. The output naming was corrected to append `.zip` to the full directory name. The manifest and ZIP were regenerated and rechecked under `AVOC_Formal_v0.16.0.zip`. This was a filename bug, not a failed proof or checksum check.
