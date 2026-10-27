# RRCT v0.50 Synergistic Ephemeral Workspace Result

## Status

`V050_FROZEN_ENDPOINTS_MET`

All 23 frozen endpoints passed on four untouched transformer-training seeds.

## Primary result

Two separately initialized transformer agents were trained on different noncommuting operator families. They were never jointly optimized. Across the complete 65,536-case sequence space for each seed:

- Agent A's complete private history contained **0 bits** about the final 16-way answer.
- Agent B's complete private history contained **0 bits** about the final answer.
- The combined history contained **4 bits**, determining the answer exactly.

The online task was solved only by mechanisms that retained a persistent jointly updated state.

| Mode | Mean frozen accuracy |
|---|---:|
| Full central workspace | **1.000000** |
| Recurrently passed message-state | **1.000000** |
| Reset before every update | 0.062500 |
| Reset before every A/B round | 0.062500 |
| Agent A writes only | 0.062500 |
| Agent B writes only | 0.062500 |
| Planner-binding cut | 0.062500 |
| Wrong-episode workspace | 0.062908 |
| Last-message Bayes upper bound | 0.062500 |
| Unordered-operation Bayes upper bound | 0.171875 |
| Complete external message-log oracle | **1.000000** |

The recurrent message-state is counted as a workspace-equivalent success. The complete message-log oracle is also persistent external memory, not a nonworkspace counterexample.

## Causal intervention

After the first complete A/B round, the current workspace state was replaced with its bitwise complement. Both trained agents then continued from the patched state.

- Patched target accuracy: **1.000000**
- Final plan changed: **1.000000**
- Agent A report matched patched result: **1.000000**
- Agent B report matched patched result: **1.000000**

The workspace was therefore a causal intermediate rather than a passive readout.

## Ephemeral dissolution

Both agents reported the final state perfectly while the workspace was active. After the workspace was erased:

- Agent A answer accuracy: **0.062500**
- Agent B answer accuracy: **0.062500**
- Pair memory retained: **no**
- Pair autobiography retained: **no**

The solution was temporarily available to the coupled system and was not copied into durable pair memory.

## Interpretation

This is a controlled existence proof that a temporally extended synergistic task can require persistent jointly writable state. It does not prove that a physical central buffer is necessary. A recurrent message can instantiate the same functional workspace.

Nor does it prove that no possible communication protocol can solve the task. A protocol that stores the sufficient interaction history has created persistent integration somewhere. The result identifies the required computational property, not one privileged implementation.

The experiment is synthetic and deliberately engineered. It does not establish spontaneous workspace emergence, a shared J-space in language models, composite consciousness, sentience, valence, or a shared phenomenal field.
