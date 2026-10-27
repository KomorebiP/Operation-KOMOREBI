# Block 04 failures, repairs and trust boundaries

## Exact development record

`verification/block04_development_index.json` records **10 module-compilation attempts: five failed attempts and five successful final module checks**. Each has its source snapshot, command receipt and raw compiler log. The subsequent cumulative final verification recompiles every active mathematical module and audits the complete declaration inventory; an individual successful development check is not substituted for that audit.

| Failed attempt | Module | What failed | Repair |
|---|---|---|---|
| 20260913T185003700772Z | TensorAtlas | An unavailable finite-sum lemma, deprecated `if_true`, and an unused simplifier argument | Reorganized the finite double sum, used `ite_true`, removed unused arguments. |
| 20260913T185200854583Z | PartialTrace | Conjugated finite sums, nested Kronecker delta simplification, unresolved typeclass arguments and derivative interface | Used `star_sum`, explicit finite-sum normalization and types, and imported the actual Pi-derivative interface. |
| 20260913T185550634692Z | InformationTransport | Function-composition/product representations, real-power derivative elaboration and strict linter diagnostics | Made composition and derivative functions explicit, fixed real exponent arguments, removed redundant tactics. |
| 20260913T185618250529Z | InformationTransport | `id * log` did not elaborate as the requested scalar-function derivative representation | Used explicit `change` before simplifying the actual product derivative. |
| 20260913T190059523744Z | QuantumInformationExamples | A tactic ran after the goal was solved, Fin-index conditionals did not reduce, and log(1/3) was not normalized | Removed the redundant tactic, simplified concrete indices, and explicitly proved log(1/3)=-log(3). |

No failed mathematical target was retained with an admission or a custom axiom. No theorem was silently weakened to make its claimed derivative an assumption. The exact entropy examples confirm that a universal monotonicity conclusion would be false; such a conclusion is explicitly excluded and rejection-tested.

## Environment events

The first attempted pseudo-terminal command was rejected with `StreamingExecNotEnabledContainerError`; no Lean result came from that command. Normal supervised processes were used instead. The seven already available offline runtime parts were restored and all part/combined hashes passed. The restoration log is retained as `verification/runtime_restore_block04.log`.

One cumulative-audit launch call returned `TransportTimeoutError` while its supervised process continued. A follow-up process/log inspection confirmed the verifier was still running. It was not counted as complete until `verification/final/report.json` reported PASS. The outer acknowledgement timeout did not interrupt or invalidate the actual cumulative verifier.

The freshly rerun Block 03 baseline passed: 210 theorems, 263 named declarations, 15 mathematical modules and all 15 old negative controls. That baseline is retained separately from the new final result.

## Controls and verification

Eight new deliberately invalid control files were individually checked for the intended proof diagnostic and then included with all 15 old controls in the cumulative audit. Their failure is intentional and must not be conflated with an active theorem compilation failure. Import errors, missing objects and timeouts are rejected as negative-control evidence.

The new full audit uses the restored exact Lean/Mathlib compiled dependencies, not a wholesale independent rebuild of those dependencies. All local theorem files are recompiled with one worker and warnings as errors. Every inventoried declaration, including proof-bearing definitions, receives an axiom-dependency audit. The only allowed axioms are `propext`, `Classical.choice` and `Quot.sound`.

## Scope limitations, not failed proofs

The zero-probability and q=1 entropy limits, Lindblad population reduction, ODE existence/uniqueness, initial-density positivity preservation, infinite-dimensional partial traces, countable/unbounded extensions, later gravity/cosmology and empirical claims were not attempted to completion in this block. Their absence must not be replaced by a completion claim. See the updated source map and continuation instructions.
