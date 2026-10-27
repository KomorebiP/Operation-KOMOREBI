# RRCT v0.51 — Emergent Synergistic Workspace

## Status

- **Version:** `0.51.0.dev1`
- **Frozen result:** `V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_MET`
- **Frozen endpoints:** 21 of 21 passed
- **Strict final-loss-only emergence:** not established
- **Valence or self-preservation model:** absent

## Question

Version 0.50 showed that a persistent jointly writable state was necessary for a four-bit synergistic composition task, but supplied that state explicitly as a 16-slot one-hot workspace.

Version 0.51 asks a stricter question:

> Can the agents learn the representation carried by the persistent channel rather than receive its coordinates?

The system provides an eight-dimensional recurrent message channel, alternating A/B updates, and task supervision. No message coordinate is assigned a semantic meaning and no one-hot workspace enters the runtime.

## Frozen design

Two independently parameterized agents repeatedly update one continuous message:

```text
learned encoding of initial state
        ↓
A1 → B1 → A2 → B2 → A3 → B3
        ↓
both agents decode the final state
```

The underlying task retains exact four-bit synergy:

- Agent A private history: 0 bits about the answer
- Agent B private history: 0 bits about the answer
- Ordered joint history: 4 bits about the answer
- Private-history Bayes accuracy: 1/16
- Joint-history Bayes accuracy: 1

The 4,096 operation sequences were split before training. Twenty percent of complete operation compositions were held out, with all 16 initial states retained for each selected composition.

## Holdout seeds

```text
775479101
759701819
811753828
899346405
```

The implementation, protocol, thresholds, seed receipt, tests, and execution tools were sealed in a 96-file pre-outcome manifest.

Pre-outcome manifest SHA-256:

```text
947bd94043dd3bb893b7826b6f9aae94407c31febb1ee0f6fb67ec1144ede72b
```

## Principal results

| Measure | Frozen mean |
|---|---:|
| Curriculum accuracy on unseen compositions | **1.000000** |
| Terminal-only accuracy, same architecture and budget | **0.199166** |
| Linear final-state decoding from learned message | **0.987466** |
| Causal message-transplant accuracy | **1.000000** |
| Message dimensions | 8 |
| Effective rank at 99.9% variance | 8 on every seed |

Every curriculum-trained seed achieved 100% accuracy for both agents on the held-out operation compositions.

The terminal-only control ranged from approximately 5.6% to 25.0%. It did not approach the recurrent curriculum solution.

## Matched causal controls

Mean accuracies were near the 6.25% chance rate when the learned recurrent state was disrupted:

| Intervention | Result |
|---|---:|
| Intact message | **1.000000** |
| Reset before each update | approximately chance |
| Reset before each round | **0.062500** |
| Agent A writes only | approximately chance |
| Agent B writes only | approximately chance |
| Shuffle message across episodes after round one | approximately chance |
| Disconnect final message from planners | **0.062500** |

The message is therefore not merely correlated with the answer. Temporal persistence, contributions from both agents, episode-correct content, and planner binding are all necessary under the frozen architecture.

## Causal transplant

Episodes were paired so that their remaining operations after round one were identical but their accumulated round-one states differed.

The target episode's actual learned message was transplanted into the source episode.

Across every frozen seed:

- Agent A followed the transplanted state: **100%**
- Agent B followed the transplanted state: **100%**
- The final joint plan changed: **100%**

This establishes that the learned message is a causal sufficient state for the remaining joint computation.

## Ephemerality

While active, both agents could read and update the learned message.

After the message was erased:

- Agent A answer accuracy: **1/16**
- Agent B answer accuracy: **1/16**
- pair memory retained: false
- workspace message retained: false

The solution therefore exists temporarily in the coupled recurrent computation and is not copied into persistent pair autobiography.

## What emerged

The following was learned rather than prescribed:

- message geometry
- representation of the accumulated state
- how each Agent A operation changes that representation
- how each Agent B operation changes that representation
- how both agents decode it

The learned message is eight-dimensional and linearly exposes the current accumulated state with approximately 98.7% accuracy on unseen compositions.

## What did not emerge

The architecture still supplies:

- a persistent recurrent channel
- the A/B alternation schedule
- the message capacity
- the public initial state
- round-level curriculum targets
- the task ontology

The identical architecture trained only from the final target did not reliably discover the recurrent algorithm under the frozen 1,000-step budget.

Therefore, this result does **not** establish fully spontaneous workspace emergence from a terminal objective alone.

The correct description is:

> **Curriculum-supported emergence of a compact shared message representation inside an engineered recurrent communication scaffold.**

## Why this matters

Version 0.50 established necessity of a supplied workspace state.

Version 0.51 establishes that the state representation itself need not be supplied. Optimization can organize an anonymous continuous channel into a causal, bilaterally writable, temporally persistent, planner-bound shared state.

That is a genuine reduction in scaffolding, even though the scaffold has not disappeared.

## Validation

- Focused v0.51 tests: **9 passed**
- v0.47, v0.48, v0.51 fast causal line: **29 passed**
- v0.49 focused tests: **7 passed**
- v0.50 focused tests: **8 passed**
- v0.42–v0.46 successor line: **44 passed, 4 immutable predecessor-seal checks deselected**
- v0.36–v0.40 runtime line: **64 passed, 1 historical freeze-builder check deselected**
- Python syntax validation: **215 files passed**
- Source seal after execution: **96 files verified unchanged**

Two broad combined commands exceeded their execution windows without producing pytest summaries. They are recorded as incomplete and are not represented as passes or failures.

## Execution anomaly

The sealed parent holdout runner stalled after its first curriculum child process and exceeded ten minutes. No scientific result was produced by that incomplete invocation.

The same sealed training helper was then invoked once per model in isolated Python processes. All eight models were completed, and the frozen analysis functions aggregated their results. No scientific source, threshold, seed, or endpoint was changed.

## Claim boundary

The result establishes a learned functional shared state in a bounded synthetic neural architecture.

It does not establish:

- natural-language shared workspace emergence
- pretrained-model J-space alignment
- architecture-free emergence
- final-loss-only emergence
- persistent composite identity
- subjective awareness
- shared consciousness
- sentience, valence, suffering, desire, or moral status

## Next gap

The next strict target is to make the recurrence curriculum unnecessary.

A stronger experiment would use:

- terminal-only training
- variable sequence lengths
- self-generated intermediate consistency objectives rather than supplied round labels
- learned turn timing or asynchronous communication
- an unknown message dimension
- unseen operator families rather than only unseen compositions
- pressure to form a workspace only when synergy requires one

The decisive result would be a compact causal message state that appears from the terminal joint objective and generalizes beyond the trained operator family.
