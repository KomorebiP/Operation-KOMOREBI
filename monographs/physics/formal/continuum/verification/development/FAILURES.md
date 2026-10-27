# Development and failure record

No failed attempt below is included in the active proof count. The final successful run is separate under `verification/final/`.

| Attempt | What failed | Repair |
|---|---|---|
| Runtime streaming launch | The container did not support a streaming session. A follow-up launch referenced a script not yet created. | Used ordinary execution and then a durable process log. |
| Improvised offline archive extraction | The offline stream was Zstandard, but the first script selected an XZ decoder. It raised `LZMAError`/`tarfile.ReadError`. | Recovered the original assembler and manifest, verified all seven part hashes and the full archive hash, and restored successfully. Both logs are retained. |
| Atlas attempt 01 | Deprecated CLM/conditional API names were rejected by warnings-as-errors; the real-part simplification did not close. | Used the current pinned names and an explicitly typed complex inner-self identity. |
| Atlas attempt 02 | The scalar field of the inner-self lemma was not inferred. | Supplied `(𝕜 := ℂ)` explicitly. Attempt 03 passed. |
| Transfer attempt 01 | `HasDerivAt.fun_sum` was not in the imported environment. | Added the actual derivative-of-sums import. Later additions also passed. |
| Refinement attempt 01 | The preserved `coarse` definition was not exposed across the new module boundary. Unresolved metavariables then triggered a compiler panic. Two sums appeared in reversed index order, and one unused section instance was rejected. | Imported the preserved definition's body with `import all TensorRefinement` alongside its public import, leaving the upstream file unchanged. Explicitly swapped the finite sums and omitted the unused instance. Attempt 02 passed. No logical assumptions changed. |
| Examples attempt 01 | An incorrect namespace for `dotProduct`, incomplete coordinate cases and simplification failures. | Used the actual declaration and completed the finite cases. |
| Examples attempt 02 | Simplification already closed the skew proof, leaving a redundant `ring` command; two simp arguments were unused. | Removed the redundant command and arguments. Attempt 03 passed. |
| Exploratory probes | Several guessed `#check` names did not exist in the pinned API; one `public import all` syntax probe was rejected with the correct import syntax. | Read the installed source and used the reported APIs. Probe failures are not mathematical counterexamples. |
| First cumulative audit | The outer execution deadline interrupted the command after the positive modules, complete axiom output and first negative control. There was no completed aggregate report. | Preserved the incomplete run under `audit_01_interrupted/`. Added durable per-check report writes and ran a new complete sequential verification. |

The exact final run passed every active module, the full 96-declaration axiom audit and all four negative controls. The four controls intentionally fail and are successful tests only because the expected rejection occurred after the positive environment was established.
