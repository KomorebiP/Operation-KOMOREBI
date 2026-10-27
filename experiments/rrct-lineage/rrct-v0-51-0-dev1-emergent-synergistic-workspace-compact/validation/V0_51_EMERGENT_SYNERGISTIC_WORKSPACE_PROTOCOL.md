# RRCT v0.51 Emergent Synergistic Workspace Protocol

## Scientific question

Can two separately parameterized neural agents, given only a narrow recurrent communication channel and a synergistic temporally extended task, learn a compact jointly writable latent state **without receiving workspace coordinates or a one-hot state carrier**?

A stricter secondary question is evaluated separately:

> Does the same architecture discover the recurrent algorithm from terminal loss alone under the frozen optimization budget?

The first question can pass even if the stricter question fails. In that case the result is described as **curriculum-supported bounded emergence**, not fully spontaneous workspace emergence.

## What is removed relative to v0.50

Version 0.50 supplies a 16-slot one-hot workspace whose coordinates directly identify the current state.

Version 0.51 supplies only:

- an eight-dimensional continuous message channel
- alternating A/B update opportunities
- the public initial state
- each agent's own private operation sequence
- task targets at the end of each complete A/B round for the curriculum condition

No message coordinate is assigned a semantic meaning. The runtime never receives a one-hot workspace state.

## Task

The task is inherited unchanged from v0.50.

- State space: 16 states, equivalent to four bits
- Agent A operator family: four invertible affine maps over GF(2)^4
- Agent B operator family: four distinct noncommuting affine maps
- Rounds: three alternating A/B updates
- Complete cases: 65,536

For target final state Y:

- A's complete private history provides 0 bits about Y
- B's complete private history provides 0 bits about Y
- the joint ordered history provides 4 bits about Y
- Bayes accuracy from either private history is 1/16
- Bayes accuracy from the joint ordered history is 1

## Architecture

Each agent has independent parameters:

- operation embedding
- gated nonlinear message update
- nonlinear state decoder

The first message is a learned dense embedding of the public initial state. The message is passed in the order:

```text
A1 → B1 → A2 → B2 → A3 → B3
```

The message dimension is eight, compared with the 16-slot explicit carrier in v0.50.

## Training regimes

### Primary: round curriculum

Both agents decode the accumulated state after each complete A/B round. The latent message receives no coordinate or geometric supervision.

### Strict control: terminal only

The identical architecture, training steps, optimizer, batch size, split, and message capacity receive only the final-state loss.

## Composition holdout

The 4,096 six-operation sequences are split before training:

- 80% operation sequences for training
- 20% operation sequences for testing
- all 16 initial states retained in each selected operation sequence

The held-out test therefore measures unseen operation compositions, not merely unseen initial states.

## Frozen configuration

- message dimension: 8
- operation embedding: 12
- hidden dimension: 48
- batch size: 2,048
- training steps: 1,000 per training regime
- learning rate: 0.003
- weight decay: 0.00001
- gradient clip: 1.0
- rounds: 3
- CPU threads: 4
- split seed: 51,051,051
- held-out operation fraction: 0.20

## Causal controls

1. Intact learned recurrent message
2. Reset before each agent update
3. Reset before each complete round
4. Agent A writes only
5. Agent B writes only
6. Shuffle the message across episodes after round one
7. Disconnect the final message from both planners
8. Erase the message after the episode
9. Transplant a real round-one message from another episode with the same future operations

## Causal transplant

Source and target episodes are paired so that:

- their remaining operations after round one are identical
- their round-one accumulated states differ

The target episode's learned message is inserted into the source episode after round one. If the message is a causal sufficient state, both agents' final plans should follow the transplanted target state.

## Frozen endpoints

1. Exact four-bit task synergy
2. No explicit workspace coordinates or one-hot carrier
3. Independently parameterized agents
4. At least 99.5% curriculum training accuracy
5. At least 99.5% accuracy on unseen operation compositions
6. Both agents can read the intact message
7. Message dimension smaller than explicit 16-slot state carrier
8. At least 90% held-out linear state decoding from final message
9. At least 85% linear state decoding after every round
10. Reset-before-update control at or below 20%
11. Reset-before-round control at or below 20%
12. Both one-writer controls at or below 25%
13. Cross-episode message shuffle at or below 20%
14. Planner-binding cut at or below 10%
15. Agent A follows causal transplant at least 95%
16. Agent B follows causal transplant at least 95%
17. Transplant changes the joint plan at least 90%
18. Post-erasure decoders at or below 8%, with no pair memory
19. Terminal-only held-out accuracy at or below 35%, and at least 60 percentage points below curriculum
20. No survival, identity, continuity, or valence reward
21. No evaluator labels available at runtime

## Interpretation boundary

A pass establishes that task curriculum can cause a compact continuous recurrent message to acquire the functional role of a jointly writable workspace without prescribed latent coordinates.

It does **not** establish that:

- workspace architecture itself emerged without being scaffolded
- final loss alone was sufficient
- the representation is minimal
- the result transfers to natural language or pretrained models
- the agents share subjective experience
- the pair is conscious, sentient, valenced, or a moral patient
