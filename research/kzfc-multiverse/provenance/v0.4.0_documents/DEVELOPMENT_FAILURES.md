# Development failures and repairs v0.4.0

## Current block

1. The fresh environment contained the seven archived runtime parts but no extracted compiler. The exact archive was restored and its concatenated SHA-256 verified. A streaming container session was unavailable, so ordinary processes and explicit result inspection were used.
2. FilterExtension's first compilation exposed opaque-definition elaboration problems. Explicit `change` statements aligned the goals for Holds, and explicit finite-set proofs replaced attempts to infer finiteness of opaque scopes. No mathematical hypothesis changed.
3. ConeFilter's first compilation could not infer the set type for a union inside a cardinal expression. An explicit Set I annotation fixed the inference.
4. ResidualClassification's first compilation lacked the import defining the Sound interface. The missing import was added. There was no assumed proof placeholder in the source.
5. SuccessorObstruction's first compilation was rejected by the unnecessarySimpa linter under warnings-as-errors. `simp` replaced `simpa`. The proof statement and argument did not change.
6. Two synchronous enclosing tool calls interrupted complete-verification attempts, although the build and source checks reached before each interruption had passed. Their logs are retained under verification/interrupted_driver and verification/interrupted_recorded_driver. A detached process, polled to completion within this interaction, ran the whole verifier and recorded the actual zero exit status. This was an execution interruption, not a mathematical counterexample.
7. The interrupted rerun exposed a stale-output risk: a previous RESULTS.json could remain at the active path while a new run was incomplete. The verifier now removes stale verdict and coverage files at startup, and the recording wrapper removes its old process record. The complete final run was repeated after this repair. Its actual process exit is recorded in verification/process_record.json.

Raw failed compilation attempts remain under verification/*attempt_1.log. No repair added a custom axiom, proof placeholder, native proof shortcut, or suppressed linter.

## Mathematical outcome and correction

The new class-level theorem identifies the specified candidate with complete filter extension and the fine complete ultrafilter principle. The result does not support a claim of new large-cardinal strength. It also strengthens the earlier correction: degree zero can already express large-cardinal strength once the semantic class and arity bounds are unrestricted at the relevant scale. Positive residual depth is not a necessary marker of foundational novelty.

## Earlier release record

The original v0.3.0 failure record is preserved verbatim in provenance/v0.3.0_documents/DEVELOPMENT_FAILURES.md. Its implementation failures and finite-support mathematical corrections remain part of the project history.
