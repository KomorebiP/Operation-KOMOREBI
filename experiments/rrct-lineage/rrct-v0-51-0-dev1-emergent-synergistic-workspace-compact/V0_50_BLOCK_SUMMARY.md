# RRCT v0.50 — Synergistic Ephemeral Workspace

## Result

**Scientific status:** `V050_FROZEN_ENDPOINTS_MET`  
**Frozen endpoints:** **23 of 23 passed**

Version 0.50 tests whether two differently trained transformer agents can solve a temporally extended problem only through persistent jointly writable state.

## Architecture

Agent A and Agent B are separately initialized 10,292-parameter transformers. Each is trained exhaustively on a different family of invertible affine updates over a 16-state space. They receive no joint sequence training and no joint end-to-end objective.

During the joint task they alternately read and write one temporary 16-slot state for three rounds. That state is erased after action.

## Exact information structure

The final target has four bits of entropy. Given the initial state:

\[
I(Y;A_{1:3})=0,
\qquad
I(Y;B_{1:3})=0,
\]

but

\[
I(Y;A_{1:3},B_{1:3})=4\text{ bits}.
\]

Thus each complete private history leaves the answer at chance \(1/16\), while the combined history determines it exactly.

## Frozen holdout

Seeds:

```text
476798751
912461818
486597126
559071340
```

Per seed:

- 65,536 complete sequence cases
- 11 matched modes
- two separately trained transformer agents

Across the frozen cohort:

- 262,144 unique sequence cases
- 2,883,584 matched mode evaluations
- eight saved trained models

## Principal measurements

| Condition | Accuracy |
|---|---:|
| Full workspace | **1.000000** |
| Recurrent message workspace | **1.000000** |
| Best genuinely nonpersistent control | **0.171875** |
| Reset, one-way, planner-cut, or last-message controls | **0.062500** |
| Full external log oracle | **1.000000** |

A causal mid-sequence workspace patch redirected both agents and the final plan with 100% accuracy. Unrelated private routines remained at 100%.

After workspace dissolution, both agents returned to chance on the joint answer. No pair autobiography remained.

## Strongest justified conclusion

> Under the frozen synthetic architecture and resource rules, solving the online composition requires a persistent state that both agents can successively update. The state can be centrally stored or recurrently passed; physical centralization is not essential.

## Critical qualification

A sufficiently expressive communication protocol can emulate a workspace by carrying persistent state. The v0.50 result therefore does not establish that “messages cannot solve the problem.” It establishes that any successful online mechanism must preserve and integrate the joint state somewhere.

The benchmark deliberately engineers this necessity. It is not evidence that a shared workspace spontaneously emerged in open-ended agents, nor evidence of shared consciousness.

## Next gap

The next stronger test should remove the explicit 16-slot state and ask whether separately trained agents **spontaneously invent** a compact recurrent joint state under a strict information bottleneck. The candidate latent should then be discovered post hoc and subjected to the same reset, one-way, planner-binding, provenance, and dissolution tests.
