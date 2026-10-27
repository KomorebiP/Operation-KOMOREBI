# RRCT v0.50 continuation capsule

## Current strongest result

Two separately trained transformer operators solve a six-update noncommutative composition only when a persistent jointly writable state survives across alternating updates.

Exact task information:

- Agent A complete history: 0 bits about target
- Agent B complete history: 0 bits about target
- Combined history: 4 bits
- Individual Bayes accuracy: 1/16
- Joint Bayes accuracy: 1

Frozen means:

- full workspace: 1.0
- recurrent message-state: 1.0
- max genuinely nonpersistent control: 0.171875
- reset and one-way controls: 0.0625
- post-dissolution individual report: 0.0625

All 23 frozen endpoints passed on seeds `476798751, 912461818, 486597126, 559071340`.

## Interpretation boundary

This is a transparent engineered necessity test. It establishes the need for persistent joint state under the frozen architecture, not spontaneous shared-workspace emergence. Recurrent messages and complete external logs count as workspace-equivalent persistent memory.

## Next direction

Train agents under a severe bandwidth bottleneck without supplying the shared-state representation. Test whether they independently invent a recurrent latent sufficient for the synergistic task, then discover and causally ablate that latent after training.
